from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    city = models.CharField(max_length=20, blank=True, default='')
    region = models.CharField(max_length=20, default='1')
    address = models.CharField(max_length=20, blank=True, default='')
    postal_code = models.IntegerField(null=True, default=None)
    phone_number = models.IntegerField(null=True, default=None)

    def is_verified(self):
        for mail in self.emailaddress_set.all():
            if mail.verified:
                return True
            else:
                return False

    def return_postal_code(self):
        pc = str(self.postal_code)
        return pc[:2] + "-" + pc[2:5]

    def return_form_data(self):
        return {'first_name': self.first_name, 'last_name': self.last_name,
                'city': self.city, 'address': self.address, 'postal_code': self.return_postal_code(),
                'phone_number': self.phone_number, 'region': self.region
                }

class AdditionalData(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    liked_books = models.JSONField(default=dict)
    order_list = models.JSONField(default=list, null=False)

