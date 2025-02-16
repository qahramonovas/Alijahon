import re

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import Form, CharField, BooleanField, IntegerField, ModelForm, SlugField, DateTimeField

from apps.models import Thread, WithDraw


class AuthForm(Form):
    phone_number = CharField(max_length=20)
    password = CharField(max_length=50)
    is_doc_read = BooleanField(required=False)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 5:
            raise ValidationError("You Password is Short !", code=400)
        return password

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")[4:]
        return re.sub(r'\D', '', phone_number)


class ChangePasswordForm(Form):
    old_password = CharField(max_length=50)
    new_password = CharField(max_length=50)
    confirm_password = CharField(max_length=50)

    def clean(self):
        clean_data = self.cleaned_data
        new_password = clean_data.get('new_password')
        confirm_password = clean_data.get('confirm_password')
        if confirm_password != new_password:
            raise ValidationError('Your Password is not Match')
        if len(new_password) < 5:
            raise ValidationError('Your Password id short')
        del clean_data['confirm_password']
        clean_data['new_password'] = make_password(clean_data['new_password'])
        return clean_data


class ProfileEditForm(Form):
    first_name = CharField(max_length=255, required=False)
    last_name = CharField(max_length=255, required=False)
    district = IntegerField(required=False)
    address = CharField(max_length=255, required=False)
    telegram_id = CharField(max_length=255, required=False)
    description = CharField(max_length=255, required=False)


    def clean_telegram_id(self):
        telegram_id = self.cleaned_data.get('telegram_id')
        if not telegram_id:
            return None
        return telegram_id


class OrderForm(Form):
    name = CharField(max_length=50)
    thread = CharField(max_length=255 , required=False)
    phone_number = CharField(max_length=50)
    product = CharField(max_length=255)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")[4:]
        return re.sub(r'\D', '', phone_number)


class ThreadForm(ModelForm):
    # owner = CharField(max_length=50 , required=False)
    class Meta:
        model = Thread
        exclude = "create_at" , "update_at" , "visit_count"


    def __init__(self, *args , **kwargs):
        super(ThreadForm , self).__init__(*args , **kwargs)
        self.fields['owner'].required=False


class WithDrawForm(ModelForm):
    class Meta:
        model = WithDraw
        exclude = 'create_at' , 'update_at' , 'user' , 'status'


class SearchForm(Form):
    product__category_id = CharField(max_length=255 , required=False)
    district_id = CharField(max_length=255,required=False)
    status = CharField(max_length=30 , required=False)


    def clean_product__category_id(self):
        category = self.cleaned_data.get('product__category_id')
        if category:
            return category

    def clean_district_id(self):
        district = self.cleaned_data.get('district_id')
        if district:
            return district

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if status:
            return status


    def clean(self):
        data = self.cleaned_data
        filter_data = {}
        for key , value in data.items():
            if value != None:
                filter_data.update({key:value})

        return filter_data


class OrderOperatorForm(Form):
    quantity = IntegerField()
    send_order_date = DateTimeField()
    district = IntegerField(required=False)
    status = CharField(max_length=50)
    comment_operator = CharField(max_length=255 , required=False)


    