from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('users/', views.users, name='users'),
    path('users/<str:user_identifier>/', views.user_details, name='user_details'),
    path('users/<int:user_id>/follows/', views.user_follows, name='user_follows'),
    path('users/<int:user_id>/follow/', views.follow, name='follow'),
    path('users/<int:user_id>/unfollow/', views.unfollow, name='unfollow'),
    path('photos/<int:photo_id>/', views.photo_details, name='photo_details'),
    path('photos/', views.post, name='post_photo'),
    path('photos/<int:photo_id>/like/', views.like, name='like'),
    path('photos/<int:photo_id>/unlike/', views.unlike, name='unlike'),
    path('photos/<int:photo_id>/likecount/', views.like_count, name='likecount'),
    path('photos/<int:photo_id>/comments/', views.comments, name='comments'),
    path('media/<str:media_id>/', views.media, name='media'),
    path('feed/', views.feed, name='feed'),
    path('login/', auth_views.LoginView.as_view(template_name='pics/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='pics/logout.html'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('<str:username>/', views.user_view, name='user_view'),
    path('health/', views.health, name='health'),
]

