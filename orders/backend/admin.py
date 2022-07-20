from django.contrib import admin
from .models import Users, Contacts, Shops, Categories, Products, ProductsInfo, Parameters, \
    ProductParameter, Orders, OrderItems, ConfirmEmailToken


class UsersAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'type', 'is_active', 'is_staff',)


class ContactsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id_id', 'city', 'street', 'build', 'corpus', 'apartment', 'phone')


class ShopsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id_id', 'name', 'status_work', 'url_shop')


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_id_id', 'name')


class ProductsInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop_id_id', 'product_id_id', 'external_id', 'quantity', 'price', 'price_rrc')


class ParametersAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'parameter_id_id', 'value', 'product_info_id_id')


class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id_id', 'product_info_id_id', 'quantity')


class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id_id', 'status', 'date', 'contact_id')


admin.site.register(Users, UsersAdmin)

admin.site.register(Contacts, ContactsAdmin)
admin.site.register(Shops, ShopsAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(ProductsInfo, ProductsInfoAdmin)
admin.site.register(Parameters, ParametersAdmin)
admin.site.register(ProductParameter, ProductParameterAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(OrderItems, OrderItemsAdmin)
admin.site.register(ConfirmEmailToken)
