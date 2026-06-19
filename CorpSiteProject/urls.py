"""
URL configuration for CorpSiteProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from module_project import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_output,  name='Home'),
    path('Departments/', views.departments_info,  name='Departments'),
    path('Profile/', views.profile_info,  name='Profile'),
    path('Docs/', views.documents_info, name="Docs"),
    path('Events/', views.event, name="Events"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', LoginView.as_view(template_name='module_project/login.html'), name='login'),
    path('event/<int:event_id>/', views.event_detail, name='event'),
    path('create_news/', views.news_create, name='news_create'),
    path('create_events/', views.event_create, name='event_create'),
    path('workplace/<int:workplace_id>/employees/', views.Deppersonal, name='personal'),
    path('event/<int:event_id>/photos/upload/', views.event_photos_upload, name='event_photos_upload'),
    path('api/photo/<int:photo_id>/delete/', views.photo_delete_ajax, name='photo_delete_ajax'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
]

urlpatterns += [
    path("gallery-handler/", include("galleryfield.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
