from django import template
from ..models import Book_Review
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.core import serializers
import simplejson as json

register = template.Library()

@register.filter(name='futfill')
def futfill(number):
    return range(4 - number)

@register.simple_tag
def get_link_to_product(type, link):
    if type == 'book':
        return '/books/' + link

@register.simple_tag
def display_authors(authors):
    if len(authors) != 1:
        return authors[0] + ' i inni'
    else:
        return authors[0]

@register.simple_tag
def return_key_val(d, k):
    return d.get(k, None)

@register.simple_tag
def return_data(user, book, book_reviews, your_rate, is_reviewed, user_additional_data, you_liked, num_of_reviews, other_books):
    if user.is_authenticated:
        data_to_back = {'user_id': user.id, 'book': json.dumps(book.serialize()), 'book_reviews': serializers.serialize('json', book_reviews), 'is_reviewed': is_reviewed,
                        'user_additional_data': serializers.serialize('json', [user_additional_data]), 'you_liked': you_liked,
                        'num_of_reviews': num_of_reviews, 'other_books': json.dumps(other_books)
                        }
        if your_rate:
            data_to_back['your_rate'] = serializers.serialize('json', [your_rate])
        return data_to_back
    else:
        return {'you_liked': 0, 'book': json.dumps(book.serialize()),
                'other_books': json.dumps(other_books)
                }

@register.simple_tag
def return_data_two(user, user_additional_data, new, best, prom):
    if user.is_authenticated:
        return {'user_id': user.id, 'user_additional_data': serializers.serialize("json", [user_additional_data]),
                'other_books': json.dumps(new + best)}
    else:
        return {'other_books': json.dumps(new + best + prom)}

@register.simple_tag
def return_data_three(user, user_additional_data, other_books, categories):
    if user.is_authenticated:
        return {'user_id': user.id, 'user_additional_data': serializers.serialize('json', [user_additional_data]),
                        'other_books': json.dumps(other_books), 'categories': json.dumps(categories)
                        }
    else:
        return {'other_books': json.dumps(other_books), 'categories': json.dumps(categories)}










