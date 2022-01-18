from django.contrib import admin
from .models import Book, Book_Review

class BookReviewsPanel(admin.StackedInline):
    model = Book_Review
    fields = ('user', 'subject', 'text')

class BooksWithReviews(admin.ModelAdmin):
    date_hierarchy = 'publication_date'
    model = Book
    inlines = [
        BookReviewsPanel,
    ]

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if change:
            obj.is_created = False
            form.changed_data.append('menu_img')
            form.changed_data.append('book_page_img')
            obj.save(update_fields=form.changed_data)
        else:
            obj.is_created = True
            obj.save()

admin.site.register(Book, BooksWithReviews)

