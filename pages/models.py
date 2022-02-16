from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
import uuid
import decimal
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import now

class MyShopConf(models.Model):
    rev_num = models.IntegerField(default=0, null=False)
    comment_num = models.IntegerField(default=0, null=False)
    pics_num = models.IntegerField(default=100, null=False)

class Sorted_Items(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('name')

class Author(models.Model):
    objects = Sorted_Items()
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(blank=True, null=False, default='')

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class Category(models.Model):
    objects = Sorted_Items()
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name

class Product(models.Model):
    objects = Sorted_Items()
    name = models.CharField(max_length=100, null=False, blank=False)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    objects = Sorted_Items()
    name = models.CharField(max_length=200, null=False, blank=False)
    url = models.CharField(max_length=200, null=False, default='', blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    default_product_id = 1
    link = models.UUIDField(
        unique=True,
        primary_key=False,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(max_length=100, null=False, default='No title')
    original_title = models.CharField(max_length=100, default='n/d')
    author = models.ManyToManyField(Author)
    description = models.TextField(blank=True, null=False, default='Ta książka nie ma jeszcze opisu.')
    availability = models.BooleanField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=decimal.Decimal(0000.00))
    promotional_price = models.DecimalField(max_digits=6, decimal_places=2, default=decimal.Decimal(0000.00))
    category = models.ManyToManyField(Category)
    pages = models.IntegerField(null=True)
    cover_type = models.CharField(max_length=20, null=False, default='BD', choices=[
                                                            ('m', 'miękka okładka'),
                                                            ('t', 'twarda okładka'),
                                                            ('b', 'BD')
                                                         ],)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, null=True)
    language = models.CharField(max_length=20, null=False, default='polski', choices=[
                                                            ('pl', 'polski'),
                                                            ('en', 'angielski'),
                                                            ('de', 'niemiecki'),
                                                            ('fr', 'francuski'),
                                                         ],)
    isbn = models.BigIntegerField(default=0)
    publication_date = models.DateField(null=True)
    adding_to_shop_date = models.DateField(default=now)
    cover_img = models.ImageField(default='covers/sample.jpg')
    book_page_img = models.CharField(max_length=1000, blank=True, default='')
    menu_img = models.CharField(max_length=1000, blank=True, default='')
    size = models.CharField(max_length=15, null=True, default='30 x 213 x148')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, default=default_product_id)
    number_of_items = models.IntegerField(default=0)
    number_of_sold = models.IntegerField(default=0)
    rate = models.IntegerField(default=0)
    num_of_likes = models.IntegerField(default=0)
    num_of_rates = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
        ]
    def serialize(self):
        txt = ''
        for a in self.author.all():
            txt += a.name + ', '
        txt = txt.rstrip(', ')
        data_to_back = {'id': self.id, 'link': str(self.link), 'title': self.title, 'authors': txt, 'price': str(self.price), 'promotional_price': str(self.promotional_price),
                        'menu_img': self.menu_img}
        return data_to_back

    def get_authors_to_query_or(self):
        authors = list(self.author.all())
        query = Q(author=authors.pop())
        while authors:
            query = query | Q(author=authors.pop())
        return query

    def get_genres_to_query_or(self):
        genres = list(self.category.all())
        query = Q(category=genres.pop())
        while genres:
            query = query | Q(category=genres.pop())
        return query

    def is_long_name(self):
        if len(self.title) > 24:
            return 1
        else:
            return 0


    def display_title(self):
        if not len(self.title) > 24:
            return self.title
        else:
            return self.title

    def display_authors(self):
        authors = self.author.all()
        if len(authors) != 1:
            return str(authors[0]) + ' i inni'
        else:
            return str(authors.get())

    def is_in_sold(self):
        if self.number_of_items > 0:
            return True
        else:
            return False

    def is_in_promotion(self):
        if self.promotional_price:
            self.percentage = self.calculate_percentage()
            return True
        else:
            return False

    def list_of_authors(self):
        if len(self.authors) > 1:
            text = '<li class="list-group-item">Autorzy: '
            for a in self.authors:
                text += a + ', '
            return text[:-2]
        else:
            text = '<li class="list-group-item">Autor: ' + self.authors[0]
            return text

    def list_of_genres(self):
        if self.category.count() > 1:
            text = '<li class="list-group-item">Gatunek: '
            for g in self.category.all():
                text += g.name + ', '
            return text[:-2]
        else:
            text = '<li class="list-group-item">Gatunek: ' + self.category.all()[0].name
            return text

    def get_absolute_url(self):
        return '/books/' + str(self.link)

    def return_str_id(self):
        return str(self.id)

    def calculate_percentage(self):
        if self.promotional_price <= 0:
            raise ValueError("Podana promocyjna cena jest nieodpowiednia.")
        else:
            diference = self.price - self.promotional_price
            return round(diference / (self.price / 100))


    def __str__(self):
        return self.title

def default_data_to_likes():
    return {'number': 0, 'users_id': []}

class Book_Review(models.Model):
    html1 = """<p id="%s"><span class="font-weight-bold">Data:</span> %s</p>\n<p><span class="font-weight-bold">Autor:</span>  %s %s</p>\n<h5 class="title">%s</h5>\n<p class"subject">%s</p>\n<p class='pb-6'><small>%s uznało tę recenzję za przydatną.</small>&nbsp;<small><a href="#%s">Link</a></small><hr></p>"""
    html2 = """<p id="%s"><span class="font-weight-bold">Data:</span> %s</p>\n<p><span class="font-weight-bold">Autor:</span>  %s %s</p>\n<h5 class="title">%s</h5>\n<p class"subject">%s</p>\n<p class="index d-flex" index="%s"><a href='' id='report'>Zgłoś</a>&nbsp;&nbsp;<a href='' id='like_review' isliked="0">Polub</a><i class="far fa-thumbs-up pt-1" style="color: Dodgerblue;"></i><small class="ml-auto"></p>\n<p class='pb-6'>%s uznało tę recenzję za przydatną.</small>&nbsp;<small><a href="#%s">Link</a></small><hr></p>"""
    html3 = """<p id="%s"><span class="font-weight-bold">Data:</span> %s</p>\n<p><span class="font-weight-bold">Autor:</span>  %s %s</p>\n<h5 class="title">%s</h5>\n<p class"subject">%s</p>\n<p class="index d-flex" index="%s"><a href='' id='report'>Zgłoś</a>&nbsp;&nbsp;<a href="" id='like_review' isliked="1">Lubisz</a><i class="fas fa-thumbs-up pt-1" style="color: Dodgerblue";></i><small class="ml-auto"></p>\n<p class='pb-6'><span class=rev_num_likes>%s</span> uznało tę recenzję za przydatną.&nbsp;<a href="#%s">Link</a></small><hr></p>"""
    html4 = """<p id="%s"><span class="font-weight-bold">Data:</span> %s</p>\n<p><span class="font-weight-bold">Autor:</span>  %s %s</p>\n<h5 class="title">%s</h5>\n<p class"subject">%s</p>\n<p class="index d-flex" index="%s"><a href="" id="remove">Usuń</a>&nbsp;&nbsp;<a href="" id="edit">Edytuj</a></p>\n<p class='pb-6'><small>%s uznało tę recenzję za przydatną.</small>&nbsp;<small><a href="#%s">Link</a></small><hr></p>"""

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output = self.get_html1

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'book'], name='unique_review')]
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, editable=False)
    date = models.DateTimeField(auto_now=False, auto_now_add=True, null=False, editable=True)
    subject = models.TextField(max_length=30, blank=True, null=False, default='')
    text = models.TextField(max_length=500, null=False)
    likes = models.JSONField(default=list, null=False)
    number = models.IntegerField(null=True)

    def num_of_likes(self):
        return len(self.likes)

    def get_html1(self):
        '''
        Output dla niezalogowanego użytkownika.
        :return: str
        '''
        return self.html1 % (self.number, self.date.date(), self.user.first_name, self.user.last_name, self.subject, self.text, self.num_of_likes(), self.number)

    def get_html2(self):
        '''
        Recenzja której nie polubiłeś.
        :return: str
        '''
        return self.html2 % (self.number, self.date.date(), self.user.first_name, self.user.last_name, self.subject, self.text, self.index, self.num_of_likes(), self.number)

    def get_html3(self):
        '''
        Recenzja którą polubiłeś.
        :return: str
        '''
        return self.html3 % (self.number, self.date.date(), self.user.first_name, self.user.last_name, self.subject, self.text, self.index, self.num_of_likes(), self.number)

    def get_html4(self):
        '''
        Twoja recenzja.
        :return: str
        '''
        return self.html4 % (self.number, self.date.date(), self.user.first_name, self.user.last_name, self.subject, self.text, self.index, len(self.likes), self.number)

class Book_Rate(models.Model):
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'book'], name='unique_vote')]
    class Suit(models.IntegerChoices):
        one   = 1
        two   = 2
        three = 3
        four  = 4
        five  = 5
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, editable=False)
    rate = models.IntegerField(choices=Suit.choices)
    rev = models.OneToOneField(Book_Review, null=True, on_delete=models.SET_NULL)

    def get_html1(self):
        return """<p><br><span class="font-weight-bold">Ocenił na: </span><span class="fa fa-star checked"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></p>"""

    def get_html2(self):
        return """<p><br><span class="font-weight-bold">Ocenił na: </span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></p>"""

    def get_html3(self):
        return """<p><br><span class="font-weight-bold">Ocenił na: </span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></p>"""

    def get_html4(self):
        return """<p><br><span class="font-weight-bold">Ocenił na: </span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span><span class="fa fa-star"></span></p>"""

    def get_html5(self):
        return """<p><br><span class="font-weight-bold">Ocenił na: </span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span><span class="fa fa-star checked"></span></p>"""

    def output(self):
        if self.rate == 1:
            return self.get_html1()
        elif self.rate == 2:
            return self.get_html2()
        elif self.rate == 3:
            return self.get_html3()
        elif self.rate == 4:
            return self.get_html4()
        elif self.rate == 5:
            return self.get_html5()

admin.site.register([Author, Category, Publisher, Product,])