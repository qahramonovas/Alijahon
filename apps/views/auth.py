from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, ListView

from apps.forms import AuthForm, ProfileEditForm, ChangePasswordForm, WithDrawForm
from apps.models import User, Region, District, Wishlist, WithDraw


class AuthFormView(FormView):
    form_class = AuthForm
    template_name = 'apps/user/auth.html'
    success_url = reverse_lazy('profile-edit')  # O'zingizning yo'naltirishingizni kiriting

    def form_valid(self, form):
        clean_data = form.cleaned_data
        user = User.objects.filter(phone_number=clean_data.get('phone_number')).first()

        if not user:
            # Agar foydalanuvchi topilmasa, yangi foydalanuvchi yaratiladi
            clean_data['password'] = make_password(clean_data.get('password'))
            obj, is_created = User.objects.get_or_create(phone_number=clean_data.get('phone_number'),
                                                         defaults=clean_data)
            if is_created:
                login(self.request, obj)  # Yangi foydalanuvchini login qilish
                return super().form_valid(form)
            else:
                messages.error(self.request, "User creation failed.")
                return redirect('auth')  # Noto'g'ri urinishlarda qayta yo'naltirish

        else:
            # Foydalanuvchi mavjud bo'lsa, parolni tekshirish
            is_equal = check_password(clean_data.get('password'), user.password)
            if is_equal:
                login(self.request, user)  # Mavjud foydalanuvchini login qilish
                return super().form_valid(form)
            else:
                messages.error(self.request, "Your password does not match!")
                return redirect('auth')  # Xato bo'lganda yo'naltirish

    def form_invalid(self, form):
        messages.error(self.request, "\n".join([i[0] for i in form.errors.values()]))
        return super().form_invalid(form)


class UseDocumentTemplate(TemplateView):
    template_name = 'apps/product_and_anothers/documents.html'

class LogoutView(View):
    def get(self, request):
        logout(self.request)
        return redirect('home')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/user/profile.html'



# shu joyi ishlamayapti
class ChangePasswordFormView(FormView):
    form_class = ChangePasswordForm
    template_name = 'apps/user/profil-edit.html'
    success_url = reverse_lazy('profile-edit')

    # Shu joyi ishlamidi
    def form_valid(self, form):
        user = self.request.user
        password = form.cleaned_data.get('password')
        new_password = form.cleaned_data.get('new_password')
        if check_password(password, user.password):
            messages.error(self.request, "Old Password incorrect")
            return super().form_valid(form)
        messages.success(self.request, "Success change your password")

        user: User = User.objects.filter(pk=user.pk).first()
        user.password = new_password
        user.save()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "\n".join([i[0] for i in form.errors.values()]))
        return super().form_invalid(form)


class ProfileEditFormView(FormView):
    form_class = ProfileEditForm
    template_name = "apps/user/profil-edit.html"
    success_url = reverse_lazy('profile-edit')

    def get_context_data(self, **kwargs):
        user: User = self.request.user
        data = super().get_context_data(**kwargs)

        # Foydalanuvchi tumani va viloyati borligini tekshirish
        if user.district:
            district = District.objects.filter(pk=user.district.id).first()
            if district:
                data['district_region'] = district.region.pk  # Viloyat ID
                data['district'] = district  # Tuman
        else:
            data['district_region'] = None
            data['district'] = None

        data['regions'] = Region.objects.all()
        return data

    def form_valid(self, form):
        user = self.request.user
        User.objects.filter(pk=user.pk).update(**form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form)



def wishlist_view(request):
    if request.POST:
        user = request.user

        product_id = request.POST.get('product_id')
        obj , create = Wishlist.objects.get_or_create(user_id=user.id , product_id=product_id)
        if not create:
            obj.delete()
        return JsonResponse({"response" : create})
    else:
        context = {
            'wishlists' : request.user.wishlists.all()
        }
        return render(request , 'apps/user/wishlist.html' ,context)


#
class WithDrawFormView(ListView , FormView):
    queryset = WithDraw.objects.all()
    context_object_name = 'withdraws'
    form_class = WithDrawForm
    template_name = 'apps/user/withdraw.html'
    success_url = reverse_lazy('withdraw')

    def form_valid(self, form):
        form_data = form.cleaned_data
        user:User = self.request.user
        if form_data.get('type') == "money" and form_data.get("amount") > user.balance:
            messages.error(self.request , "Your money is not enough")
            return redirect('withdraw')
        elif form_data.get("type") == "coin" and form_data.get("amount") > user.coin:
            messages.error(self.request, "Your coins is not enough")
            return redirect('withdraw')
        if form_data.get('type') == "money":
            user.balance -= form_data.get('amount')
        else:
            user.coin -= form_data.get('amount')

        user.save()
        form = form.save(commit=False)
        form.user = user
        form.save()
        return super().form_valid(form)


    def get_queryset(self):
        query = super().get_queryset()
        return query.filter(user=self.request.user)

    def form_invalid(self, form):
       print(form)

    def get_context_data(self,  *args, **kwargs):
        context = super().get_context_data(*args , **kwargs)
        context.update(self.get_queryset().filter(status = WithDraw.WithDrawStatus.COMPLETED.value).aggregate(completed_pay=Sum('amount')))
        return context






