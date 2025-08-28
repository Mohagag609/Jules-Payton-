"""
Brokers Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from accounting.models import Broker, BrokerDue
from accounting.forms import BrokerForm


@login_required
def broker_list(request):
    """List all brokers"""
    brokers = Broker.objects.all()
    return render(request, 'accounting/brokers/list.html', {
        'brokers': brokers
    })


@login_required
def broker_create(request):
    """Create a new broker"""
    if request.method == 'POST':
        form = BrokerForm(request.POST)
        if form.is_valid():
            broker = form.save()
            messages.success(request, f'تم إضافة السمسار {broker.name} بنجاح')
            return redirect('brokers:broker_detail', pk=broker.pk)
    else:
        form = BrokerForm()
    
    return render(request, 'accounting/brokers/form.html', {
        'form': form,
        'title': 'إضافة سمسار جديد'
    })


@login_required
def broker_detail(request, pk):
    """Broker detail view"""
    broker = get_object_or_404(Broker, pk=pk)
    dues = BrokerDue.objects.filter(broker_name=broker.name)
    
    return render(request, 'accounting/brokers/detail.html', {
        'broker': broker,
        'dues': dues
    })


@login_required
def broker_edit(request, pk):
    """Edit broker"""
    broker = get_object_or_404(Broker, pk=pk)
    
    if request.method == 'POST':
        form = BrokerForm(request.POST, instance=broker)
        if form.is_valid():
            broker = form.save()
            messages.success(request, 'تم تحديث بيانات السمسار بنجاح')
            return redirect('brokers:broker_detail', pk=broker.pk)
    else:
        form = BrokerForm(instance=broker)
    
    return render(request, 'accounting/brokers/form.html', {
        'form': form,
        'broker': broker,
        'title': f'تعديل السمسار: {broker.name}'
    })


@login_required
def broker_delete(request, pk):
    """Delete broker"""
    broker = get_object_or_404(Broker, pk=pk)
    
    if request.method == 'POST':
        broker.delete()
        messages.success(request, f'تم حذف السمسار بنجاح')
        return redirect('brokers:broker_list')
    
    return render(request, 'accounting/brokers/confirm_delete.html', {
        'broker': broker
    })