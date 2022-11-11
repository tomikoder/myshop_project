from django.views.generic import DetailView, ListView, TemplateView
from users.forms import CustomSignupForm as signup_form
from users.forms import CustomLoginForm as  login_form
from django.http import JsonResponse
from .models import Book, Product, Book_Rate, Book_Review
from allauth.account.views import SignupView, LoginView
from .forms import CommentForm as comment_form, NumberOfItems as number_of_items
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.utils.decorators import method_decorator
from django.core import serializers
from .custom_signals import rate_is_updated, book_is_liked, book_is_unliked, book_review_is_created, book_review_is_saved
import json
from django.db import connection
from .models import Category

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    data_to_back = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return data_to_back



others_categories = ['gry planszowe', 'zabawki', 'zakładki']
music_categories =  ['elektroniczna', 'jazz', 'klasyczna', 'metal', 'rap & hip-hop', 'regge', 'rock']
movies_categories = ['animacja', 'anime', 'biografia', 'dla dzieci', 'dokumentalne', 'erotyka', 'fantasy', 'historyczne', 'horror', 'klasyka',
                     'komedie', 'kryminał', 'przygodowe', 'romans', 'science fiction', 'sensacja', 'seriale', 'thriller']
games_categories =  ['Nintendo', 'PC', 'Playstation', 'Xbox']

class Custom_TemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = signup_form
        context['login_form'] = login_form
        context['num_of_items_form'] = number_of_items
        context['book_categories'] = Product.objects.get(name='books').categories.all()
        context['others_categories'] = others_categories
        context['music_categories'] = music_categories
        context['movies_categories'] = movies_categories
        context['games_categories'] = games_categories
        user = self.request.user
        #Uwstawienia koszyka zakupów dla zalogowanego użytkownika i nie zalagowanego.
        if user.is_authenticated:
            context['user_additional_data'] = user.additionaldata
            c = 0
            for i in context['user_additional_data'].order_list:
                c+= i['amount']
            context['num_of_items_in_shca'] = c
        else:
            if not 'order_list' in self.request.session:  #Używam ciasteczek by przetrrzymywać dane o koszyku.
                self.request.session['order_list'] = []
                context['num_of_items_in_shca'] = 0
            else:
                c = 0
                for i in self.request.session['order_list']:
                    c+= i['amount']
                context['num_of_items_in_shca'] = c
        return context

class Custom_DetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = signup_form
        context['login_form'] = login_form
        context['num_of_items_form'] = number_of_items
        context['book_categories'] = Product.objects.get(name='books').categories.all()
        context['others_categories'] = others_categories
        context['music_categories'] = music_categories
        context['movies_categories'] = movies_categories
        context['games_categories'] = games_categories
        return context

class Custom_ListView(ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = signup_form
        context['login_form'] = login_form
        context['num_of_items_form'] = number_of_items
        context['music_categories'] = music_categories
        context['movies_categories'] = movies_categories
        context['book_categories'] = Product.objects.get(name='books').categories.all()
        context['others_categories'] = others_categories
        context['games_categories'] = games_categories

        user = self.request.user
        if user.is_authenticated:
            context['user_additional_data'] = user.additionaldata
            c = 0
            for i in context['user_additional_data'].order_list:
                c+= i['amount']
            context['num_of_items_in_shca'] = c
        else:
            if not 'order_list' in self.request.session:
                self.request.session['order_list'] = []
                context['num_of_items_in_shca'] = 0
            else:
                c = 0
                for i in self.request.session['order_list']:
                    c+= i['amount']
                context['num_of_items_in_shca'] = c
        return context


@method_decorator(ensure_csrf_cookie, name='dispatch')
class HomePageView(Custom_TemplateView):
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Pobieram ksiażki do wyświetlenia na głównej.
        with connection.cursor() as cursor:
            cursor.execute('''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                            FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                                 INNER JOIN pages_author AS a ON a.id = ba.author_id
                                            WHERE b.availability = true
                                            GROUP BY b.id
                                            ORDER BY b.publication_date DESC
                                            LIMIT 8)
                                            SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() - 1 AS index
                                            FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                              
                           ''')
            context['new']  = dictfetchall(cursor)
        with connection.cursor() as cursor:
            cursor.execute('''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                            FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                                 INNER JOIN pages_author AS a ON a.id = ba.author_id
                                            WHERE b.availability = true
                                            GROUP BY b.id
                                            ORDER BY b.number_of_sold DESC
                                            LIMIT 8)
                                            SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() + 7 AS index
                                            FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                                                                                               
                           ''')
            context['best']  = dictfetchall(cursor)
        with connection.cursor() as cursor:
            cursor.execute('''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                            FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                                 INNER JOIN pages_author AS a ON a.id = ba.author_id
                                            WHERE b.availability = true AND b.promotional_price IS NOT NULL 
                                            GROUP BY b.id
                                            LIMIT 8)
                                            SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() +  15 AS index
                                            FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                                                                                               
                           ''')
            context['prom']  = dictfetchall(cursor)
        return context

class RegulaminPageView(Custom_TemplateView):
    template_name = 'regulamin.html'

@method_decorator(ensure_csrf_cookie, name='dispatch')
class BookDetailPageView(Custom_DetailView):
    template_name = 'detail.html'
    model = Book
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            your_rate =  Book_Rate.objects.filter(book=self.object, user=user) #Ocena produktu prez użytkownika
            if your_rate:
                context['your_rate'] = your_rate.get()
        else:
            context['your_rate'] = None
        context['num_of_votes'] = self.object.num_of_rates
        #Sprowadzam wszystkie recenzje
        context['book_reviews'] = list(Book_Review.objects.raw('''SELECT br.*, bra.rate, ROW_NUMBER() OVER() - 1 AS index, u.first_name, u.last_name 
                                                                  FROM pages_book_review AS br INNER JOIN pages_book_rate AS bra ON br.id = bra.rev_id
                                                                                               INNER JOIN users_customuser AS u ON br.user_id = u.id  
                                                                  WHERE br.book_id = %s
                                                                  ORDER BY br.date DESC
                                                               ''', [self.object.id]))
        #Instrukcja SQL która sprowadza pozostałe książki autora do wyświetlenia na pasku. Jeżeli książek jest za mało, sprowadza inne książki z tych samych gatunków jak
        #wyświetlana książka
        with connection.cursor() as cursor:
            cursor.execute('''SELECT STRING_AGG(CAST(ba.author_id AS VARCHAR), ', ')
                              FROM pages_book_author AS ba
                              WHERE ba.book_id = %s
                              GROUP BY book_id
                           ''', [self.object.pk])
            sub_set = '(' + cursor.cursor.fetchone()[0] + ')'
            cursor.execute(('''WITH book AS (SELECT b.id, b.title, ARRAY_AGG (a.name) AS authors, b.price, b.promotional_price, b.product_id, b.link, b.menu_img, b.rate
                                             FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id  
                                                                  INNER JOIN pages_author AS a ON a.id = ba.author_id
                                             WHERE b.id != %s AND ba.author_id IN %s 
                                             GROUP BY b.id
                                             LIMIT 15) 
                                             SELECT b2.id, b2.title, b2.authors, CAST(b2.price AS VARCHAR), CAST(b2.promotional_price AS VARCHAR), (LENGTH(b2.title) > 24) AS is_long,
                                             p.name AS product_type, ROW_NUMBER() OVER() -1 AS index, CAST(b2.link AS CHAR(36)), b2.menu_img, b2.rate 
                                             FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                             
                           ''' % (self.object.id, sub_set)))
            other_books = dictfetchall(cursor)
            rows_num = cursor.rowcount
            if rows_num != 15:
                cursor.execute(('''WITH book AS (SELECT b.id, b.title, b.price, b.promotional_price, b.product_id, b.link, ARRAY_AGG(DISTINCT a.name) AS authors, b.menu_img, b.rate 
                                                 FROM pages_book AS b INNER JOIN pages_book_category AS bc ON b.id = bc.book_id
                                                                      INNER JOIN pages_book_author AS ba ON ba.book_id = b.id
                                                                      INNER JOIN pages_author AS a ON a.id = ba.author_id  
                                                 WHERE bc.category_id IN (SELECT category_id 
                                                                          FROM pages_book_category 
                                                                          WHERE book_id = %s)
                                                 AND ba.author_id NOT IN %s
                                                 GROUP BY b.id
                                                 LIMIT %s)
                                                 SELECT b2.id, b2.title, b2.authors, CAST(b2.price AS VARCHAR), CAST(b2.promotional_price AS VARCHAR), (LENGTH(b2.title) > 24) AS is_long,
                                                  p.name AS product_type, ROW_NUMBER() OVER() + %s AS index, CAST(b2.link AS CHAR(36)), b2.menu_img, b2.rate 
                                                 FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                               
                               ''' % (self.object.pk, sub_set, (15 - cursor.rowcount), (rows_num - 1))))
                other_books += dictfetchall(cursor)
            c = 15 - len(other_books)
            while c:
                other_books.append(None)
                c -= 1
        context['other_books'] = other_books
        context['num_of_reviews'] = len(context['book_reviews'])
        if user.is_authenticated:
            context['user_additional_data'] = user.additionaldata
            c = 0
            for i in context['user_additional_data'].order_list:
                c+= i['amount']
            context['num_of_items_in_shca'] = c
            if (self.object.return_str_id() in context['user_additional_data'].liked_books):
                context['you_liked'] = 1
            else:
                context['you_liked'] = 0
            context['is_reviewed'] = False
            for rev in context['book_reviews']:
                if (str(user.id) in rev.likes):
                    rev.output = rev.get_html3
                elif user == rev.user:
                    context['comment_form'] = comment_form({'subject': rev.subject, 'content': rev.text})
                    rev.output = rev.get_html4
                    context['is_reviewed'] = True
                else:
                    rev.output = rev.get_html2
        else:
            if not 'order_list' in self.request.session:
                self.request.session['order_list'] = []
            c = 0
            for i in self.request.session['order_list']:
                c+= i['amount']
            context['num_of_items_in_shca'] = c
        return context

    def get_object(self):
        #Pobieram dane o produkcie ze wszystkimi potrzebnymi danymi.
        indicator = self.kwargs.get("link")
        queryset = list(Book.objects.raw('''WITH book AS (SELECT b.*, ARRAY_AGG(DISTINCT  a.name) AS authors, ARRAY_AGG(DISTINCT  c.name) AS categories  
                                                          FROM pages_book AS b INNER JOIN pages_book_category AS bc ON b.id = bc.book_id
                                                                               INNER JOIN pages_category AS c ON c.id = bc.category_id
                                                                               INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                                               INNER JOIN pages_author AS a ON a.id = ba.author_id
                                                                               INNER JOIN pages_product AS p ON b.product_id = p.id 
                                                          WHERE b.link = %s
                                                          GROUP BY b.id)
                                                          SELECT b2.*, p.name AS product_type
                                                          FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                     
                                         ''', [indicator]))

        return queryset[0]

class New_Books(Custom_ListView):
    '''
    Strona, która wyświetla najnowsze książi.
    '''
    template_name = 'new.html'
    context_object_name = 'books'
    paginate_by = 12
    limit = 84
    sql_script = '''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG(a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                  FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                       INNER JOIN pages_author AS a ON a.id = ba.author_id
                                  WHERE b.availability = true
                                  GROUP BY b.id
                                  ORDER BY b.publication_date DESC
                                  LIMIT %s)
                                  SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() - 1 AS index
                                  FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                              
                  '''

    def get_args_to_query(self):
        return (self.limit,)

    def get_queryset(self):
        with connection.cursor() as cursor:
            cursor.execute(self.sql_script, self.get_args_to_query())
            queryset = dictfetchall(cursor)
            if not (cursor.rowcount % 4) == 0:
                c = cursor.rowcount % 4
                c = 4 - c
                while c:
                    queryset.append(None)
                    c -= 1
        return queryset


class Prom_Books(New_Books):
    template_name = 'prom.html'
    sql_script = '''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                  FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                       INNER JOIN pages_author AS a ON a.id = ba.author_id
                                  WHERE b.availability = true AND b.promotional_price > 0.00                                            
                                  GROUP BY b.id
                                  LIMIT %s)
                                  SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() - 1 AS index
                                  FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                              
                 '''

class Best_Books(New_Books):
    template_name = 'best.html'
    sql_script = '''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                  FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                       INNER JOIN pages_author AS a ON a.id = ba.author_id
                                  WHERE b.availability = true                                          
                                  GROUP BY b.id
                                  ORDER BY b.number_of_sold DESC
                                  LIMIT %s)
                                  SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() - 1 AS index
                                  FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                              
                 '''

class Search_Book(New_Books):
    template_name = 'result_search.html'
    limit = None
    sql_script = '''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                  FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                       INNER JOIN pages_author AS a ON a.id = ba.author_id
                                  WHERE b.title ILIKE %s OR b.title ILIKE %s
                                  GROUP BY b.id
                                  LIMIT %s)
                                  SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() - 1 AS index
                                  FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                              
                 '''

    def get_args_to_query(self):
        return (self.request.GET['query'] + '%', '%' + self.request.GET['query'] + '%', self.limit)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET['query']
        return context

class Search_Book_Two(Search_Book):
    sql_script = '''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                  FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                       INNER JOIN pages_author AS a ON a.id = ba.author_id
                                  WHERE b.compresed_search_data @@ to_tsquery(%s)
                                  GROUP BY b.id
                                  LIMIT %s)
                                  SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() - 1 AS index
                                  FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                              
                 '''

    def get_args_to_query(self):
        query = self.request.GET['query']
        query = query.split()
        query = ' & '.join(query)
        return (query, self.limit)





class Specific_Book_Categories(New_Books):
    template_name = 'category.html'
    limit = None
    sql_script = '''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                  FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                       INNER JOIN pages_author AS a ON a.id = ba.author_id
                                                       INNER JOIN pages_book_category AS bc ON b.id = bc.book_id
                                                       INNER JOIN pages_category AS c ON bc.category_id = c.id  
                                  WHERE c.name in %s                                            
                                  GROUP BY b.id
                                  LIMIT %s)
                                  SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() - 1 AS index
                                  FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                              
                 '''

    def get_args_to_query(self):
        categories = self.request.GET.get('cat')
        categories = tuple(categories.split('  '))
        return (categories, self.limit)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = self.request.GET.get('cat')
        context['categories'] = list(categories.split('  '))
        context['categories_url'] = categories
        return context

class Specific_Book_Category(New_Books):
    template_name = 'category.html'
    limit = None
    sql_script = '''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                                  FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                       INNER JOIN pages_author AS a ON a.id = ba.author_id
                                                       INNER JOIN pages_book_category AS bc ON b.id = bc.book_id
                                                       INNER JOIN pages_category AS c ON bc.category_id = c.id  
                                  WHERE c.name = %s                                            
                                  GROUP BY b.id
                                  LIMIT %s)
                                  SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() - 1 AS index
                                  FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                              
                 '''
    def get_args_to_query(self):
        indicator = self.kwargs.get("category")
        return (indicator, self.limit)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [self.kwargs.get("category")]
        context['categories_url'] = context['categories']
        return context

def vote_on_book(request):
    if request.is_ajax() and request.method == 'POST' and request.user.is_authenticated:
        data = request.POST.dict()
        rate = int(data['stars'])
        first_vote = int(data['first_vote'])
        if first_vote:
            new_rate = Book_Rate.objects.create(user=request.user, book_id=data['book_pk'], rate=rate)
            new_rate.save()
            data_to_update = rate_is_updated.send(sender=vote_on_book, book_pk=data['book_pk'], Book_Rate=Book_Rate, created=True)[0][1]
            return JsonResponse(data={"new_rate": data_to_update, "your_rate": serializers.serialize("json", [new_rate])}, status=201)
        else:
            new_rate = next(serializers.deserialize("json", data['your_rate'])).object
            new_rate.rate = rate
            new_rate.save()
            data_to_update = rate_is_updated.send(sender=vote_on_book, book_pk=data['book_pk'], Book_Rate=Book_Rate, created=False)[0][1]
            return JsonResponse(data={"new_rate": data_to_update}, status=201)
        return JsonResponse(data={"message": "Błąd w przetwarzaniu danych."}, status=500)

def add_like_to_book(request):
    if request.is_ajax() and request.method == 'POST' and request.user.is_authenticated:
        data = request.POST.dict()
        user_additional_data = next(serializers.deserialize("json", data['user_additional_data'])).object
        user_additional_data.liked_books[data['book_pk']] = None
        user_additional_data.save()
        book_is_liked.send(sender=add_like_to_book, book_pk=data['book_pk'])
        return JsonResponse(data={'user_additional_data': serializers.serialize("json", [user_additional_data])}, status=201)
    else:
        return JsonResponse(data={}, status=500)

def remove_like_from_book(request):
    if request.is_ajax() and request.method == 'POST' and request.user.is_authenticated:
        data = request.POST.dict()
        user_additional_data = next(serializers.deserialize("json", data['user_additional_data'])).object
        del user_additional_data.liked_books[data['book_pk']]
        user_additional_data.save()
        book_is_unliked.send(sender=remove_like_from_book, book_pk=data['book_pk'])
        return JsonResponse(data={'user_additional_data':serializers.serialize("json", [user_additional_data])}, status=201)
    else:
        return JsonResponse(data={}, status=500)

def post_book_review(request):
    if request.is_ajax() and request.method == 'POST' and request.user.is_authenticated:
        data = request.POST.dict()
        form = comment_form(data)
        if form.is_valid():
            your_rate = next(serializers.deserialize("json", data['your_rate'])).object
            your_review = Book_Review(user=request.user, book_id=data['book_pk'], subject=form.cleaned_data['subject'], text=form.cleaned_data['content'],
                                      number=book_review_is_created.send(sender=post_book_review)[0][1])
            your_review.save()
            your_review.index = 0
            your_review.rate = your_rate.rate
            your_review.output = your_review.get_html4
            return  JsonResponse({'output': ('<div class="rev">%s%s</div>' % (your_rate.output(), your_review.output())), 'your_rate':
                serializers.serialize("json", [(book_review_is_saved.send(sender=post_book_review, your_review=your_review, your_rate=your_rate)[0][1])]),
                                  'is_reviewed': True, 'your_review': serializers.serialize("json", [your_review])}, status=201)
        else:
            return JsonResponse({}, status=500)
    else:
        return  JsonResponse({}, status=500)

def remove_book_review(request):
    if request.is_ajax() and request.method == 'POST' and request.user.is_authenticated:
        data = request.POST.dict()
        Book_Review.objects.filter(pk=data['your_review_pk']).delete()
        your_rate = next(serializers.deserialize("json", data['your_rate'])).object
        your_rate.rev = None
        your_rate.save()
        return JsonResponse({'your_rate': serializers.serialize('json', [your_rate])}, status=200)
    else:
        return JsonResponse({}, status=500)

def edit_book_review(request):
    if request.is_ajax() and request.method == 'POST' and request.user.is_authenticated:
        data = request.POST.dict()
        your_review = next(serializers.deserialize("json", data['your_review'])).object
        form = comment_form(data)
        if form.is_valid():
            your_review.subject = data['subject']
            your_review.text = data['content']
            your_review.save()
            return JsonResponse(data={'your_review': serializers.serialize("json", [your_review])}, status=200)
        else:
            return JsonResponse(data={}, status=500)
    else:
        return JsonResponse(data={}, status=500)

def add_like_to_book_review(request):
    if request.is_ajax() and request.method == 'POST' and request.user.is_authenticated:
        data = request.POST.dict()
        rev_like = int(data['rev_like'])
        user = data['user_id']
        review = next(serializers.deserialize("json", data['liked_review'])).object
        if rev_like:
            review.likes.remove(user)
            review.save()
            rev_like = 0
        else:
            review.likes.append(user)
            review.save()
            rev_like = 1
        return JsonResponse(data={'rev_like': rev_like, 'review': serializers.serialize("json", [review])}, status=200)
    else:
        return JsonResponse(data={}, status=500)

def add_product_to_shopping_cart(request):
    if request.is_ajax() and request.method == 'POST' :
        data = request.POST.dict()
        book = json.loads(data['book'])
        if request.user.is_authenticated:
            user_additional_data = next(serializers.deserialize("json", data['user_additional_data'])).object
            for b in user_additional_data.order_list:
                if b['id'] == book['id']:
                    b['amount'] += book['amount']
                    if b['promotional_price'] == '0.00':
                        b['total'] = '{0:.2f}'.format((b['amount'] * float(b['price'])))
                    else:
                        b['total'] = '{0:.2f}'.format((b['amount'] * float(b['promotional_price'])))
                    break
            else:
                if book['promotional_price'] == '0.00':
                    book['total'] = '{0:.2f}'.format((book['amount'] * float(book['price'])))
                    book['index'] = len(user_additional_data.order_list)
                else:
                    book['total'] = '{0:.2f}'.format((book['amount'] * float(book['promotional_price'])))
                    book['index'] = len(user_additional_data.order_list)
                user_additional_data.order_list.append(book)
            user_additional_data.save()
            return JsonResponse(data={'user_additional_data': serializers.serialize("json", [user_additional_data])}, status=200)
        else:
            for b in request.session['order_list']:
                if b['id'] == book['id']:
                    b['amount'] += book['amount']
                    if b['promotional_price'] == '0.00':
                        b['total'] = '{0:.2f}'.format((b['amount'] * float(b['price'])))
                    else:
                        b['total'] = '{0:.2f}'.format((b['amount'] * float(b['promotional_price'])))
                    break
            else:
                if book['promotional_price'] == '0.00':
                    book['total'] = '{0:.2f}'.format((book['amount'] * float(book['price'])))
                    book['index'] = len(request.session['order_list'])
                else:
                    book['total'] = '{0:.2f}'.format((book['amount'] * float(book['promotional_price'])))
                    book['index'] = len(request.session['order_list'])
                request.session['order_list'].append(book)
            request.session.modified = True
            return JsonResponse(data={}, status=200)
    else:
        return JsonResponse(data={}, status=500)