from django.utils import timezone
from django.shortcuts import render
from .models import Licenca
from django.db.models import Sum, Count

def painel_licencas_admin(request):
    hoje = timezone.now().date()
    proximas_expirar = Licenca.objects.filter(data_expiracao__lte=hoje + timezone.timedelta(days=30))
    total_ativas = Licenca.objects.filter(data_expiracao__gte=hoje).count()
    total_vencidas = Licenca.objects.filter(data_expiracao__lt=hoje).count()
    valor_total = Licenca.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0

    agrupadas = (
        Licenca.objects.values('aplicacao__nome')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    nomes_aplicacoes = [x['aplicacao__nome'] for x in agrupadas]
    total_por_aplicacao = [x['total'] for x in agrupadas]

    context = {
        'proximas_expirar': proximas_expirar,
        'total_ativas': total_ativas,
        'total_vencidas': total_vencidas,
        'valor_total': valor_total,
        'nomes_aplicacoes': nomes_aplicacoes,
        'total_por_aplicacao': total_por_aplicacao,
    }
    return render(request, 'admin/painel_licencas.html', context)
