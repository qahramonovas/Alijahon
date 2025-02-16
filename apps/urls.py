from django.contrib import admin
from django.urls import path

from apps.views import HomeTemplateView, AuthFormView, UseDocumentTemplate, LogoutView, ProfileView, \
    ProfileEditFormView, AdminTemplateView,   \
     KangalarTemplateView, \
    ProductDetailView, get_districts, ChangePasswordFormView, CategoryListView, MahsulotlarListView, \
    wishlist_view, OrderSuccessTemplateView, MerketCategoryListView, ThreadListFormView, OrderListView, search_view, \
    ThreatStatistikaListView, WithDrawFormView, OperatorFormView, OrderDetailView , CompetitionListView

urlpatterns1 = [
    path('' , HomeTemplateView.as_view() , name = 'home'),
    path('category/<str:slug>' , CategoryListView.as_view() , name = 'category'),
    path('salesman/market/category/<str:slug>' , MerketCategoryListView.as_view() , name = 'market'),
    path('salesman/market/search' , search_view , name = 'search'),
    path('salesman/market/oqim' , ThreadListFormView.as_view() , name='thread'),
    path('statistika' , ThreatStatistikaListView.as_view() , name = 'statistika'),

    path('competition' , CompetitionListView.as_view() , name = 'competition'),
    path('tangalar' , KangalarTemplateView.as_view() , name = 'tangalar'),
    path('product-detail/<slug:slug>' , ProductDetailView.as_view() , name = 'product-detail'),
    path('oqim/<int:thread_id>' , ProductDetailView.as_view() , name='thread'),
    path('categoryy' , MahsulotlarListView.as_view() , name = 'categoryy'),
    path('get-districts/<int:region_id>/',get_districts, name='get_districts'),
    path('user/wishlist',wishlist_view, name='wishlist'),
]


urlpatterns3 = [
    path('order-success' , OrderSuccessTemplateView.as_view() , name='order-success'),
    path('order/list' , OrderListView.as_view() , name='order-list'),
    path('operator/page' , OperatorFormView.as_view() , name='operator'),
    path('operator/order<int:pk>' , OrderDetailView.as_view() , name='order-detail')
]

urlpatterns2 = [
    path('auth' , AuthFormView.as_view() , name = 'auth'),
    path('doc' , UseDocumentTemplate.as_view() , name = 'doc'),
    path('logout' , LogoutView.as_view() , name = 'logout'),
    path('profile' , ProfileView.as_view() , name = 'profile'),
    path('profile-edit' , ProfileEditFormView.as_view() , name = 'profile-edit'),
    path('adminn' , AdminTemplateView.as_view() , name = 'adminn'),
    path('change-password' , ChangePasswordFormView.as_view() , name = 'change-password'),
    path('withdraw' , WithDrawFormView.as_view() , name = 'withdraw'),


]

urlpatterns = urlpatterns1 + urlpatterns2 + urlpatterns3



