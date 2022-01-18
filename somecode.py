from pages.models import Book

Book.objects.raw('''SELECT b.title, ARRAY_AGG (a.name) AS authors
                    FROM ((pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id) INNER JOIN pages_author AS a ON a.id = ba.author_id);
                    WHERE NOT (b.id = %s AND (a.id=%s OR a.id=%s);
                    GROUP BY b.id''' % (1, 2, 3))

Book.objects.raw('''SELECT b.id, b.link, b.price, b.menu_img, ARRAY_AGG (a.name) AS authors
                    FROM ((pages_book AS b INNER JOIN pages_book_author AS ba ON b.id = ba.book_id)
                    INNER JOIN pages_author AS a ON a.id = ba.author_id)
                    GROUP BY b.id;
                    ''')
