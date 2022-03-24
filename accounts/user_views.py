import copy
import logging
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, get_user_model, login, logout,
                                 signals, update_session_auth_hash)
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.db import connection
from django.http.response import Http404, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import (is_safe_url, urlsafe_base64_decode,
                               urlsafe_base64_encode)
from django.views.generic import CreateView, FormView
from django_email_verification import send_email as send_verification_email

from accounts.forms import (LoginForm, MyProfileEditForm, RecoverPasswordForm,
                            UserCreationForm, UserEditForm)
from accounts.models import UserPasswordHistory
from accounts.utils import on_email_changed, send_custom_email

User = get_user_model()

if connection.introspection.table_names():
    admin_group, __ = Group.objects.get_or_create(name='admin')
    security_group, __ = Group.objects.get_or_create(name='security')


def logout_request(request):
    logout(request)
    return redirect("home")


# class LoginView(FormView):
#     form_class = LoginForm
#     success_url = "home"
#     template_name = "accounts/users/login.html"

#     def form_valid(self, form):
#         request = self.request

#         next_ = request.GET.get('next')
#         next_post = request.POST.get('next')
#         redirect_path = next_ or next_post or None

#         username = form.cleaned_data.get("username")
#         password = form.cleaned_data.get("password")

#         user = authenticate(
#             request=request, username=username, password=password)
#         print(user)
#         if user is not None:
#             login(request, user)
#             if is_safe_url(redirect_path, request.get_host()):
#                 return redirect(redirect_path)
#             else:
#                 return redirect("home")
#         return super(LoginView, self).form_invalid(form)

#     # def form_invalid(self, form):
#     #     request = self.request

#         # inform django-axes of failed login
#         # signals.user_login_failed.send(
#         #     sender=User,
#         #     request=request,
#         #     credentials={
#         #         'username': form.data.get('username'),
#         #     },
#         # )
#         # messages.error(
#         #     request, 'Realizó muchos intentos. Espere 30 minutos para intentarlo de nuevo.')


def recover_password_page(request):
    if request.method == "POST":
        form = RecoverPasswordForm(request.POST)
        if form.is_valid():
            # https://docs.djangoproject.com/en/3.2/topics/email/
            from_email = settings.EMAIL_FROM_ADDRESS
            to_email = form.cleaned_data['email']
            user = settings.EMAIL_QUERY(User, to_email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            send_mail(
                'Recuperación de Contraseña',
                'Entre a este enlace para cambiar su contraseña: http://127.0.0.1:8000' +
                reverse('accounts:reset_password', kwargs={
                        'uidb64': uid, 'token': token}),
                from_email,
                [to_email],
                fail_silently=False,
            )
            messages.success(
                request, 'Se envió la recuperación de contraseña a su correo')
            return redirect("accounts:login")
    else:
        form = RecoverPasswordForm
    context = {
        'form': form,
    }
    return render(request, 'accounts/users/recover_password.html', context)


def reset_password_page(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    try:
        user = User._default_manager.get(pk=uid)
    except:
        return render(request, 'accounts/reset_password.html', {'success': False})
    if default_token_generator.check_token(user, token) == False:
        return HttpResponse('Token expirado')
    if request.method == "POST":
        password_form = SetPasswordForm(user, request.POST)
        if password_form.is_valid():
            user_saved = password_form.save()
            update_session_auth_hash(request, user_saved)
            messages.success(
                request, 'Se actualizó la contraseña correctamente!')
            return redirect('accounts:login')
    else:
        password_form = SetPasswordForm(user=user)
    context = {
        'password_form': password_form,
        'success': True
    }
    return render(request, 'accounts/reset_password.html', context)


def activate_account_after_changing_email_page(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    try:
        user = User._default_manager.get(pk=uid)
        user.is_active = True
        user.save()
    except:
        return render(request, 'accounts/account_confirmation.html', {'success': False})
    if default_token_generator.check_token(user, token) == False:
        return HttpResponse('Token expirado')
    context = {
        'user': user,
        'success': True
    }
    return render(request, 'accounts/account_confirmation.html', context)


def register_user_page(request):
    if request.method == "POST":
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(False)
            user.worker = user_form.cleaned_data['worker']
            send_verification_email(user)
            if user.pk != None:
                if user_form.cleaned_data['role'] == "admin":
                    admin_group.user_set.add(user)
                    pass
                elif user_form.cleaned_data['role'] == "security":
                    security_group.user_set.add(user)
                    pass
            return redirect("accounts:list_users")
    else:
        user_form = UserCreationForm
    context = {
        'user_form': user_form,
    }
    return render(request, 'accounts/users/register.html', context)


class RegisterAdminView(CreateView):
    form_class = UserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")


def list_users_page(request):
    context = {
        'users': User.objects.all(),
    }
    return render(request, 'accounts/users/list.html', context)


def get_user_page(request, id):
    context = {
        'user': get_object_or_404(User, id=id),
    }
    return render(request, 'accounts/users/view.html', context)


def edit_user_page(request, id):
    user = get_object_or_404(User, id=id)
    password_form = SetPasswordForm(user=user)
    if request.method == "POST":
        user_form = UserEditForm(user.worker,
                                 request.POST, request.FILES, instance=user)
        if 'user-form' in request.POST:
            old_role = user.role
            if user_form.is_valid():
                user = user_form.save(False)
                if user_form.cleaned_data['worker']:
                    user.worker = user_form.cleaned_data['worker']
                user.save()
                if user_form.cleaned_data['role'] == "admin":
                    security_group.user_set.remove(user)
                    admin_group.user_set.add(user)
                elif user_form.cleaned_data['role'] == "security":
                    admin_group.user_set.remove(user)
                    security_group.user_set.add(user)
                if old_role != user.role:
                    to_email, title, content = user.worker.email, "Rol Actualizado", "Su rol de usuario ha sido actualizado a " + user.role
                    if send_custom_email(to_email, title, content):
                        messages.success(
                            request, 'Se envió un correo al usuario')
                messages.success(
                    request, 'Se actualizó las configuraciones del usuario')
                return redirect('accounts:get_user', id=id)
        if 'password-form' in request.POST:
            password_form = SetPasswordForm(user, request.POST)
            if password_form.is_valid():
                user_saved = password_form.save()
                update_session_auth_hash(request, user_saved)
                messages.success(
                    request, 'Se actualizó la contraseña correctamente!')
                to_email, title, content = user_saved.worker.email, "Correo Actualizado", "Se actualizó la contraseña de su cuenta"
                if send_custom_email(to_email, title, content):
                    messages.success(
                        request, 'Se envió un correo al usuario')
                else:
                    messages.warning(
                        request, 'Hubo un fallo en el envio de correo')
                return redirect('accounts:get_user', id=id)
    else:
        user_form = UserEditForm(instance=user, initial={
                                 'worker': user.worker, 'role': user.role}, worker=user.worker)
    context = {
        'user': user,
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'accounts/users/edit.html', context)


def my_profile_page(request):
    user = request.user
    profile_form = MyProfileEditForm(instance=user.worker)
    password_form = SetPasswordForm(user=user)
    if request.method == "POST":
        if 'profile-form' in request.POST:
            previous_email = user.worker.email
            profile_form = MyProfileEditForm(
                request.POST, request.FILES, instance=user.worker)
            if profile_form.is_valid():
                profile_form.save()
                if on_email_changed(request, previous_email, profile_form.cleaned_data['email']):
                    messages.success(
                        request, 'Se envió a su correo el link de confirmación de su cuenta')
                    return redirect("accounts:logout")
                messages.success(
                    request, 'Se actualizó los datos correctamente!')
                return redirect('accounts:my_profile')
        if 'password-form' in request.POST:
            password_form = SetPasswordForm(user, request.POST)
            if password_form.is_valid():
                user_saved = password_form.save()
                update_session_auth_hash(request, user_saved)
                messages.success(
                    request, 'Se actualizó la contraseña correctamente!')
                return redirect('accounts:my_profile')
    context = {
        'user': user,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'accounts/users/my_profile.html', context)


def delete_user_request(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('accounts:list_users')


def block_user_request(request, action, id):
    user = get_object_or_404(User, id=id)
    user.is_blocked = True if action == 'true' else False
    user.save()
    return redirect('accounts:list_users')
