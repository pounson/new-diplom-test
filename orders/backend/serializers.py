from rest_framework import serializers
from .models import Users, Contacts, ConfirmEmailToken, Categories, Shops, OrderItems, Products, ProductsInfo, \
    ProductParameter, Orders, Parameters
from django.utils.translation import gettext_lazy as _


class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = ('id', 'user_id', 'city', 'street', 'build', 'corpus', 'apartment', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user_id': {'write_only': True}
        }


class UsersSerializer(serializers.ModelSerializer):
    contacts = ContactsSerializer(read_only=True, many=True)

    class Meta:
        model = Users
        fields = ('id', 'first_name', 'last_name', 'email', 'company', 'position', 'contacts')
        read_only_fields = ('id',)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=65, min_length=8, write_only=True)

    class Meta:
        model = Users
        fields = ['email', 'password']


class LoginTokenResponseSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255, min_length=1)

    class Meta:
        model = ConfirmEmailToken
        fields = ['token']


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ShopsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shops
        fields = ('id', 'name', 'status_work',)
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    category_id = CategoriesSerializer()

    class Meta:
        model = Products
        fields = ('name', 'category_id',)


class ParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parameters
        fields = ('id', 'name',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter_id = ParameterSerializer(read_only=True)

    class Meta:
        model = ProductParameter
        fields = ('parameter_id', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product_id = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductsInfo
        fields = ('id', 'shop_id', 'product_id', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ('id', 'order_id', 'product_info_id', 'quantity',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order_id': {'write_only': True}
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info_id = ProductInfoSerializer(read_only=True)


class OrdersSerializer(serializers.ModelSerializer):
    order_id = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = serializers.IntegerField()
    contact = ContactsSerializer(read_only=True)

    class Meta:
        model = Orders
        fields = ('order_id', 'ordered_items', 'status', 'date', 'total_sum', 'contact',)
        read_only_fields = ('id',)

