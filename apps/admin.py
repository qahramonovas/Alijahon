from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html
from django.utils.html import format_html
from apps.models import Product, Category, AdminSite, WithDraw, User


# admin.site.register(Product)
# admin.site.register(Category)

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = 'id' , 'fullname' , 'phone_number1' ,'role'
    list_editable = 'role' ,


    def fullname(self , obj):
        return f"{obj.first_name} {obj.last_name}"
    fullname.short_description = "Fullname"


    def phone_number1(self , obj):
        return f"+998 {obj.phone_number}"

    phone_number1.short_description = 'Phone Number'



@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    exclude = 'slug',


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    exclude = 'slug',

@admin.register(AdminSite)
class AdminSite(ModelAdmin):
    pass

@admin.register(WithDraw)
class WithDrawAdmin(ModelAdmin):
    list_display = "id" , "phone_number" , "status" , "card_number" , "type" , "image","formatted_create_at" , "message" ,
    list_editable = 'status' , 'message' , 'image',

    def phone_number(self,obj):
        return f"+998 {obj.user.phone_number}"

    def formatted_create_at(self , obj):
        return obj.create_at.strftime("%Y/%m/%d")

    formatted_create_at.short_description = 'Create At'


    def status_button(self, obj):
        if obj.status == 'under review':
            color = 'blue'
        elif obj.status == 'completed':
            color = 'green'
        elif obj.status == 'canceled':
            color = 'red'
        else:
            color = 'gray'  # Boshqa holatlar uchun

        return format_html(
            '<button style="background-color: {}; color: white; border: none; padding: 5px 10px;">{}</button>',
            color,
            obj.status.capitalize()
        )

    status_button.short_description = 'Status'

    def save_model(self , request , obj , form , change):
        if change:
            old_obj = WithDraw.objects.filter(pk=obj.pk).first()
            if old_obj.status != 'cenceled' and obj.status == 'cenceled':
                self.return_funds(obj , obj.user)

        super().save_model(request,obj , form , change)

    def return_funds(self , obj , user):
        User.objects.filter(pk=user.pk).update(balance= user.balance + obj.amount)
