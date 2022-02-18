from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, AdditionalData
from .custom_signals import user_is_created
from .adapter import MyDefaultAdapter

@receiver(user_is_created, sender=MyDefaultAdapter)
def populate_additional_db(sender, instance, **kwargs):
        AdditionalData(user_id=instance.id).save()




