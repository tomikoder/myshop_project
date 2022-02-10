import os
from django.core.management.base import BaseCommand
from pages.models import Book

class Command(BaseCommand):
    help = 'Clean folder'

    def add_arguments(self, parser):
        parser.add_argument('--extra', default=False, type=bool, help='Remove all redundant pics.')

    def handle(self, *args, **options):
        path = os.path.normpath('./media/')
        files = os.listdir(path)
        c = 0
        for f in files:
            f = os.path.join(path, f)
            if os.path.isfile(f) == True:
                os.remove(f)
                c += 1
        if options['extra'] == True:
            books = Book.objects.all().values_list('cover_img', 'book_page_img', 'menu_img')
            cover_img_set = {os.path.split(p[0])[-1] for p in books}
            menu_img_set  = {os.path.split(p[1])[-1] for p in books}
            book_page_img = {os.path.split(p[2])[-1] for p in books}
            path = os.path.join('.', 'media', 'covers')
            for f in os.listdir(path):
                if not f in cover_img_set:
                    file_path = os.path.join(path, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        c += 1
            path = os.path.join('.', 'media', 'covers', 'md')
            for f in os.listdir(path):
                if not f in menu_img_set:
                    file_path = os.path.join(path, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        c += 1
            path = os.path.join('.', 'media', 'covers', 'sm')
            for f in os.listdir(path):
                if not f in book_page_img:
                    file_path = os.path.join(path, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        c += 1
        if c > 0:
            print(str(c) + " files was removed.")
        else:
            print("No files to remove.")









