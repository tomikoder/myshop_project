from django.urls import path, re_path
from .views import (HomePageView, RegulaminPageView, BookDetailPageView, vote_on_book, post_book_review, add_like_to_book_review,
                    edit_book_review, add_like_to_book, remove_like_from_book, remove_book_review, add_product_to_shopping_cart,
                    New_Books, Best_Books, Prom_Books, Specific_Book_Categories, Specific_Book_Category, Search_Book_Two
                    )

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('regulamin/', RegulaminPageView.as_view(), name='regulamin'),
    path('books/<uuid:link>/', BookDetailPageView.as_view(), name='book_detail'),
    path('vote/book/', vote_on_book, name='vote'),
    path('like/book/', add_like_to_book),
    path('unlike/book/', remove_like_from_book),
    path('post/book/review/', post_book_review),
    path('remove/book/review/', remove_book_review),
    path('like/book/review/', add_like_to_book_review),
    path('edit/book/comment/', edit_book_review),
    path('add/product/', add_product_to_shopping_cart),
    path('new/book/', New_Books.as_view(), name='new_books'),
    path('best/book', Best_Books.as_view(), name='the_best'),
    path('prom/book/', Prom_Books.as_view(), name='prom'),
    path('search/', Search_Book_Two.as_view()),
    path('category/books/', Specific_Book_Categories.as_view()),
    path('specific/category/books/<str:category>', Specific_Book_Category.as_view())
]