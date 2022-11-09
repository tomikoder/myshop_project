from django.core.management.base import BaseCommand
from pages.models import Book
from django.contrib.postgres.search import SearchVector
from django.db import connection

class Command(BaseCommand):
    '''Aktualizuje searchvector in pages_book'''
    def handle(self, *args, **options):
        books = Book.objects.all()
        b: Book
        for b in books:
            if not b.search_data == "": continue
            txt = ""
            txt += b.publisher.name + " "
            authors = b.author.all()
            for a in authors:
                txt += a.name + " "
            categorys = b.category.all()
            for c in categorys:
                txt += c.name + " "
            txt += "książki " + "książka"
            b.search_data = txt
            b.save()
            b.compresed_search_data = SearchVector('search_data', weight='C', config='simple',) + SearchVector('title', weight='A', config='simple',)
            b.save()







