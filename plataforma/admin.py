from django.urls import path
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum
from .models import Aplicacao, Licenca, RenovacaoLicenca
from datetime import timedelta
from plataforma.views import painel_licencas_admin
from django.db.models import Count
from django.db.models.functions import TruncMonth


class RenovacaoLicencaInline(admin.TabularInline):
    model = RenovacaoLicenca
    extra = 0
    readonly_fields = ('data_renovacao',)

@admin.register(Licenca)
class LicencaAdmin(admin.ModelAdmin):
    list_display = ('aplicacao', 'data_compra', 'data_expiracao', 'quantidade', 'valor_total', 'dias_restantes')
    list_editable = ('quantidade',)
    list_filter = ('data_expiracao', 'aplicacao')
    search_fields = ('aplicacao__nome',)
    actions = ['renovar_licenca_1_ano']
    inlines = [RenovacaoLicencaInline]

    @admin.action(description="Renovar licença por mais 1 ano")
    def renovar_licenca_1_ano(self, request, queryset):
        for licenca in queryset:
            nova_data = licenca.data_expiracao + timedelta(days=365)
            RenovacaoLicenca.objects.create(
                licenca_original=licenca,
                nova_data_expiracao=nova_data,
                observacoes="Renovada automaticamente por 1 ano via admin"
            )
            licenca.data_expiracao = nova_data
            licenca.save()
        self.message_user(request, f"{queryset.count()} licença(s) renovada(s) com sucesso.")

# DASHBOARD VIEW
class CustomAdminSite(admin.AdminSite):
    site_header = "Gestão de Licenças"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/licencas/", self.admin_view(self.dashboard_licencas,), name="dashboard-licencas"),
        ]
        return custom_urls + urls

    def dashboard_licencas(self, request):
        hoje = timezone.now().date()
        trinta_dias = hoje + timedelta(days=30)

        total_ativas = Licenca.objects.filter(data_expiracao__gte=hoje).count()
        total_vencidas = Licenca.objects.filter(data_expiracao__lt=hoje).count()
        proximas_expirar = Licenca.objects.filter(data_expiracao__range=(hoje, trinta_dias))
        valor_total = Licenca.objects.all().aggregate(Sum('valor_total'))['valor_total__sum'] or 0

        context = dict(
            self.each_context(request),
            total_ativas=total_ativas,
            total_vencidas=total_vencidas,
            proximas_expirar=proximas_expirar,
            valor_total=valor_total,
        )
        agrupadas = (
            Licenca.objects.values('aplicacao__nome')
            .annotate(total=Sum('quantidade'))
            .order_by('-total')
        )
        nomes_aplicacoes = [x['aplicacao__nome'] for x in agrupadas]
        total_por_aplicacao = [x['total'] for x in agrupadas]
        context.update({
            'nomes_aplicacoes': nomes_aplicacoes,
            'total_por_aplicacao': total_por_aplicacao,
        })
        from django.db.models.functions import TruncMonth
        licencas_por_mes = (
            Licenca.objects
            .annotate(mes=TruncMonth('data_compra'))
            .values('mes')
            .annotate(total=Sum('quantidade'))
            .order_by('mes')
        )
        labels_meses = [x['mes'].strftime('%b/%Y') for x in licencas_por_mes]
        dados_meses = [x['total'] for x in licencas_por_mes]
        context.update({
            'labels_meses': labels_meses,
            'dados_meses': dados_meses,
        })
        return TemplateResponse(request, "admin/dashboard_licencas.html", context)
