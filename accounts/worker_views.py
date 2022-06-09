from datetime import date
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import connection

from accounts.forms import WorkerCreationForm, WorkerEditForm
from accounts.models import Worker

if connection.introspection.table_names():
    admin_group, __ = Group.objects.get_or_create(name='admin')
    security_group, __ = Group.objects.get_or_create(name='security')

    content_type = ContentType.objects.get_for_model(Worker)
    worker_permissions = Permission.objects.filter(content_type=content_type)

    for perm in worker_permissions:
        admin_group.permissions.add(perm)


@login_required
@permission_required('accounts.view_worker', raise_exception=True)
def list_workers_page(request):
    search = request.GET.get('search', False)

    workers = Worker.objects.all()

    if search:
        workers = workers.annotate(search_str=Concat('names', V(' '), 'surnames')).filter(search_str__icontains=search)

    page = request.GET.get('page', 1)
    paginator = Paginator(workers, 10)

    try:
        workers = paginator.page(page)
    except PageNotAnInteger:
        workers = paginator.page(1)
    except EmptyPage:
        workers = paginator.page(paginator.num_pages)

    context = {
        'workers': workers,
        'filter': search if search != False else ''
    }

    return render(request, 'accounts/workers/list.html', context)


@login_required
@permission_required('accounts.view_worker', raise_exception=True)
def get_worker_page(request, id):
    context = {
        'worker': get_object_or_404(Worker, id=id)
    }
    return render(request, 'accounts/workers/view.html', context)


@login_required
@permission_required('accounts.add_worker', raise_exception=True)
def register_worker_page(request):
    if request.method == "POST":
        worker_form = WorkerCreationForm(request.POST, request.FILES)
        if worker_form.is_valid():
            worker = worker_form.save(False)
            worker.date_joined = date.today()
            worker.save()

            return redirect("accounts:list_workers")
    else:
        worker_form = WorkerCreationForm
    context = {
        'worker_form': worker_form,
    }
    return render(request, 'accounts/workers/register.html', context)


@login_required
@permission_required('accounts.change_worker', raise_exception=True)
def edit_worker_page(request, id):
    worker = get_object_or_404(Worker, id=id)
    if request.method == "POST":
        worker_form = WorkerEditForm(
            request.POST, request.FILES, instance=worker)
        if worker_form.is_valid():
            worker_form.save()
            return redirect('accounts:get_worker', id=id)
    else:
        worker_form = WorkerEditForm(instance=worker)
    context = {
        'worker': worker,
        'worker_form': worker_form,
    }
    return render(request, 'accounts/workers/edit.html', context)


@login_required
@permission_required('accounts.delete_worker', raise_exception=True)
def delete_worker_request(request, id):
    worker = get_object_or_404(Worker, id=id)
    worker.delete()
    return redirect('accounts:list_workers')
