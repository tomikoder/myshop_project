from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import CustomUser, AdditionalData, Orders_Two
from .custom_signals import user_is_created, order_instance_is_created
from .adapter import MyDefaultAdapter
from pages.models import MyShopConf
from .forms import UserDataFormOrder
from copy import copy

@receiver(user_is_created, sender=MyDefaultAdapter)
def populate_additional_db(sender, instance, **kwargs):
        AdditionalData(user_id=instance.id).save()

@receiver(order_instance_is_created, sender=UserDataFormOrder)
def add_initial_data(sender, instance, user, **kwargs):
        instance.user = user
        print('A')
        instance.order_list = copy(user.additionaldata.order_list)

@receiver(pre_save, sender=Orders_Two)
def add_initial_data_two(sender, instance, **kwargs):
        num = MyShopConf.objects.raw('''update pages_myshopconf set order_num_two = order_num_two + 1
                                          where id = 1
                                          returning id, order_num_two; 
                                       ''')[0].order_num_two
        instance.number = num

@receiver(post_save, sender=Orders_Two)
def final_tasks(sender, instance, **kwargs):
        additional_data = instance.user.additionaldata
        additional_data.order_list = []
        additional_data.save()








