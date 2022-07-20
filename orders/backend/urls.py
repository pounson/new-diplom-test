from django.urls import path

from . import views

from .views import RegisterUsers, ConfirmAccount, LoginAccount, AccountDetails, CategoriesView, ShopsView, \
    PartnerUpdate, PartnerState, PartnerOrders, ContactsView, ProductInfoView, BasketView, OrderView
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm


urlpatterns = [
    path('', views.home, name='home'),
    # path('sign_up', views.sign_up, name='sign_up'),
    path('register', RegisterUsers.as_view(), name='register'),
    path('login', LoginAccount.as_view(), name='login'),
    # сброс пароля с токеном сессии\авторизации пользователя + указать email
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    # смена пароля с токеном сессии\авторизации пользователя + полями json("token" сброса + логин\email + пас)
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
    # подтверждение почты, указать json(email, token)
    path('register/confirm', ConfirmAccount.as_view(), name='user_register_confirm'),
    # /GET получить инфу /POST изменить инфу
    path('user/details', AccountDetails.as_view(), name='user_details'),
    path('user/contacts', ContactsView.as_view(), name='user_contacts'),
    path('categories', CategoriesView.as_view(), name='categories'),
    path('shops', ShopsView.as_view(), name='shops'),

    # Загрузка прайса
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),

    path('partner/state', PartnerState.as_view(), name='partner-state'),
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),

    path('products', ProductInfoView.as_view(), name='shops'),
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),
]
