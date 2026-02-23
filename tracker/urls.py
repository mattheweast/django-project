from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views  # Imports login_view, home from tracker/views.py

app_name = 'tracker'  # Registers the namespace

urlpatterns = [
    path('', views.login_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('categories/new/', views.category_create_view, name='category_create'),
    path('currency/update/', views.currency_update_view, name='currency_update'),
    path('items/new/', views.item_create_view, name='item_create'),
    path('items/<int:item_id>/', views.item_detail_view, name='item_detail'),
    path('items/<int:item_id>/edit/', views.item_edit_view, name='item_edit'),
    path('items/<int:item_id>/delete/', views.item_delete_view, name='item_delete'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='tracker/password_reset_form.html',
            email_template_name='tracker/password_reset_email.txt',
            subject_template_name='tracker/password_reset_subject.txt',
            success_url=reverse_lazy('tracker:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='tracker/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='tracker/password_reset_confirm.html',
            success_url=reverse_lazy('tracker:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='tracker/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path('home/', views.home, name='home'),
]