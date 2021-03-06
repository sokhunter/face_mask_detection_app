from django.contrib.auth import views
from django.urls import include, path
from accounts.forms import LoginForm

from accounts.user_views import (block_user_request, delete_user_request,
                                 edit_user_page, get_user_page,
                                 list_users_page, logout_request,
                                 my_profile_page, recover_password_page,
                                 register_user_page, reset_password_page,
                                 camera_selector)
from accounts.worker_views import (delete_worker_request, edit_worker_page,
                                   get_worker_page, list_workers_page,
                                   register_worker_page, register_workers,
                                   download_worker_registry_excel_template)

app_name = 'accounts'
urlpatterns = [
    path('login/', views.LoginView.as_view(template_name="accounts/users/login.html",
                                           authentication_form=LoginForm,
                                           success_url="home"
                                           ), name='login'),
    path('login_security/', views.LoginView.as_view(template_name="accounts/users/login_security.html",
                                           authentication_form=LoginForm), name='login_security'),
    path('camera_selector/', camera_selector, name='camera_selector'),
    path('logout/', logout_request, name='logout'),

    path('recover/', recover_password_page, name='recover'),
    path('reset/<uidb64>/<token>/', reset_password_page, name='reset_password'),
    path('my_profile/', my_profile_page, name='my_profile'),

    path('workers/', list_workers_page, name='list_workers'),
    path('workers/view/<int:id>/', get_worker_page, name='get_worker'),
    path('workers/register/', register_worker_page, name='register_worker'),
    path('workers/register_multiple/', register_workers, name='register_workers'),
    path('workers/register_multiple_template/', download_worker_registry_excel_template, name='multiple_register_template'),
    path('workers/edit/<int:id>/', edit_worker_page, name='edit_worker'),
    path('workers/delete/<int:id>/', delete_worker_request, name='delete_worker'),

    path('users/', list_users_page, name='list_users'),
    path('users/view/<int:id>/', get_user_page, name='get_user'),
    path('users/register/', register_user_page, name='register_user'),
    path('users/edit/<int:id>/', edit_user_page, name='edit_user'),
    path('users/delete/<int:id>/', delete_user_request, name='delete_user'),
    path('users/block/<str:action>/<int:id>/', block_user_request, name='block_user'),
]
