from datetime import date
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import WorkerCreationForm, WorkerEditForm
from accounts.models import Worker
from accounts.utils import on_email_changed


def list_workers_page(request):
    workers = Worker.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(workers, 10)

    try:
        workers = paginator.page(page)
    except PageNotAnInteger:
        workers = paginator.page(1)
    except EmptyPage:
        workers = paginator.page(paginator.num_pages)

    context = {
        'workers': workers
    }

    return render(request, 'accounts/workers/list.html', context)


def get_worker_page(request, id):
    context = {
        'worker': get_object_or_404(Worker, id=id)
    }
    return render(request, 'accounts/workers/view.html', context)


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


def edit_worker_page(request, id):
    worker = get_object_or_404(Worker, id=id)
    if request.method == "POST":
        previous_email = worker.email
        worker_form = WorkerEditForm(
            request.POST, request.FILES, instance=worker)
        if worker_form.is_valid():
            worker_form.save()
            if on_email_changed(request, previous_email,
                                worker_form.cleaned_data['email']):
                messages.success(
                    request, 'Se envió al nuevo correo el link de confirmación de cuenta')
            return redirect('accounts:get_worker', id=id)
    else:
        worker_form = WorkerEditForm(instance=worker)
    context = {
        'worker': worker,
        'worker_form': worker_form,
    }
    return render(request, 'accounts/workers/edit.html', context)


def delete_worker_request(request, id):
    worker = get_object_or_404(Worker, id=id)
    worker.delete()
    return redirect('accounts:list_workers')
