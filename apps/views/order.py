from django.views.generic import ListView, TemplateView

from apps.models import Order


class OrderListView(ListView):
    queryset = Order.objects.select_related('district').all()
    template_name = 'apps/order/order-list.html'
    context_object_name = 'orders'


    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(user=self.request.user).all()
        return query


class OrderSuccessTemplateView(TemplateView):
    template_name = 'apps/order/success.html'