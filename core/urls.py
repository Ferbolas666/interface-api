from django.contrib import admin
from django.urls import path
from cliente_app.views import (
    dashboard_view,
    relatorio_clientes_view,
    cliente_projetos_view,
    pagina_customizada_view,
    detalhe_cliente_view,
    api_subprojetos_por_projeto,
    api_aplicacoes_ativas,
    salvar_aplicacoes_via_api,
    usuarios_cliente_api,
    cadastrar_usuario_api,
    grupos_disponiveis_api,
    api_usuarios_firebird,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("admin/dashboard/", dashboard_view, name="dashboard"),
    path("admin/relatorio-clientes/", relatorio_clientes_view, name="relatorio_clientes"),
    path("admin/cliente-projetos/", cliente_projetos_view, name="cliente_projetos"),

    path("pagina-customizada/", pagina_customizada_view, name="pagina_customizada"),
    path("cliente/<int:cliente_id>/", detalhe_cliente_view, name="detalhe_cliente"),

    # APIs todas dentro de /api/ sem /admin/
    path("api/subprojetos/<int:projeto_id>/", api_subprojetos_por_projeto, name="api_subprojetos"),
    path("api/aplicacoes_ativas/<int:cliente_id>/", api_aplicacoes_ativas, name="aplicacoes_ativas"),
    path("api/inserir_aplicacoes/", salvar_aplicacoes_via_api, name="inserir_aplicacoes"),

    path("api/usuarios_cliente/<int:cliente_id>/", usuarios_cliente_api, name="usuarios_cliente"),
    path("api/cadastrar_usuario/", cadastrar_usuario_api, name="cadastrar_usuario"),

    path("api/grupos_disponiveis/", grupos_disponiveis_api, name="grupos_disponiveis"),

    path("api/firebird_usuarios/<int:cliente_id>/", api_usuarios_firebird, name="api_usuarios_firebird"),
]
