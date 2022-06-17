import pandas as pd

from datetime import datetime, date
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Value as V, Q
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection
from django.core.files.storage import default_storage
from django.http import HttpResponse

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
        workers = workers.annotate(search_str=Concat('names', V(' '), 'surnames')).filter(Q(search_str__icontains=search) | Q(document=search))

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
        'filter': search if search != False else '',
        'errors': request.session.get('errors', {})
    }

    request.session['errors'] = {}

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
@permission_required('accounts.add_worker', raise_exception=True)
def register_workers(request):
    file = request.FILES.get('file', False)

    dtype_dic = {'Número de documento': str, 'Número de celular' : str}

    if file:
        try:
            data = pd.read_excel(file, dtype = dtype_dic)
        except:
            try:
                data = pd.read_csv(file, dtype = dtype_dic)
            except:
                request.session['errors'] = {'title': "Error de lectura", 'body': "Ha ocurrido un error inesperado intentando leer el archivo"}
                redirect('accounts:list_workers')

    document_types = [x[0] for x in Worker.DOCUMENT_TYPES]

    file_header = ['Tipo de documento', 'Número de documento', 'Nombres', 'Apellidos', 'Email', 'Número de celular']

    for i, column in enumerate(data.columns):
        if column != file_header[i]:
            request.session['errors'] = {'title': "Error de lectura", 'body': "Ha ocurrido un error intentando leer el archivo.<br><br>Se encontró el valor de cabecera<br><strong>{}</strong><br>cuando se esperaba<br><strong>{}</strong>.<br><br>Por favor, revise que la cabecera del archivo esté compuesta por:<br><br>Tipo de documento<br>Número de documento<br>Nombres<br>Apellidos<br>Email<br>Número de celular<br><br>Asegúrese de respetar las mayúsculas.".format(column, file_header[i])}
            return redirect('accounts:list_workers')

    with transaction.atomic():
        for index, row in data.iterrows():
            line_number = index + 1

            try:
                document_type = row[0]
                document = row[1]
                names = row[2]
                surnames = row[3]
                email = row[4]
                phone_number = row[5]
            except:
                request.session['errors'] = {'title': "Error de lectura", 'body': "Ha ocurrido un error intentando leer la fila {}".format(line_number)}
                break

            if not document_type in document_types:
                request.session['errors'] = {'title': "Error de creación", 'body': "Ha ocurrido un error intentando leer la fila {}.<br>El tipo de documento <strong>{}</strong> no existe.<br><br>Tipos de documento disponibles:<br><br>dni, ruc, carnet de extranjero<br><br>Asegúrese de respetar las mayúsculas.".format(line_number, document_type)}
                break

            try:
                Worker.objects.get(document = document)
                request.session['errors'] = {'title': "Error de creación", 'body': "Ha ocurrido un error al intentar crear el colaborador de la fila {}. El colaborador con documento {} ya existe.".format(line_number, document)}
                break
            except:
                pass

            try:
                Worker.objects.get(email = email)
                request.session['errors'] = {'title': "Error de creación", 'body': "Ha ocurrido un error al intentar crear el colaborador de la fila {}. El colaborador con email {} ya existe.".format(line_number, email)}
                break
            except:
                pass

            try:
                worker = Worker(document_type = document_type, document = document, names = names, surnames = surnames, email = email, phone_number = phone_number, date_joined = datetime.now())
                worker.save()
            except Exception as e:
                request.session['errors'] = {'title': "Error de creación", 'body': "Ha ocurrido un error inesperado al intentar crear el colaborador de la fila {}".format(line_number)}
                transaction.set_rollback(True)
                break

    return redirect('accounts:list_workers')


@login_required
@permission_required('accounts.add_worker', raise_exception=True)
def download_worker_registry_excel_template(request):
    with default_storage.open('Formato.xlsx', 'rb') as f:
        response = HttpResponse(
            content = f,
            content_type = 'application/vnd.ms-excel',
            headers = {'Content-Disposition': 'attachment; filename="Formato.xlsx"'},
        )

    return response


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

    if worker.user is not None:
        if worker.user.is_superuser:
            request.session['errors'] = {'title': "Eliminación fallida", 'body': "Este usuario no puede ser eliminado"}
        elif worker.user.id == request.user.id:
            request.session['errors'] = {'title': "Eliminación fallida", 'body': "Se está intentando eliminar al mismo usuario de esta sesión"}
        return redirect('accounts:list_workers')

    worker.delete()
    return redirect('accounts:list_workers')
