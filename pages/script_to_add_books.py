from bs4 import BeautifulSoup
import requests
from pages.models import Book
import re
import random

page = 1
month = 1
c = 0

link1 = 'https://lubimyczytac.pl'
link2 = 'https://lubimyczytac.pl/top100?page=%s&listId=listTop100&month=%s&year=2021&paginatorType=Standard'

while c != 400:
    data = requests.get((link2 % (page, month))).text
    list_page = BeautifulSoup(data, 'lxml')
    indiv_books = list_page.find_all("a", class_='authorAllBooks__singleTextTitle float-left')
    for b in indiv_books:
        data = requests.get(link1 + b['href'])
        indiv_book = BeautifulSoup(data, 'lxml')
        title = indiv_book.find("h1", class_='book__title')
        author = indiv_book.find("a", class_='link-name')
        descr = indiv_book.find("div", class_='collapse-content').text
        pages = indiv_book.find("span", class_='d-sm-inline-block book-pages book__pages pr-2 mr-2 pr-sm-3 mr-sm-3').text
        pages = int(re.match('\n([0-9]*) str.\n', pages))
        price = round(random.uniform(20 ,60), 2)






