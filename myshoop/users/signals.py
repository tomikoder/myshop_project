from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import CustomUser, AdditionalData, Orders
from .custom_signals import user_is_created, order_instance_is_created
from .adapter import MyDefaultAdapter
from pages.models import MyShopConf
from .forms import UserDataFormOrder, lista_województw
from django.contrib.auth import get_user_model
from django.conf import settings
import os
from django.core.mail import send_mail


@receiver(post_save, sender=get_user_model())
def populate_additional_db(sender, instance, created, **kwargs):
    if created == True:
        AdditionalData(user_id=instance.id).save()

@receiver(pre_save, sender=Orders)
def add_initial_data_two(sender, instance, **kwargs):
    num = MyShopConf.objects.raw('''update pages_myshopconf set order_num = order_num + 1
                                          where id = 1
                                          returning id, order_num; 
                                     ''')[0].order_num
    instance.number = num

@receiver(post_save, sender=Orders)
def final_tasks(sender, instance, **kwargs):
    u = instance.user
    d = u.additionaldata
    sum = float(0)
    for p in d.order_list:
        sum += float(p['total'])
    d.order_list = []
    d.save()
    txt = "Zamówienie nr %s\nKwota %s\nDane adresata:\n%s %s %s %s %s"
    for i in lista_województw:
        if i[0] == u.region:
            region = i[1]

    txt = txt % (instance.number, sum, (u.first_name + " " + u.last_name), region, u.city, u.return_postal_code(), u.address)
    send_mail('Potwierdzenie przyjęcia zamówienia',
              txt,
              'myshop@tomekj344.pl',
              [u.email]
              )









