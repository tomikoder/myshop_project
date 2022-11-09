from django.db.models.signals import post_save, pre_save, post_delete, post_migrate, m2m_changed
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.conf import settings
from PIL import Image
import os
from django.core.exceptions import ObjectDoesNotExist
from .custom_signals import rate_is_updated, book_is_liked, book_is_unliked, book_review_is_created, book_review_is_saved, book_is_created
from .views import vote_on_book
from .models import Book, Book_Review, MyShopConf, Product
from django.db.models import Avg, F
from django.conf import settings
from django.apps import apps
from django.contrib.postgres.search import SearchVector
from .admin import BooksWithReviews

size_lg = 352, 500
size_md = 278, 392
size_sm = 140, 198


def content_file_name(filename):
    index = MyShopConf.objects.raw('''update pages_myshopconf set pics_num = pics_num + 1
                                     where id = 1
                                     returning id, pics_num; 
                                    ''')[0].pics_num

    ext = filename.split('.')[-1]
    filename = "%s_lg.%s" % (index, ext)
    return filename, ext

@receiver(user_logged_in)
def update_shoping_cart(sender, user, request, **kwargs):
    user_additional_data = user.additionaldata
    if ('order_list' in request.session) and request.session['order_list']:
        for b in request.session['order_list']:
            for b2 in user_additional_data.order_list:
                if b['id'] == b2['id']:
                    b2['amount'] += b['amount']
                    break
            else:
                user_additional_data.order_list.append(b)
        user_additional_data.save()
        request.session['order_list'] = []

@receiver(pre_save, sender=Book)
def add_minipics(sender, instance, **kwargs):
    if (kwargs['update_fields'] is not None and 'cover_img' in kwargs['update_fields']) or (hasattr(instance, 'is_created') and instance.is_created):
        new_file_name, ext = content_file_name(os.path.split(instance.cover_img.name)[-1])
        file = Image.open(instance.cover_img.path)
        if file.size > size_lg:
            file.thumbnail(size_lg, Image.ANTIALIAS)
        instance.cover_img.name = 'covers//' + new_file_name
        file.thumbnail(size_md, Image.ANTIALIAS)
        new_file_name = os.path.split(instance.cover_img.name)[-1][:-6] + ('md.%s' % ext)
        file.save(os.path.join(settings.MEDIA_ROOT, 'covers', 'md', new_file_name))
        instance.book_page_img = '/media/covers/md/' + new_file_name
        file.thumbnail(size_sm, Image.ANTIALIAS)
        new_file_name = os.path.split(instance.cover_img.name)[-1][:-6] + ('sm.%s' % ext)
        file.save(os.path.join(settings.MEDIA_ROOT, 'covers', 'sm', new_file_name))
        instance.menu_img = '/media/covers/sm/' + new_file_name

@receiver(post_save, sender=Book)
def update_field(sender, instance, created, **kwargs):
    if created and instance.ready_to_add_data:
        b = instance
        b.compresed_search_data = SearchVector('search_data', weight='C', config='simple',) + SearchVector('title', weight='A', config='simple',)
        b.save()

@receiver(post_delete, sender=Book)
def remove_pics(sender, instance, **kwargs):
    if os.path.isfile(instance.cover_img.path):
        os.remove(instance.cover_img.path)
    path_to_file = os.path.normpath(instance.menu_img)[1:]
    path_to_file = os.path.join('.', path_to_file)
    if os.path.isfile(path_to_file):
        os.remove(path_to_file)
    path_to_file = os.path.normpath(instance.book_page_img)[1:]
    path_to_file = os.path.join('.', path_to_file)
    if os.path.isfile(path_to_file):
        os.remove(path_to_file)

@receiver(rate_is_updated)
def evaulate_average(sender, book_pk, Book_Rate, created, **kwargs):
    data_set = Book_Rate.objects.filter(book_id=book_pk).aggregate(average_rating=Avg('rate'))
    if created:
        Book.objects.filter(pk=book_pk).update(rate=data_set['average_rating'], num_of_rates=F('num_of_rates') + 1)
        return round(data_set['average_rating'])
    else:
        Book.objects.filter(pk=book_pk).update(rate=data_set['average_rating'])
        return round(data_set['average_rating'])

@receiver(book_is_liked)
def increase_number_of_likes(sender, book_pk, **kwargs):
    Book.objects.filter(pk=book_pk).update(num_of_likes=F('num_of_likes') + 1)

@receiver(book_is_unliked)
def decrease_number_of_likes(sender, book_pk, **kwargs):
    Book.objects.filter(pk=book_pk).update(num_of_likes=F('num_of_likes') - 1)

@receiver(book_review_is_created)
def assign_number_to_review(sender, **kwargs):
    return MyShopConf.objects.raw('''update pages_myshopconf set rev_num = rev_num + 1
                                     where id = 1
                                     returning id, rev_num; 
                                    ''')[0].rev_num

@receiver(book_review_is_saved)
def assign_review_to_rate(sender, your_review, your_rate, **kwargs):
    your_rate.rev = your_review
    your_rate.save()
    return your_rate
