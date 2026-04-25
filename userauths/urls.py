from django.urls import path
from userauths import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns=[
    path('editProfile/',views.editProfile,name="editProfile"),
    path('sign-up/', views.register, name="sign_up"),
    path('sign-in/', auth_views.LoginView.as_view(template_name="login.html", redirect_authenticated_user=True), name='sign-in'),
    path(
        'sign-out/',
        auth_views.LogoutView.as_view(next_page='sign-in'),
        name='sign-out'
    ),

]
