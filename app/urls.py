from django.contrib import admin
from django.urls import path, include
from plataforma.admin import CustomAdminSite, LicencaAdmin
from plataforma.models import Aplicacao, Licenca, RenovacaoLicenca

admin_site = CustomAdminSite()

admin_site.register(Aplicacao)
admin_site.register(Licenca, LicencaAdmin)
admin_site.register(RenovacaoLicenca)

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('plataforma.urls'))
]
