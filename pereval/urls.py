"""
URL configuration for pereval project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from mountain_pass.views import PerevalCreateView, PerevalDetailUpdateView, PerevalListByEmailView, index

schema_view = get_schema_view(
    openapi.Info(
        title="API Pereval",
        default_version='v1',
        description="Документация API для работы с данными перевалов",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', index, name='home'),  # Главная страница
    path('admin/', admin.site.urls),

    # POST: создание записи
    path('api/v1/submitData', PerevalCreateView.as_view(), name='submit_data'),

    # GET: получение записи по id; # PATCH: редактирование записи по id
    path('api/v1/submitData/<int:id>', PerevalDetailUpdateView.as_view(), name='pereval_detail_update'),

    # GET: получение записей по email пользователя (...submitData/?user__email=<email>)
    path('api/v1/submitData/', PerevalListByEmailView.as_view(), name='submit_data_by_email'),

    # Пути для Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
