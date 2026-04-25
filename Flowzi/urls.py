from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import FlowziApp.urls
import userauths.urls
import directMessage.urls
from userauths.views import UserProfile, follow

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(FlowziApp.urls)),
    path('users/', include(userauths.urls)),
    path('messages/', include(directMessage.urls)),
    path('<username>/saved/', UserProfile, name="favourite"),
    path('<username>/profile/', UserProfile, name="profile"),
    path('<username>/follow/<option>/', follow, name="follow"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
