"""
URL configuration for onlineChequeDeposit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from user import action
from teller import dashboard
from diagram import generate

urlpatterns = [
    path('teller/dashboard', dashboard.show),
    path('update/<int:id>', dashboard.update_details),
    path('teller/action/<int:id>/<str:action>', dashboard.change_status),
    path('', action.upload_cheque),
    path('diagram/show/<int:id>', generate.show),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
