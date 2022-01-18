import django.dispatch

rate_is_updated = django.dispatch.Signal()
book_is_liked = django.dispatch.Signal()
book_is_unliked = django.dispatch.Signal()
book_review_is_created = django.dispatch.Signal()
book_review_is_saved = django.dispatch.Signal()
