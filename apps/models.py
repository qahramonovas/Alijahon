from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.models import ContentType
from django.db.models import CharField, Model, ForeignKey, CASCADE, BigIntegerField, TextField, BooleanField, \
    OneToOneField, DecimalField, ImageField, SlugField, PositiveIntegerField, TextChoices, DateTimeField, SET_NULL, \
    DateField
from django.apps import apps
from django.urls import reverse
from django.utils.text import slugify


class DateTimeBaseModel(Model):
    create_at = DateTimeField(auto_now_add=True)
    update_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, email, password, **extra_fields):

        if not phone_number:
            raise ValueError("The given phone_number must be set")
        email = self.normalize_email(email)

        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        phone_number = GlobalUserModel.normalize_username(phone_number)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, email, password, **extra_fields)

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", 'admin')


        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, email, password, **extra_fields)


class User(AbstractUser):
    class RoleType(TextChoices):
        ADMIN = 'admin' , "Admin"
        USER = "user" , "User"
        OPERATOR = "operator" , "Operator"
        DELIVER = "deliver" , "Deliver"
    role = CharField(max_length=50 , choices=RoleType.choices , default=RoleType.USER)
    phone_number = CharField(max_length=9 , unique=True , blank=True)
    address = CharField(max_length=255 , null=True , blank=True)
    telegram_id = BigIntegerField(null=True , blank=True)
    description = TextField(null=True , blank=True)
    coin = PositiveIntegerField(default=0)
    objects = CustomUserManager()
    USERNAME_FIELD = "phone_number"
    username = None
    is_doc_read = BooleanField(default=False , blank=True)
    district = OneToOneField('apps.District' , CASCADE , null=True , blank=True)
    image = ImageField(upload_to="user/")
    balance = DecimalField(max_digits=12 , decimal_places=0 , default=0)

    @property
    def self_wishlist(self):
        return self.wishlists.all().values_list('product_id', flat=True)


class Region(Model):
    name = CharField(max_length=50)


class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey('apps.Region' , CASCADE,  related_name='district')


class BaseSlug(Model):
    name = CharField(max_length=255)
    slug = SlugField(max_length=255 , unique=True , db_index=True)

    class Meta:
        abstract = True

    def save(self , *args , **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique = self.slug
            num = 1
            while Category.objects.filter(
                    slug=unique).exists():  # todo Category orniga self qilib qoysak ozini olib ketadi
                unique = f'{self.slug}-{num}'
                num += 1
            self.slug = unique
        return super().save(*args , **kwargs)


class Category(BaseSlug):
    image = ImageField(upload_to="product/")

    def __str__(self):
        return self.name


class Product(BaseSlug , DateTimeBaseModel):
    description = TextField()
    image = ImageField(upload_to='product/')
    quantity = PositiveIntegerField(default=1)
    discount = DecimalField(max_digits=12 , decimal_places=2 , default=0)
    price = DecimalField(max_digits=19 , decimal_places=2)
    selesman_price = DecimalField(max_digits=12 , decimal_places=0)
    category = ForeignKey('apps.Category', CASCADE, to_field='slug', related_name='category')

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})


    @property
    def discount_price(self):
        return self.price * (100-self.discount)/100


    def __str__(self):
        return self.name


class Wishlist(DateTimeBaseModel):
    user = ForeignKey(User, on_delete=CASCADE, related_name='wishlists')
    product = ForeignKey(Product, on_delete=CASCADE, related_name='wishlists')

    class Meta:
        unique_together = ('user', 'product')


class Order(DateTimeBaseModel):
    class StatusType(TextChoices):
        NEW = 'new' , 'New'
        READY_TO_START = 'ready to start' , 'Ready to start'
        DELIVERING = 'delivering' , 'Delivering'
        DELIVERED = 'delivered' , 'Delivered'
        CANCEl_CALL = 'cencel call' , 'Cancel call'
        CANCELED = 'canceled' , 'Canceled'
        ARCHIVED = 'archived' , 'Archived'
        HOLD = 'hold' , 'Hold'
    comment_operator = TextField()
    send_order_date = DateTimeField(null=True , blank=True)
    quantity = PositiveIntegerField(default=1)
    product = ForeignKey('apps.Product' , CASCADE , to_field='slug',  related_name='orders')
    user = ForeignKey('apps.User' , CASCADE , related_name='orders')
    status = CharField(max_length=50 , choices=StatusType , default=StatusType.NEW)
    thread = ForeignKey('apps.Thread' , SET_NULL , null=True , blank=True , related_name='orders')
    phone_number = CharField(max_length=25)
    name = CharField(max_length=50)
    all_amount = DecimalField(max_digits=9 , decimal_places=2)
    district = ForeignKey('apps.District' , SET_NULL , null=True , blank=True , related_name='orders')
    address = CharField(max_length=255)


    @property
    def discount_price(self):
        amount = self.product.discount_price
        if self.thread:
            amount -= self.thread.discount_price
        return amount



class AdminSite(Model):
    delivering_price = DecimalField(max_digits=9 , decimal_places=2)
    competition_photo = ImageField(upload_to='site_settings')
    competition_start = DateField(null=True , blank=True)
    competition_end = DateField(null=True , blank=True)
    message = TextField(null=True , blank=True)


class Thread(DateTimeBaseModel):
    owner = ForeignKey('apps.User' , CASCADE , related_name='threads')
    product = ForeignKey('apps.Product' , CASCADE , related_name='threads')
    title = CharField(max_length=100)
    discount_price = DecimalField(max_digits=9 , decimal_places=0)



class Visit(DateTimeBaseModel):
    thread = ForeignKey('apps.Thread' , CASCADE , related_name='visits')


class WithDraw(DateTimeBaseModel):
    class WithDrawStatus(TextChoices):
        UNDAER_REVIEW = "under review" , "Under review"
        COMPLETED = "completed" , "Completed"
        CANCELED = "cenceled" , "Cenceled"
    class CashType(TextChoices):
        MONEY = "money" , "Money"
        COIN = "coin" , "Coin"
    card_number = CharField(max_length=16)
    amount = DecimalField(max_digits=12 , decimal_places=0)
    user = ForeignKey('apps.User' , SET_NULL , null=True , blank=True , related_name='withdraws')
    status = CharField(max_length=30 , choices=WithDrawStatus.choices , default=WithDrawStatus.UNDAER_REVIEW)
    type = CharField(max_length=255 ,choices=CashType.choices , default=CashType.MONEY)
    message = TextField(null=True , blank=True)
    image = ImageField(upload_to='withdraws/' , null=True , blank=True)

    def __str__(self):
        return f"{self.user.phone_number}"

    def image_url(self):
        if self.image:
            return self.image.url
        return ""





