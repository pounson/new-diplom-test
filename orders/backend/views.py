from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q, Sum, F
from django.db import IntegrityError
from requests import get

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListAPIView

from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from yaml import load as load_yaml, Loader

from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password

from .models import ConfirmEmailToken, Categories, Shops, ProductsInfo, Products, Parameters, ProductParameter, \
    Users, Orders, Contacts, OrderItems

from .send_email import new_user_registered, new_order

from .serializers import UsersSerializer, LoginSerializer, LoginTokenResponseSerializer, CategoriesSerializer, \
    ShopsSerializer, OrdersSerializer, ContactsSerializer, ProductInfoSerializer, OrderItemSerializer

import sys
# sys.path.insert(1, 'E:\\YakoBro\\Proekt_Python\\Django_full_project(final-diplom)\\orders')
# from celery_sender import new_user_registered


def home(request):
    return render(request, 'backend/home.html')


def log_in(request):
    return render(request, 'backend/log_in.html')


def sign_up(request):
    return render(request, 'backend/sign_up.html')


class RegisterUsers(APIView):

    def post(self, request, *args, **kwargs):
        required_fields = {'email', 'password', 'first_name', 'last_name', }
        if required_fields.issubset(request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                user_serializer = UsersSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()

                    # send signal mail
                    # new_user_registered.send(sender=self.__class__, user_id=user.id)
                    new_user_registered.delay(user_id=user.id)
                    # new_user_registered(user_id=user.id)

                    return JsonResponse({'Status': True, 'MSG': 'Пользователь создан'})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({
            'Status': False,
            'Errors': f'Не указаны все необходимые аргументы. Не указано: {list(required_fields ^ set(request.data.keys()))}'
        })


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """
    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return JsonResponse({'Status': True, 'MSG': 'Почта подтверждена.'})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'
                                                        f"({list({'email', 'token'} ^ set(request.data.keys()))})"})


class LoginAccount(GenericAPIView):
    """
    Авторизация пользователя

    Метод для авторизации пользователя
    """
    serializer_class = LoginSerializer

    @swagger_auto_schema(responses={200: LoginTokenResponseSerializer()})
    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({'token': token.key})

            return JsonResponse({'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Errors': "Не указаны все необходимые аргументы. "
                                       f"({list({'email', 'password'} ^ set(request.data.keys()))})"})


class AccountDetails(APIView):
    """
    Класс для работы с данными пользователя
    """

    # получить данные
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        serializer = UsersSerializer(request.user)
        return Response(serializer.data)

    # Редактирование методом POST
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        # проверяем обязательные аргументы

        if 'password' in request.data:
            errors = {}
            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                request.user.set_password(request.data['password'])

        # проверяем остальные данные
        user_serializer = UsersSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class CategoriesView(ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


class ShopsView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shops.objects.filter(status_work=True)
    serializer_class = ShopsSerializer


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Авторизуйтесь'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)

                shop, _ = Shops.objects.get_or_create(name=data['shop'], user_id=Users.objects.get(id=request.user.id))
                for category in data['categories']:
                    category_object, _ = Categories.objects.get_or_create(id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductsInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Products.objects.get_or_create(name=item['name'],
                                                                category_id=Categories.objects.get(id=item['category']))

                    product_info = ProductsInfo.objects.create(product_id=Products.objects.get(id=product.id),
                                                               external_id=item['id'],
                                                               # model=item['model'],
                                                               price=item['price'],
                                                               price_rrc=item['price_rrc'],
                                                               quantity=item['quantity'],
                                                               shop_id=Shops.objects.get(id=shop.id))
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameters.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=ProductsInfo.objects.get(id=product_info.id),
                                                        parameter_id=Parameters.objects.get(id=parameter_object.id),
                                                        value=value)

                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerState(APIView):
    """
    Класс для работы со статусом поставщика
    """
    # получить текущий статус
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        shop = request.user.shops
        serializer = ShopsSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        status_work = request.data.get('status_work')
        if status_work is not None:
            try:
                Shops.objects.filter(user_id=request.user.id).update(status_work=bool(status_work))
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками
    """
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        order = Orders.objects.filter(user_id=request.user.id).exclude(status='basket').prefetch_related(
            'ordered_items__product_info_id_id__product_id_id__category_id_id',
            'ordered_items__product_info_id_id__product_parameters__parameter_id_id').select_related(
            'contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info_id_id__price'))).distinct()

        serializer = OrdersSerializer(order, many=True)
        return Response(serializer.data)


class ContactsView(APIView):
    """
    Класс для работы с контактами покупателей
    """

    # получить мои контакты
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contacts.objects.filter(
            user_id=request.user.id)
        serializer = ContactsSerializer(contact, many=True)
        return Response(serializer.data)

    # добавить новый контакт
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'city', 'street', 'phone', 'build'}.issubset(request.data):
            request.data.update({'user_id': request.user.id})
            serializer = ContactsSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # удалить контакт
    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('id')
        if items_sting:
            query = Q()
            objects_deleted = False
            for contact_id in items_sting:
                query = query | Q(user_id=request.user.id, id=contact_id)
                objects_deleted = True

            if objects_deleted:
                deleted_count = Contacts.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # редактировать контакт
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'id' in request.data:
            contact = Contacts.objects.filter(id=request.data['id'], user_id=request.user.id).first()
            if contact:
                serializer = ContactsSerializer(contact, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({'Status': True})
                else:
                    JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ProductInfoView(APIView):
    """
    Класс для поиска товаров
    """
    def get(self, request, *args, **kwargs):
        query = Q(shop_id__status_work=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product_id__category_id=category_id)

        # фильтруем и отбрасываем дубликаты
        queryset = ProductsInfo.objects.filter(
            query).select_related(
            'shop_id', 'product_id__category_id').prefetch_related(
            'product_parameters__parameter_id').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя
    """
    # получить корзину
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Orders.objects.filter(
            user_id_id=request.user.id, status='basket').prefetch_related(
            'ordered_items__product_info_id_id__product_id_id__category_id_id',
            'ordered_items__product_info_id_id__product_parameters__parameter_id_id').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info_id_id__price'))).distinct()

        serializer = OrdersSerializer(basket, many=True)
        return Response(serializer.data)

    # редактировать корзину
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            basket, _ = Orders.objects.get_or_create(user_id_id=request.user.id, status='basket')
            objects_created = 0

            for order_item in items_sting:
                order_item.update({'order_id': basket.id})
                serializer = OrderItemSerializer(data=order_item)
                if serializer.is_valid():
                    try:
                        serializer.save()
                    except IntegrityError as error:
                        return JsonResponse({'Status': False, 'Errors': str(error)})
                    else:
                        objects_created += 1

                else:

                    JsonResponse({'Status': False, 'Errors': serializer.errors})

            return JsonResponse({'Status': True, 'Создано объектов': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # удалить товары из корзины
    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_id = request.data.get('items_id')
        if items_id:
            basket, _ = Orders.objects.get_or_create(user_id_id=request.user.id, status='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_id:
                query = query | Q(order_id=basket.id, id=order_item_id)
                objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItems.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # добавить позиции в корзину
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            basket, _ = Orders.objects.get_or_create(user_id_id=request.user.id, status='basket')
            objects_updated = 0
            for order_item in items_sting:
                if order_item.get('id') and order_item.get('quantity'):
                    objects_updated += OrderItems.objects.filter(order_id=basket.id, id=order_item['id']).update(
                        quantity=order_item['quantity'])

            return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class OrderView(APIView):
    """
    Класс для получения и размещения заказов пользователями
    """
    # получить мои заказы
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order = Orders.objects.filter(
            user_id_id=request.user.id).exclude(status='basket').prefetch_related(
            'ordered_items__product_info_id_id__product_id_id__category_id_id',
            'ordered_items__product_info_id_id__product_parameters__parameter_id_id').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info_id_id__price'))).distinct()

        serializer = OrdersSerializer(order, many=True)
        return Response(serializer.data)

    # разместить заказ из корзины
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'id', 'contact'}.issubset(request.data):
            is_updated = Orders.objects.filter(user_id_id=request.user.id, id=request.data['id']).update(
                contact_id=request.data['contact'], status='new')
            if is_updated:
                new_order.send(sender=self.__class__, user_id=request.user.id)
                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
