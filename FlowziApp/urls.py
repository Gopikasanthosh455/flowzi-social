from django.urls import path
from FlowziApp import views

urlpatterns = [
    path('', views.home_page, name="home_page"),
    path('newpost/', views.NewPost, name='newpost'),
    path('edit/<uuid:post_id>/', views.edit_post, name='edit_post'),
    path('delete/<uuid:post_id>/', views.delete_post, name='delete_post'),
    path('<uuid:post_id>/like/', views.like, name="like"),
    path('<uuid:post_id>/post-detail/', views.PostDetail, name="post-detail"),
    path('<uuid:post_id>/favourite/', views.favourite, name="post-favourite"),
]
