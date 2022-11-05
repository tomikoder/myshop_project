from django.core.management.base import BaseCommand
from pages.models import Book
#from elasticsearch import Elasticsearch, client

'''
class Command(BaseCommand):
    help = 'create index'

    def handle(self, *args, **options):
        es = Elasticsearch()
        index = client.IndicesClient(es)
        body = {"settings": {"number_of_shards": 1,
                             "number_of_replicas": 0},
                "mappings": {
                    "books": {
                        "_source": {
                            "enabled": False
                        },
                        "properties": {
                            "title": {
                                "type": "string",
                                "index": "not_analyzed"
                            },
                            "authors": {
                                "type": "string",
                                "index": "not_analyzed",
                            },
                            "description": {
                                "type": "text"
                            },
                        }
                    }
                }}
        index.create(index="products", body=body)
        books_to_index = Book.objects.all()
        for b in books_to_index:
            es.create(index="products",
                      doc_type="books",
                      id=b.id,
                      body={"title": b.title,
                            "authors": b.list_of_authors_2(),
                            "description": b.description
                            })
'''


