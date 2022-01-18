from django import template
from django.core import serializers

register = template.Library()

@register.simple_tag
def multiple_values(val1, val2):
    return val1 * val2

@register.simple_tag
def return_data(user, user_additional_data=None):
    if user.is_authenticated:
        return {'user_id': user.id, 'user_additional_data': serializers.serialize('json', [user_additional_data])}
    else:
        return {}

@register.simple_tag
def return_data2(user, user_additional_data, price_one, price_two):
    if user.is_authenticated:
        return {'user_id': user.id, 'user_additional_data': serializers.serialize('json', [user_additional_data]),
                'price_one': price_one, 'price_two': price_two
                }
    else:
        return {}
