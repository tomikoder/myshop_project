from django.test import TestCase, Client
from django.contrib.auth import get_user_model, get_user
from django.urls import resolve
from .models import *
import os
from django.core import serializers
import json

file = open('test_output', 'w')
category = Categories.objects.all()[0]

user_credentials = {'username': 'somename', 'email': 'testuser@mail.com', 'first_name': 'Somename', 'last_name': 'Somesurname',
                    'city': 'Somecity', 'address': 'someaddress 00', 'postal_code': 00000,
                    'phone_number': 000000000, 'region': 'Zadupie', 'password': 'somepass',
                    }
some_book = {'title': 'Some Title', 'description': 'Cool book', 'availability': True, 'price': 17.00, 'number_of_items': 1000}


class Login_Test(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(**user_credentials)
        self.author = Author.objects.create(name='Some Name')
        self.category = Categories.objects.create(name='Somecategory')
        self.user = get_user_model().objects.get(pk=1)
        self.book = Book.objects.create(**some_book)
        self.book.author.add(self.author)
        self.book.category.add(self.category)
        self.client = Client()
        self.client.login(username='testuser@mail.com', password='somepass')
    def test_vote(self):
        self.data = {'book': serializers.serialize("json", [self.book]), 'stars': 5, 'first_vote': 1}
        self.response = self.client.post('/vote/book/',data=self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(self.response.status_code, 201)
        self.data = json.loads(self.response.content)
        self.assertNotEqual(self.data['your_rate'], None)
        self.data = {'book': serializers.serialize("json", [self.book]), 'stars': 3, 'first_vote': 0}
        self.response = self.client.post('/vote/book/', data=self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
#        self.assertEqual(self.response.status_code, 201)

#    def test_db(self):
#        self.assertEqual(self.user.is_authenticated, True)
#        self.response = self.client.get(reverse('book_detail', kwargs={'link': self.book.link}))
#        self.assertEqual(self.response.status_code, 200)




