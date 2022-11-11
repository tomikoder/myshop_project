from django.urls import path, include, re_path
from .views import (CustomSignupView, CustomLoginView, YouShoppingCart,
    clear_shopping_cart, remove_product_from_shc, change_product_amount_in_sch,
    Finalize_Order, Person_Page, confmail)

urlpatterns =[
    path('signup/', CustomSignupView.as_view(), name='account_signup'),
    path('login/', CustomLoginView.as_view(), name='account_login'),
    re_path(
        r"^confirm-email/(?P<key>[-:\w]+)/$",
        confmail,
        name="account_confirm_email",
    ),
    path('ashoppingcartlogin/', YouShoppingCart.as_view(), name="shopping_cart"),
    path('personalpage/', Person_Page.as_view(), name='person_page'),
    path('finalizeorder/', Finalize_Order.as_view(), name='finalize_order'),
    path('clear/shc/', clear_shopping_cart),
    path('remove/items/shc/', remove_product_from_shc),
    path('change/items/shc/', change_product_amount_in_sch),
    path('regulamin/accounts/login/', CustomLoginView.as_view()),
    path('regulamin/accounts/signup/', CustomSignupView.as_view()),
]
