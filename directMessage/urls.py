from django.urls import path
from directMessage import views

urlpatterns = [
    path('inbox/', views.inbox, name="inbox"),
    path('directs/<str:username>/', views.Directs, name="directs"),
    path('send/', views.SendMessages, name="send-message"),
    path('new/', views.UserSearch, name="user-search"),
    path('new/<str:username>/', views.NewMessage, name="new-message"),
]
