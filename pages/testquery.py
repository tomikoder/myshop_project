from django.db import connection
from .models import Book_Review, Book

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    data_to_back = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return data_to_back


sql_script = '''WITH book AS (SELECT b.id, b.title, b.rate, ARRAY_AGG (a.name) AS authors, CAST(b.price AS VARCHAR), CAST(b.promotional_price AS VARCHAR), b.product_id, CAST(b.link AS CHAR(36)), b.menu_img  
                              FROM pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id
                                                   INNER JOIN pages_author AS a ON a.id = ba.author_id
                              WHERE b.title LIKE %s
                              GROUP BY b.id
                              LIMIT 36)
                              SELECT b2.id, b2.title, b2.rate, b2.authors, b2.price, b2.promotional_price, p.name AS product_type, b2.link, b2.menu_img, ROW_NUMBER() OVER() - 1 AS index
                              FROM book AS b2 INNER JOIN pages_product AS p ON b2.product_id = p.id;                                                              
             '''

def get_other_books(num, pk=None):
    if pk == None: pk = 1
    if num == 1:
        queryset = Book.objects.raw(sql_script, ['Harry Potter i Komnata Tajemnic'])
        return list(queryset)













