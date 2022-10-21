from bs4 import BeautifulSoup
import requests
from pages.models import Book, Product, Book_Rate, Book_Review, Category, Author, Publisher
import re
import random
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from pages.signals import content_file_name, size_lg, size_md, size_sm
from datetime import datetime
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from pages.signals import content_file_name, size_lg, size_md, size_sm
from PIL import Image
from django.conf import settings

class Command(BaseCommand):
    '''Użyj np python manage.py fill_database 100 --sy 2020 --ey 2022, by pobrać przykładowe
       ksiązki do celów testowych.
    '''
    help = 'Add books to database'

    def add_arguments(self, parser):
        parser.add_argument('amount', type=int)
        parser.add_argument('--sy', default=2021, type=int, help='Start year')     #start year
        parser.add_argument('--ey', default=2023, type=int, help='End year')       #end_year

    def update_register(self, year, month, page, number, counter, stop=False):
        '''Log pobranych książek'''
        file = open('fill_database_log.txt', 'a')
        text = 'year-%s month-%s page-%s counter_start-%s counter_stop-%s %s\n' % (year, month, page, number, counter, datetime.now().strftime('%Y-%m-%d %X'))
        if stop == True:
            text = 'Stop at: ' + text
        file.write(text)
        file.close()
        self.stdout.write(str(counter) + " books was added.")

    def handle(self, *args, **options):
        page= 1
        month = 1
        year = options['sy']
        end_year = options['ey']
        number = options['amount']
        counter = 0
        authors = list(Author.objects.all())
        categories = list(Category.objects.all())
        publishers = list(Publisher.objects.all())
        product = Product.objects.get(name='books')
        link1 = 'https://lubimyczytac.pl'
        link2 = 'https://lubimyczytac.pl/top100?page=%s&listId=listTop100&month=%s&year=%s&paginatorType=Standard'
        books_in_db = set()
        with connection.cursor() as cursor:
            cursor.cursor.execute('''SELECT isbn
                                     FROM pages_book; 
                                  ''')
            while True:
                item = cursor.fetchone()
                if item == None:
                    break
                else:
                    books_in_db.add(item[0])
        while True:
            html_1 = BeautifulSoup(requests.get((link2 % (page, month, year))).text, 'lxml')
            if html_1.status_code == 404:
                self.update_register(year, month, page, number, counter, True)
                return
            books = html_1.find_all("a", class_='authorAllBooks__singleTextTitle float-left')
            for (i, b) in enumerate(books):
                html_2 = BeautifulSoup(requests.get(link1 + b['href']).text, 'lxml')
                b_title = html_2.find("h1", class_='book__title').text.strip()
                b_description = html_2.find("div", class_='collapse-content').text.strip()
                b_price = round(random.uniform(20, 60), 2)

                if (i % 10 == 0): # Co dziesiąta książka będzie w promocji
                    b_promotional_price = b_price - round(float(0.25) * b_price)
                else:
                    b_promotional_price = float(0)

                b_detail = html_2.find("div", id='book-details').find("dl")
                b_isbn = b_detail.find("dt", string=re.compile('ISBN:'))

                if b_isbn:
                    b_isbn = int(b_isbn.find_next_sibling("dd").text.strip())
                    if b_isbn in books_in_db:
                        continue
                else:
                    b_isbn = 0

                b_original_title = html_2.find("dt", string=re.compile('Tytuł oryginału:'))
                if b_original_title:
                    b_original_title = b_original_title.find_next_sibling("dd").text.strip()
                else:
                    b_original_title = 'n/d'
                b_categories = b_detail.find("dt", string=re.compile('Kategoria:')).find_next_sibling("dd").text.strip().split(',')
                b_authors = html_2.find("a", class_='link-name').text.strip().split(',')

                index = 0
                while index < len(b_categories):
                    b_categories[index] = b_categories[index].strip()
                    index += 1

                index = 0
                while index < len(b_authors):
                    b_authors[index] = b_authors[index].strip()
                    index += 1

                b_publisher  = b_detail.find("dt", string=re.compile('Wydawnictwo:')).find_next_sibling("dd").text.strip()
                b_publication_date = b_detail.find("dt", string=re.compile('Data wydania:')).find_next_sibling("dd").text.strip()
                b_pages = b_detail.find("dt", string=re.compile('Liczba stron:'))
                if b_pages:
                    b_pages = int(b_pages.find_next_sibling("dd").text.strip())
                b_language = b_detail.find("dt", string=re.compile('Język:')).find_next_sibling("dd").text.strip()

                books_in_db.add(b_isbn)

                for p in publishers:
                    if p.name == b_publisher:
                        b_publisher = p
                        break
                else:
                    b_publisher = Publisher.objects.create(name=b_publisher)
                    b_publisher.save()
                    publishers.append(b_publisher)

                new_book = Book.objects.create(title=b_title, original_title=b_original_title, description=b_description, availability=True, price=b_price,
                                    promotional_price=b_promotional_price, pages=b_pages, publisher=b_publisher, language=b_language,
                                    isbn=b_isbn, publication_date=b_publication_date, product=product,
                                    number_of_items=1000,
                                    )

                pic_link = html_2.find("a", id="js-lightboxCover")["href"]
                pic = requests.get(pic_link)
                new_file_name, ext = content_file_name(os.path.split(pic_link)[-1])
                open(os.path.join(settings.MEDIA_ROOT, 'covers', new_file_name), 'wb').write(pic.content)
                file = Image.open(os.path.join(settings.MEDIA_ROOT, 'covers', new_file_name))
                if file.size > size_lg:
                    file.thumbnail(size_lg, Image.ANTIALIAS)
                new_book.cover_img.name = 'covers//' + new_file_name
                file.thumbnail(size_md, Image.ANTIALIAS)
                new_file_name = os.path.split(new_book.cover_img.name)[-1][:-6] + ('md.%s' % ext)
                file.save(os.path.join(settings.MEDIA_ROOT, 'covers', 'md', new_file_name))
                new_book.book_page_img = '/media/covers/md/' + new_file_name
                file.thumbnail(size_sm, Image.ANTIALIAS)
                new_file_name = os.path.split(new_book.cover_img.name)[-1][:-6] + ('sm.%s' % ext)
                file.save(os.path.join(settings.MEDIA_ROOT, 'covers', 'sm', new_file_name))
                new_book.menu_img = '/media/covers/sm/' + new_file_name
                new_book.save()

                for b_a in b_authors:
                    for a in authors:
                        if b_a == a.name:
                            new_book.author.add(a)
                            break
                    else:
                        new_author = Author.objects.create(name=b_a)
                        new_author.save()
                        authors.append(new_author)
                        new_book.author.add(new_author)

                for b_c in b_categories:
                    for c in categories:
                        if b_c == c.name:
                            new_book.category.add(c)
                            break
                    else:
                        new_category = Category.objects.create(name=b_c)
                        new_category.save()
                        product.categories.add(new_category)
                        categories.append(new_category)
                        new_book.category.add(new_category)
                counter += 1
                if counter == number:
                    self.update_register(year, month, page, number, counter)
                    return

            last_page = html_1.find("li", class_="page-item next-page disabled")

            if last_page == None:
                page = 1
                if month == 12:
                    month = 1
                    year += 1
                    if year == end_year:
                        self.update_register(year, month, page, number, counter)
                        return
                else:
                    month += 1
            else:
                page += 1


