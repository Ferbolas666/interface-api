from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Cliente, Conexao, Permissao,
    SecUser, SecGroup, SecUsersGroups,
    SecGroupApp, SecSettings,
    ProjetoAplicacao, ProjetoAplicacaoDetalhe,
    ClienteProjetoAplicacao, ProjetoAplicacaoSubprojeto
)

# ===========================
# Form customizado para Cliente com seleção múltipla de Projetos
# ===========================
class ClienteProjetosForm(forms.ModelForm):
    projetos = forms.ModelMultipleChoiceField(
        queryset=ProjetoAplicacao.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple  # Pode trocar para outro widget se quiser
    )

    class Meta:
        model = Cliente
        fields = ['nome', 'cnpj', 'email', 'ativo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['projetos'].initial = ProjetoAplicacao.objects.filter(
                clientes_vinculados__cliente=self.instance
            )

    def save(self, commit=True):
        cliente = super().save(commit)
        selecionados = self.cleaned_data['projetos']

        # Remove vínculos que não estão mais selecionados
        ClienteProjetoAplicacao.objects.filter(cliente=cliente).exclude(projeto__in=selecionados).delete()

        # Adiciona vínculos novos
        for projeto in selecionados:
            ClienteProjetoAplicacao.objects.get_or_create(cliente=cliente, projeto=projeto)

        return cliente


# ===========================
# ClienteAdmin com form customizado
# ===========================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    form = ClienteProjetosForm
    list_display = ('nome', 'cnpj', 'email', 'ativo')

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        relatorio_url = reverse('relatorio_clientes')
        extra_context['custom_button'] = format_html(
            '<a class="btn btn-info" href="{}" style="margin-left:10px;">📄 Relatório de Clientes</a>',
            relatorio_url
        )
        return super().changelist_view(request, extra_context=extra_context)


# ===========================
# Inline de Detalhes (Aplicações por Cliente+Projeto)
# ===========================
class ProjetoAplicacaoDetalheInline(admin.TabularInline):
    model = ProjetoAplicacaoDetalhe
    extra = 1


# ===========================
# Admin de ClienteProjetoAplicacao
# ===========================
@admin.register(ClienteProjetoAplicacao)
class ClienteProjetoAplicacaoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'projeto', 'observacao', 'ativo')
    list_filter = ('cliente', 'projeto', 'ativo')
    search_fields = ('cliente__nome', 'projeto__nome_projeto')
    inlines = [ProjetoAplicacaoDetalheInline]


# ===========================
# Admin do Catálogo de Projetos (sem inline)
# ===========================
@admin.register(ProjetoAplicacao)
class ProjetoAplicacaoAdmin(admin.ModelAdmin):
    list_display = ('nome_projeto', 'nome_aplicacao')
    search_fields = ('nome_projeto', 'nome_aplicacao')

@admin.register(ProjetoAplicacaoSubprojeto)
class ProjetoAplicacaoSubprojetoAdmin(admin.ModelAdmin):
    list_display = ('nome_aplicacao', 'cod_relacao', 'nome_demonstracao', 'ativo')
    list_filter = ('cod_relacao', 'ativo')
    search_fields = ('nome_aplicacao', 'nome_demonstracao')

# ===========================
# Registros simples
# ===========================
admin.site.register(Conexao)
admin.site.register(Permissao)


# ===========================
# Proxy para Cliente (Segurança)
# ===========================
class ClienteSeguranca(Cliente):
    class Meta:
        proxy = True
        verbose_name = "Cliente (Segurança)"
        verbose_name_plural = "🔒 Segurança por Cliente"


# ===========================
# Inlines de segurança
# ===========================
class SecUserInline(admin.TabularInline):
    model = SecUser
    extra = 0


class SecGroupInline(admin.TabularInline):
    model = SecGroup
    extra = 0


class SecUsersGroupsInline(admin.TabularInline):
    model = SecUsersGroups
    extra = 0


class SecGroupAppInline(admin.TabularInline):
    model = SecGroupApp
    extra = 0


class SecSettingsInline(admin.TabularInline):
    model = SecSettings
    extra = 0


# ===========================
# Admin para Segurança do Cliente
# ===========================
@admin.register(ClienteSeguranca)
class ClienteSegurancaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email', 'ativo')

    fieldsets = (
        ('Dados do Cliente', {
            'fields': ('nome', 'cnpj', 'email', 'ativo')
        }),
    )

    inlines = [
        SecUserInline,
        SecGroupInline,
        SecUsersGroupsInline,
        SecGroupAppInline,
        SecSettingsInline,
    ]
