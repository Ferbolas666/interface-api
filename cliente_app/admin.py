from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Cliente, Conexao, Permissao,
    SecUser, SecGroup, SecUsersGroups,
    SecGroupApp, SecSettings,
    ProjetoAplicacao, ProjetoAplicacaoDetalhe,
    ClienteProjetoAplicacao, ProjetoAplicacaoSubprojeto,
    AplicacaoSubprojeto
)

# ===========================
# ClienteAdmin padrão (sem form customizado)
# ===========================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email', 'ativo')

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        url = reverse('pagina_customizada')
        extra_context['custom_button'] = format_html(
            '<a class="button" href="{}">Ativa Projetos</a>', url
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
# Admin de ApliccaoSubprojeto
# ===========================
@admin.register(AplicacaoSubprojeto)
class AplicacaoSubprojetoAdmin(admin.ModelAdmin):
    list_display = ('nome_aplicacao', 'subprojeto')
    search_fields = ('nome_aplicacao', 'subprojeto__nome_aplicacao')

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
