from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('users/', views.users, name='users'),
    path('users/<int:user_id>/', views.user_details, name='user_details'),
    path('users/<int:user_id>/follows/', views.user_follows, name='user_follows'),
    path('photos/<int:user_id>/', views.photos, name='photos'),
    path('media/<str:media_id>/', views.media, name='media'),
    path('login/', auth_views.LoginView.as_view(template_name='pics/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='pics/logout.html'), name='logout'),
]

