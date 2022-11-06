from django.urls import reverse_lazy
from allauth.account.views import SignupView, LoginView, ConfirmEmailView
from .forms import CustomSignupForm as signup_form, CustomLoginForm as login_form, DeliveryAddress, UserDataForm, UserDataFormOrder
from allauth.account.adapter import get_adapter
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import render
from django.views.generic import DetailView, UpdateView, CreateView
from .models import AdditionalData
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from pages.models import Product
from users.models import AdditionalData
from pages.views import music_categories, movies_categories, others_categories, games_categories
from .models import Orders

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CustomSignupView(SignupView):
    http_method_names = ['post', 'put']
    context_object_name = 'signup_form'
    form_class = signup_form
    success_url = reverse_lazy('home')
    success_message = 'Gratulacje: Założyłeś konto na MyShop.com.'

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CustomLoginView(LoginView):
    http_method_names = ['post', 'put']
    context_object_name = 'login_form'
    form_class = login_form
    success_url = reverse_lazy('home')
    success_message = 'Witamy ma MyShop.com !'

class Custom_DetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = signup_form
        context['login_form'] = login_form
        context['music_categories'] = music_categories
        context['movies_categories'] = movies_categories
        context['book_categories'] =   Product.objects.get(name='books').categories.all()
        context['others_categories'] = others_categories
        context['games_categories'] = games_categories
        user = self.request.user
        if user.is_authenticated:
            context['user_additional_data'] = user.additionaldata
            c = 0
            for i in context['user_additional_data'].order_list:
                c+= i['amount']
            context['num_of_items_in_shca'] = c
        else:
            if not 'order_list' in self.request.session:  #Używam ciasteczek by przetrrzymywać dane o koszyku.
                self.request.session['order_list'] = []
                context['num_of_items_in_shca'] = 0
            else:
                c = 0
                for i in self.request.session['order_list']:
                    c+= i['amount']
                context['num_of_items_in_shca'] = c
        return context


class CustomMailConform(ConfirmEmailView, Custom_DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = Custom_DetailView.get_context_data(self, **kwargs)
        return context

@method_decorator(ensure_csrf_cookie, name='dispatch')
class YouShoppingCart(DetailView):
    template_name = 'shoppingcart.html'
    model = AdditionalData
    context_object_name = 'products_list'

    def get_object(self):
        if self.request.user.is_authenticated:
            queryset = self.model._default_manager.all()
            indicator = self.request.user.pk
            queryset = queryset.filter(pk=indicator)
            obj = queryset.get().order_list
            sum = float(0)
            c = 0
            for p in obj:
                sum += float(p['total'])
                c += p['amount']
            self.extra_context = {'num_of_items_in_shca': c, 'sum': f'{sum:.2f}', 'user_additional_data': queryset.get()}
            return obj
        else:
            obj = self.request.session['order_list']
            sum = float(0)
            c = 0
            for p in obj:
                sum += float(p['total'])
                c += p['amount']
            self.extra_context = {'num_of_items_in_shca': c, 'sum': f'{sum:.2f}'}
            return obj

@method_decorator(ensure_csrf_cookie, name='dispatch')
class Finalize_Order(CreateView):
    template_name = 'finalizeorder.html'
    form_class = UserDataFormOrder
    model = Orders
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sum = float(0)
        c = 0
        for p in self.obj.order_list:
            sum += float(p['total'])
            c += p['amount']

        context.update({'num_of_items_in_shca': c, 'user_additional_data': self.obj,
                   'price_one': f'{(sum + 13):.2f}', 'price_two': f'{(sum + 9):.2f}',
                   'first_name': self.request.user.first_name, 'last_name': self.request.user.last_name
                  })
        return context

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.request.user.return_form_data(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
            })
        return kwargs

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
            form_class.user = self.request.user
            self.obj = form_class.additionaldata = self.request.user.additionaldata
        return form_class(**self.get_form_kwargs())

@method_decorator(ensure_csrf_cookie, name='dispatch')
class Person_Page(LoginRequiredMixin, UpdateView):
    template_name = 'personalsite.html'
    model = get_user_model()
    context_object_name = 'user'
    raise_exception = True
    form_class = UserDataForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = signup_form
        context['login_form'] = login_form
        context['music_categories'] = music_categories
        context['movies_categories'] = movies_categories
        context['book_categories'] =   Product.objects.get(name='books').categories.all()
        context['others_categories'] = others_categories
        context['games_categories'] = games_categories
        return context


    def get_object(self):
        user_additional_data = self.request.user.additionaldata
        self.extra_context = {'num_of_items_in_shca': len(user_additional_data.order_list)}
        return self.request.user

def clear_shopping_cart(request):
    if request.is_ajax() and request.method == 'POST':
        if request.user.is_authenticated:
            data = request.POST.dict()
            user_additional_data = next(serializers.deserialize("json", data['user_additional_data'])).object
            user_additional_data.order_list = []
            user_additional_data.save()
            return JsonResponse(data={'user_additional_data': serializers.serialize("json", [user_additional_data])}, status=201)
        else:
            request.session['order_list'] = []
            return JsonResponse(data={}, status=201)
    else:
        return JsonResponse(data={}, status=500)

def remove_product_from_shc(request):
    if request.is_ajax() and request.method == 'POST':
        data = request.POST.dict()
        index = int(data['index'])
        if request.user.is_authenticated:
            user_additional_data = next(serializers.deserialize("json", data['user_additional_data'])).object
            substract = user_additional_data.order_list[index]['amount']
            message = "Usunięto %sx %s" % (substract, user_additional_data.order_list.pop(index)['title'])
            c = index
            sum = 0
            while c < len(user_additional_data.order_list):
                user_additional_data.order_list[c]['index'] = c
                sum += float(user_additional_data.order_list[c]['total'])
                c += 1
            user_additional_data.save()
            return JsonResponse(data={'user_additional_data': serializers.serialize("json", [user_additional_data]),
                                      'sum': f'{sum:.2f}', 'substract': substract, 'message': message}, status=201)
        else:
            cookies = request.session
            substract = cookies['order_list'][index]['amount']
            message = "Usunięto %sx %s" % (substract, cookies['order_list'].pop(index)['title'])
            c = index
            sum = 0
            while c < len(cookies['order_list']):
                cookies['order_list'][c]['index'] = c
                sum += float(cookies['order_list'][c]['total'])
                c += 1
            cookies.modified = True
            return JsonResponse(data={'sum': f'{sum:.2f}', 'substract': substract, 'message': message}, status=201)

    else:
        return JsonResponse(data={}, status=500)

def change_product_amount_in_sch(request):
    if request.is_ajax() and request.method == 'POST':
        data = request.POST.dict()
        index = int(data['index'])
        new_amount = int(data['new_amount'])
        if request.user.is_authenticated:
            user_additional_data = next(serializers.deserialize("json", data['user_additional_data'])).object
            user_additional_data.order_list[index]['amount'] = new_amount
            user_additional_data.order_list[index]['total'] = '{:.2f}'.format((new_amount * float(user_additional_data.order_list[index]['price'])))
            user_additional_data.save()
            sum = 0
            for i in user_additional_data.order_list:
                sum += float(i['total'])
            return JsonResponse(data={'new_total': user_additional_data.order_list[index]['total'], 'new_sum': f'{sum:.2f}',
                                      'user_additional_data': serializers.serialize("json", [user_additional_data])}, status=201)
        else:
            cookies = request.session
            cookies['order_list'][index]['amount'] = new_amount
            cookies['order_list'][index]['total'] = '{:.2f}'.format((new_amount * float(cookies['order_list'][index]['price'])))
            cookies.modified = True
            sum = 0
            for i in cookies['order_list']:
                sum += float(i['total'])
            return JsonResponse(data={'new_total': cookies['order_list'][index]['total'], 'new_sum': f'{sum:.2f}'}, status=201)
    else:
        return JsonResponse(data={}, status=500)
