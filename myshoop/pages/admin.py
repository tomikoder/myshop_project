from django.contrib import admin
from .models import Book, Book_Review

class BookReviewsPanel(admin.StackedInline):
    model = Book_Review
    fields = ('user', 'subject', 'text')

class BooksWithReviews(admin.ModelAdmin):
    date_hierarchy = 'publication_date'
    model = Book
    fields = ('title', 'original_title', 'author', 'description', 'price', 'promotional_price',
              'availability', 'category', 'pages', 'cover_type',
              'publisher', 'language', 'isbn', 'publication_date', 'cover_img', 'size', 'number_of_items',
              'number_of_sold',
              )
    inlines = [
        BookReviewsPanel,
    ]

    def save_model(self, request, obj, form, change):
        if change:
            obj.is_created = False
            form.changed_data.append('menu_img')
            form.changed_data.append('book_page_img')
        else:
            obj.is_created = True
        txt = ""     #Dodaje pole do wyszukiwania w full text search
        for a in form.cleaned_data['author']:
            txt += a.name + " "
        for c in form.cleaned_data['category']:
            txt += c.name + " "
        txt += form.cleaned_data['publisher'].name + " " + "ksiązki " + "ksiązka"
        if form.cleaned_data['original_title'] != 'n/d':
            txt += ' ' + form.cleaned_data['original_title']
        obj.search_data = txt
        obj.save()
    ordering = ('title',)



admin.site.register(Book, BooksWithReviews)

