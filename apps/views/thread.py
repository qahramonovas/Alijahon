from datetime import timedelta
from time import timezone

from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic import ListView

from apps.forms import ThreadForm
from apps.models import Order, Thread


class ThreatStatistikaListView(ListView):
    queryset = Thread.objects.all()
    template_name = 'apps/salesman/statistika.html'
    context_object_name = "threads"

    def get_queryset(self):
        query = super().get_queryset()

        if period:=self.request.GET.get('period'):
            today = timezone.now().date()
            time_dict = {
                "today" : (timezone.now().date(), timezone.now().date()),
                "last_day" : (timezone.now().date()-timedelta(days=1), timezone.now().date()-timedelta(days=1)),
                "wekly": (timezone.now().date()-timedelta(days=7), today),
                "monthly":(timezone.now().date()-timedelta(days=30) , today),
            }
            choice = time_dict.get(period)
            query = query.filter(create_at__date__range=choice)


        query = query.filter(owner_id=self.request.user).select_related("product").annotate(
            new=Count('orders', filter=Q(orders__status=Order.StatusType.NEW)),
            ready_to_start=Count('orders', filter=Q(orders__status=Order.StatusType.READY_TO_START)),
            delivering=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERING)),
            delivered=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERED)),
            cancel_call=Count('orders', filter=Q(orders__status=Order.StatusType.CANCEl_CALL)),
            canceled=Count('orders', filter=Q(orders__status=Order.StatusType.CANCELED)),
            archived=Count('orders', filter=Q(orders__status=Order.StatusType.ARCHIVED)),
            visit_count=Count('visits')
        )
        return query

    def get_context_data(self, *args, **kwargs):
        query = self.get_queryset().aggregate(
            all_visit_count=Sum("visit_count"),
            all_new=Sum("new"),
            all_ready_to_start=Sum("ready_to_start"),
            all_delivering=Sum("delivering"),
            all_delivered=Sum("delivered"),
            all_cancel_call=Sum("cancel_call"),
            all_canceled=Sum("canceled"),
            all_archived=Sum("archived"),
        )
        context = super().get_context_data(*args , **kwargs)
        context.update(query)
        return context

class ThreadListFormView(FormView):
    form_class = ThreadForm
    template_name = 'apps/salesman/thread-list.html'
    success_url = reverse_lazy('thread')
    def form_valid(self, form):
        data = form.cleaned_data
        if data.get("discount_price") > data.get("product").selesman_price:
            messages.error(self.request , "Chegirma narxi hatto")
            return redirect('market' , 'all')
        data['owner'] = self.request.user
        Thread.objects.create(**data)
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['threads'] = self.request.user.threads.all()
        return context
    def form_invalid(self, form):
        # Ensure that an HttpResponse is returned
        return self.render_to_response(self.get_context_data(form=form))