from django.contrib import messages

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, DetailView

from apps.forms import SearchForm, OrderOperatorForm
from apps.models import Order, Region, Category


class OperatorFormView(ListView , FormView):
    form_class = SearchForm
    queryset = Order.objects.all()
    template_name = 'apps/operator/operator-page.html'
    context_object_name = 'orders'

    def get_queryset(self):
        status = self.request.GET.get('status')
        query = super().get_queryset()
        if status:
            query = query.filter(status=status)
        else:
            query = query.filter(status='new')

        return query

    def get_context_data(self, *args, **kwargs):
        context = {}
        if not kwargs.get('form'):
            context = super().get_context_data(*args , **kwargs)
        context['regions'] = Region.objects.all()
        context['status'] = Order.StatusType
        context['categories'] = Category.objects.all()
        if kwargs.get('form'):
            context['orders'] = Order.objects.filter(**kwargs.get("form").cleaned_data)
        return context

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request , 'apps/operator/operator-page.html' , context)



class OrderDetailView(DetailView , FormView):
    form_class = OrderOperatorForm
    queryset = Order.objects.all()
    success_url = reverse_lazy('operator')
    pk_url_kwarg = 'pk'
    template_name = 'apps/operator/order-change.html'
    context_object_name = 'order'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        return context

    def form_valid(self, form):
        order = self.get_object()
        query = Order.objects.filter(pk=order.pk)
        obj = query.first()
        status = form.cleaned_data.get('status')
        if status == Order.StatusType.DELIVERED.value and obj.thread:
            thread = obj.thread
            owner = thread.owner
            transfer_pay = obj.product.selesman_price - thread.discount_price
            owner.balance += transfer_pay
            owner.save()
        query.update(**form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, "Form Invalid")
        return redirect('order-detail', pk=self.kwargs.get('pk'))








