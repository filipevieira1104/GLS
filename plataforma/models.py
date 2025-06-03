from django.db import models
from django.utils import timezone
from datetime import timedelta

class Aplicacao(models.Model):
    nome = models.CharField(max_length=100)
    fornecedor = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Aplicação'
        verbose_name_plural = 'Aplicações'

    def __str__(self):
        return self.nome
    
class Licenca(models.Model):
    aplicacao = models.ForeignKey(Aplicacao, on_delete=models.CASCADE, related_name='licencas')
    data_compra = models.DateField()
    data_expiracao = models.DateField()
    quantidade = models.PositiveIntegerField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Licença'
        verbose_name_plural = 'Licenças'

    @property
    def valor_unitario(self):
        return self.valor_total / self.quantidade if self.quantidade else 0

    @property
    def dias_restantes(self):
        return (self.data_expiracao - timezone.now().date()).days
    
    def __str__(self):
        return f'{self.aplicacao.nome} - {self.quantidade} licenças'

class RenovacaoLicenca(models.Model):
    licenca_original = models.ForeignKey(Licenca, on_delete=models.CASCADE, related_name='renovacoes')
    data_renovacao = models.DateField(auto_now_add=True)
    nova_data_expiracao = models.DateField()
    observacoes = models.TextField(blank=True)   

    class Meta:
        verbose_name = 'Renovação de Licença'
        verbose_name_plural = 'Renovações de Licença' 

    def __str__(self):
        return f"Renovação {self.licenca_original.aplicacao.nome} em {self.data_renovacao}"   