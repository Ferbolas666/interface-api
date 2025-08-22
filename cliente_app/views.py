from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django import forms
import unicodedata
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe  # Para marcar strings como HTML seguro

from django.db import connection
import logging
# from weasyprint import HTML
from .models import (
    Cliente,
    ProjetoAplicacao,
    ClienteProjetoAplicacao,
    ProjetoAplicacaoSubprojeto,
    AplicacaoSubprojeto,
    Conexao
)

import json
import random
import requests

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import unicodedata
import requests
logger = logging.getLogger(__name__)
@csrf_exempt
def salvar_aplicacoes_via_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'erro', 'mensagem': 'Requisição inválida'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'erro', 'mensagem': 'JSON inválido'}, status=400)

    if not data or not isinstance(data, list):
        return JsonResponse({'status': 'erro', 'mensagem': 'Lista de dados vazia ou inválida'}, status=400)

    grupo_id = data[0].get("grupo_id")
    cliente_id = data[0].get("cliente_id")

    if not grupo_id or not cliente_id:
        return JsonResponse({'status': 'erro', 'mensagem': 'Grupo ou Cliente não informado'}, status=400)

    try:
        grupo_id = int(grupo_id)
        cliente_id = int(cliente_id)
    except:
        return JsonResponse({'status': 'erro', 'mensagem': 'Grupo ID ou Cliente ID inválido'}, status=400)

    # 🔁 BUSCAR CONEXÃO NO BANCO
    try:
        conexao = Conexao.objects.get(cliente_id=cliente_id)
    except Conexao.DoesNotExist:
        return JsonResponse({'status': 'erro', 'mensagem': 'Conexão não encontrada para este cliente'}, status=404)

    DB_CONFIG = {
        "ip": conexao.host,
        "banco": conexao.database_path,
        "porta": int(conexao.port_local),
        "usuario": conexao.usuario,
        "senha": conexao.senha
    }

    FIREBIRD_API = "https://desenvapiversatil.com.br/firebird-query"

    def limpar_nome(texto):
        if not texto:
            return ""
        texto = texto.replace("'", "''").strip()
        texto = ''.join(c for c in texto if unicodedata.category(c)[0] != 'C')
        return texto

    try:
        sql_max_cod = "SELECT MAX(COD) AS MAX_COD FROM SEC_GROUPS_APPS"
        payload_max = {**DB_CONFIG, "sql": sql_max_cod}

        res_max = requests.post(FIREBIRD_API, json=payload_max, timeout=10)
        res_max.raise_for_status()
        max_data = res_max.json()

        if isinstance(max_data, list) and len(max_data) > 0:
            max_cod = max_data[0].get('MAX_COD') or 0
        elif isinstance(max_data, dict) and 'data' in max_data:
            max_cod = max_data['data'][0].get('MAX_COD') or 0
        else:
            max_cod = 0
    except Exception as e:
        max_cod = 0

    total_inseridos = 0
    inseridos_debug = []

    for item in data:
        nome_projeto = item.get("nome_projeto")
        cod_projeto = item.get("cod_projeto")
        nome_aplicacao = item.get("app_name")
        cod_modulo = item.get("codModulo")

        if not (nome_projeto and cod_projeto and nome_aplicacao):
            inseridos_debug.append("❌ Dados incompletos, pulando item.")
            continue

        nome_projeto_sql = limpar_nome(nome_projeto)
        nome_aplicacao_sql = limpar_nome(nome_aplicacao)
        max_cod += 1

        sql_insert = f"""
            INSERT INTO SEC_GROUPS_APPS
            (COD, GROUP_ID, COD_MODULO, COD_PROJETO, NOME_PROJETO, APP_NAME,
             PRIV_ACCESS, PRIV_INSERT, PRIV_DELETE, PRIV_UPDATE, PRIV_EXPORT, PRIV_PRINT)
            VALUES
            ({max_cod}, {grupo_id}, {cod_modulo}, {cod_projeto}, '{nome_projeto_sql}', '{nome_aplicacao_sql}',
             'Y', 'Y', 'Y', 'Y', 'Y', 'Y')
        """

        payload_insert = {**DB_CONFIG, "sql": sql_insert}

        try:
            res_insert = requests.post(FIREBIRD_API, json=payload_insert, timeout=10)
            try:
                resposta_json = res_insert.json()
            except:
                resposta_json = res_insert.text

            if res_insert.status_code != 200:
                raise Exception(f"Erro {res_insert.status_code}: {resposta_json}")

            total_inseridos += 1
            inseridos_debug.append(f"✅ {nome_aplicacao_sql} | COD: {max_cod} | Resposta: {resposta_json}")
        except Exception as e:
            inseridos_debug.append(f"❌ {nome_aplicacao_sql} | COD: {max_cod} | Erro: {str(e)}")
            continue

    return JsonResponse({
        'status': 'ok',
        'mensagem': f'{total_inseridos} inserções bem-sucedidas',
        'inseridos': total_inseridos,
        'detalhes': inseridos_debug
    })

from django.http import JsonResponse
from cliente_app.models import Conexao  # ajuste se o import for diferente
import requests

# =========================
# API: Cadastro Usuários
# =========================
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import requests

@csrf_exempt
def cadastrar_usuario_api(request):
    if request.method != "POST":
        return JsonResponse({"status": "erro", "mensagem": "Método não permitido"}, status=405)

    try:
        dados = json.loads(request.body)

        login      = dados.get("login")
        senha      = dados.get("senha")
        nome       = dados.get("nome")
        email      = dados.get("email")
        ativo      = 'Y' if dados.get("ativo") else 'N'
        admin      = 'Y' if dados.get("admin") else 'N'
        grupo_id   = dados.get("grupo_id")
        cliente_id = dados.get("cliente_id")

        if not grupo_id or not cliente_id:
            return JsonResponse({"status": "erro", "mensagem": "Grupo ou cliente não informado!"}, status=400)

        # 🔁 BUSCAR CONFIG DA CONEXÃO DO CLIENTE
        try:
            conexao = Conexao.objects.get(cliente_id=cliente_id)
        except Conexao.DoesNotExist:
            return JsonResponse({"status": "erro", "mensagem": "Conexão não encontrada para este cliente"}, status=404)

        config_base = {
            "ip": conexao.host,
            "banco": conexao.database_path,
            "porta": int(conexao.port_local),
            "usuario": conexao.usuario,
            "senha": conexao.senha
        }

        FIREBIRD_API = "https://desenvapiversatil.com.br/firebird-query"

        # 1️⃣ INSERT: SEC_USERS
        sql_usuario = f"""
            INSERT INTO SEC_USERS (LOGIN, PSWD, NAME, EMAIL, ACTIVE, PRIV_ADMIN)
            VALUES ('{login}', '{senha}', '{nome}', '{email}', '{ativo}', '{admin}')
        """

        payload_usuario = {**config_base, "sql": sql_usuario.strip()}
        r1 = requests.post(FIREBIRD_API, json=payload_usuario, timeout=10)
        r1.raise_for_status()

        # 2️⃣ INSERT: SEC_USERS_GROUPS
        sql_grupo = f"""
            INSERT INTO SEC_USERS_GROUPS (GROUP_ID, LOGIN)
            VALUES ({grupo_id}, '{login}')
        """

        payload_grupo = {**config_base, "sql": sql_grupo.strip()}
        r2 = requests.post(FIREBIRD_API, json=payload_grupo, timeout=10)
        r2.raise_for_status()

        return JsonResponse({"status": "ok", "mensagem": "Usuário e grupo vinculados com sucesso!"})

    except requests.exceptions.RequestException as api_error:
        return JsonResponse({"status": "erro", "mensagem": f"Erro na API externa: {str(api_error)}"}, status=500)

    except Exception as e:
        return JsonResponse({"status": "erro", "mensagem": f"Erro ao cadastrar: {str(e)}"}, status=400)

# =========================
# Grupos ID para Usuários
# =========================
@csrf_exempt
def grupos_disponiveis_api(request):
    if request.method != "POST":
        return JsonResponse({"status": "erro", "mensagem": "Método não permitido"}, status=405)

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "erro", "mensagem": "JSON inválido"}, status=400)

    cliente_id = dados.get("cliente_id")
    if not cliente_id:
        return JsonResponse({"status": "erro", "mensagem": "Cliente não informado!"}, status=400)

    try:
        conexao = Conexao.objects.get(cliente_id=cliente_id)
    except Conexao.DoesNotExist:
        return JsonResponse({"status": "erro", "mensagem": "Conexão não encontrada para este cliente"}, status=404)

    config = {
        "ip": conexao.host,
        "banco": conexao.database_path,
        "porta": int(conexao.port_local),
        "usuario": conexao.usuario,
        "senha": conexao.senha,
        "sql": "SELECT GROUP_ID, DESCRIPTION FROM SEC_GROUPS ORDER BY GROUP_ID"
    }

    FIREBIRD_API = "https://desenvapiversatil.com.br/firebird-query"

    try:
        resp = requests.post(FIREBIRD_API, json=config, timeout=10)
        resp.raise_for_status()

        dados_api = resp.json()

        if isinstance(dados_api, list):
            grupos = dados_api
        else:
            grupos = dados_api.get("data", []) or dados_api.get("resultado", [])

        return JsonResponse({"status": "ok", "grupos": grupos})

    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "status": "erro",
            "mensagem": f"Erro na API externa: {str(e)}"
        }, status=502)

    except Exception as e:
        return JsonResponse({
            "status": "erro",
            "mensagem": f"Erro interno: {str(e)}"
        }, status=500)

# =========================
# API: Usuários
# =========================
def usuarios_cliente_api(request, cliente_id):
    if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        try:
            # Busca a conexão no banco de dados usando o cliente_id
            conexao = Conexao.objects.get(cliente_id=cliente_id)
        except Conexao.DoesNotExist:
            return JsonResponse({
                "status": "erro",
                "mensagem": f"Conexão não encontrada para o cliente ID {cliente_id}"
            }, status=404)

        # Tratamento seguro da porta
        try:
            porta = int(conexao.port_local)
        except (TypeError, ValueError):
            porta = 3050  # Fallback para porta padrão do Firebird

        # Monta a configuração dinamicamente
        config = {
            "ip": conexao.host,
            "banco": conexao.database_path,
            "porta": porta,
            "usuario": conexao.usuario,
            "senha": conexao.senha,
            "sql": "SELECT LOGIN, PSWD, NAME AS NOME, EMAIL, ACTIVE AS ATIVO, PRIV_ADMIN FROM SEC_USERS"
        }

        try:
            response = requests.post(
                "https://desenvapiversatil.com.br/firebird-query",
                json=config,
                timeout=10
            )
            response.raise_for_status()  # Lança exceção para status 4xx/5xx
            
            dados = response.json()
            
            # Tratamento seguro da resposta
            if isinstance(dados, list):
                lista_usuarios = dados
            else:
                lista_usuarios = dados.get("data", []) or dados.get("resultado", [])
            
            return JsonResponse({
                'status': 'ok',
                'usuarios': lista_usuarios
            })
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'status': 'erro',
                'mensagem': f"Erro na conexão com o banco: {str(e)}",
                'usuarios': []
            }, status=502)
            
        except Exception as e:
            return JsonResponse({
                'status': 'erro',
                'mensagem': f"Erro interno: {str(e)}",
                'usuarios': []
            }, status=500)

    else:
        # Parte não-AJAX mantida igual
        from cliente_app.models import Cliente
        cliente = Cliente.objects.get(id=cliente_id)
        return render(request, "admin/usuarios_cliente.html", {"cliente": cliente})
# =========================
# Usuários API Clientes
# =========================
def api_usuarios_firebird(request, cliente_id):
    if request.META.get("HTTP_X_REQUESTED_WITH") != "XMLHttpRequest":
        return JsonResponse({'erro': 'Requisição inválida'}, status=400)
    
    try:
        # Busca a conexão no banco de dados usando o cliente_id
        conexao = Conexao.objects.get(cliente_id=cliente_id)
    except Conexao.DoesNotExist:
        return JsonResponse({
            "status": "erro",
            "mensagem": f"Conexão não encontrada para o cliente ID {cliente_id}"
        }, status=404)

    # Tratamento seguro da porta
    try:
        porta = int(conexao.port_local)
    except (TypeError, ValueError):
        porta = 3050  # Fallback para porta padrão do Firebird

    # Configuração base dinâmica
    config_base = {
        "ip": conexao.host,
        "banco": conexao.database_path,
        "porta": porta,
        "usuario": conexao.usuario,
        "senha": conexao.senha,
    }

    try:
        # 1️⃣ Primeiro SELECT: busca os usuários ativos
        config_usuarios = {
            **config_base,
            "sql": "SELECT LOGIN, NAME AS NOME FROM SEC_USERS WHERE ACTIVE = 'Y'"
        }

        resp = requests.post(
            "https://apiversatil.com.br/firebird-query",
            json=config_usuarios,
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
        usuarios = data if isinstance(data, list) else data.get("data", []) or data.get("resultado", [])

        # 2️⃣ Para cada usuário, buscar o GROUP_ID
        for user in usuarios:
            login = user.get("LOGIN")
            if not login:
                user["GROUP_ID"] = None
                continue

            # Usando parâmetros seguros para evitar SQL Injection
            config_group = {
                **config_base,
                "sql": "SELECT GROUP_ID FROM SEC_USERS_GROUPS WHERE LOGIN = ?",
                "params": [login]  # Usando parâmetro seguro
            }

            try:
                group_resp = requests.post(
                    "https://apiversatil.com.br/firebird-query",
                    json=config_group,
                    timeout=8
                )
                group_resp.raise_for_status()
                group_data = group_resp.json()

                # Tratamento seguro da resposta
                grupos = group_data if isinstance(group_data, list) else group_data.get("data", []) or group_data.get("resultado", [])
                
                if grupos and isinstance(grupos, list) and len(grupos) > 0:
                    user["GROUP_ID"] = grupos[0].get("GROUP_ID")
                else:
                    user["GROUP_ID"] = None
                    
            except Exception as group_err:
                # Log opcional: logger.error(f"Erro ao buscar grupo para {login}: {str(group_err)}")
                user["GROUP_ID"] = None

        return JsonResponse({'status': 'ok', 'usuarios': usuarios})
    
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'erro', 
            'mensagem': f"Erro na conexão com o banco de dados: {str(e)}",
            'usuarios': []
        }, status=502)
        
    except Exception as e:
        return JsonResponse({
            'status': 'erro', 
            'mensagem': f"Erro interno: {str(e)}",
            'usuarios': []
        }, status=500)

# =========================
# DASHBOARD
# =========================
@staff_member_required
def dashboard_view(request):
    grupos = Cliente.objects.values_list('grupo', flat=True).distinct()
    labels = list(grupos)
    data = [Cliente.objects.filter(grupo=g).count() for g in grupos]

    context = {
        'total_clientes': Cliente.objects.count(),
        'total_grupos': len(grupos),
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }
    return TemplateResponse(request, 'admin/dashboard.html', context)

# =========================
# RELATÓRIO DE CLIENTES
# =========================
@staff_member_required
def relatorio_clientes_view(request):
    clientes = Cliente.objects.all()

    if request.GET.get('export') == 'pdf':
        html = render_to_string('relatorio_clientes_pdf.html', {'clientes': clientes})
        pdf_file = HTML(string=html).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="relatorio_clientes.pdf"'
        return response

    return TemplateResponse(request, 'relatorio_clientes.html', {'clientes': clientes})

# =========================
# CLIENTE + PROJETOS BOTÕES
# =========================
class ClienteSelectForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(ativo=True),
        label="Selecione um Cliente",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

@staff_member_required
def cliente_projetos_view(request):
    form = ClienteSelectForm(request.GET or None)
    cliente = None
    projetos = []

    if form.is_valid():
        cliente = form.cleaned_data['cliente']
        projetos = ClienteProjetoAplicacao.objects.filter(cliente=cliente, ativo=True)

    context = {
        'form': form,
        'cliente': cliente,
        'projetos': projetos
    }
    return TemplateResponse(request, 'admin/cliente_projetos.html', context)

# =========================
# Cadastro de Projetos em Clientes
# =========================
@staff_member_required
def pagina_customizada_view(request):
    clientes = Cliente.objects.all()
    context = {
        'clientes': clientes,
    }
    return TemplateResponse(request, 'admin/pagina_customizada.html', context)

# =========================
# DETALHE DO CLIENTE + VÍNCULOS
# =========================
@staff_member_required
def detalhe_cliente_view(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    # Buscar somente os projetos vinculados e ativos para esse cliente
    vinculos = ClienteProjetoAplicacao.objects.filter(cliente_id=cliente_id, ativo=True).select_related('projeto')

    # Extrair os projetos a partir desses vínculos, evitando duplicatas
    projetos = list({v.projeto for v in vinculos})

    # Mapeia subprojetos por projeto_id
    subprojetos_map = {
        projeto.cod: list(projeto.subprojetos.all())
        for projeto in projetos
    }

    if request.method == "POST":
        projeto_id = request.POST.get("projeto_id")
        subprojetos_ids = request.POST.getlist("subprojetos")

        # Remove vínculos antigos do cliente com esse projeto
        ClienteProjetoAplicacao.objects.filter(cliente=cliente, projeto_id=projeto_id).delete()

        # Insere novos vínculos
        for sp_id in subprojetos_ids:
            try:
                sub = ProjetoAplicacaoSubprojeto.objects.get(pk=sp_id)
                ClienteProjetoAplicacao.objects.create(
                    cliente=cliente,
                    projeto_id=projeto_id,
                    subprojeto=sub,
                    ativo=True
                )
            except ProjetoAplicacaoSubprojeto.DoesNotExist:
                continue  # ignora se o subprojeto não existir

    return TemplateResponse(request, 'admin/detalhe_cliente.html', {
        'cliente': cliente,
        'projetos': projetos,
        'subprojetos_map': subprojetos_map,
    })

# =========================
# Cadastro de Usuários
# =========================
@staff_member_required
def usuarios_cliente_view(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return TemplateResponse(request, 'admin/usuarios_cliente.html', {'cliente': cliente})

# =========================
# API: Subprojetos de um Projeto
# =========================
@staff_member_required
def api_subprojetos_por_projeto(request, projeto_id):
    cliente_id = request.GET.get("cliente_id")

    if not cliente_id:
        return JsonResponse({"error": "Parâmetro 'cliente_id' é obrigatório."}, status=400)
    
    subprojetos = ProjetoAplicacaoSubprojeto.objects.filter(cod_relacao_id=projeto_id)

    # Pega IDs dos subprojetos já vinculados a esse cliente + projeto
    vinculos = ClienteProjetoAplicacao.objects.filter(cliente_id=cliente_id, projeto_id=projeto_id)
    subprojetos_vinculados_ids = set()
    for v in vinculos:
        if v.subprojeto_id:
            subprojetos_vinculados_ids.add(v.subprojeto_id)

    data = {
        "subprojetos": [
            {
                "id": sp.cod_seq,
                "nome_aplicacao": sp.nome_aplicacao,
                "vinculado": sp.cod_seq in subprojetos_vinculados_ids
            }
            for sp in subprojetos
        ]
    }
    return JsonResponse(data)

# =========================
# API para retornar subprojetos ativos de um cliente
# =========================
def api_aplicacoes_ativas(request, cliente_id):
    subprojetos = ClienteProjetoAplicacao.objects.filter(cliente_id=cliente_id, ativo=True)

    resultado = []
    for sp in subprojetos:
        aplicacoes = AplicacaoSubprojeto.objects.filter(subprojeto_id=sp.subprojeto_id)
        for app in aplicacoes:
            resultado.append({
                "subprojeto_id": sp.subprojeto_id,
                "projeto_id": sp.projeto_id,
                "projeto_nome": sp.projeto.nome.lower() if hasattr(sp.projeto, "nome") else "desconhecido",
                "nome_aplicacao": app.nome_aplicacao
            })

    return JsonResponse(resultado, safe=False)

# =========================
# API Para Cadastro de Grupos
# =========================
def rota_falsa(request):
    return JsonResponse({"erro": "rota fictícia criada para evitar NoReverseMatch"})

@csrf_exempt
def grupos_cliente_api(request, cliente_id):
    """
    View que retorna os grupos do cliente por AJAX, ou renderiza a tela com HTML se for acesso normal.
    """

    # 1. Se for requisição AJAX, retorna JSON com os grupos
    if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        try:
            # Buscar dados de conexão do banco de dados
            conexao = Conexao.objects.get(cliente_id=cliente_id)
        except Conexao.DoesNotExist:
            return JsonResponse({
                "status": "erro",
                "mensagem": f"Conexão não encontrada para o cliente ID {cliente_id}"
            }, status=404)

        # Tratamento seguro da porta
        try:
            porta = int(conexao.port_local)
        except (TypeError, ValueError):
            porta = 3050  # Fallback para porta padrão do Firebird

        # Montar configuração dinâmica
        config = {
            "ip": conexao.host,
            "banco": conexao.database_path,
            "porta": porta,
            "usuario": conexao.usuario,
            "senha": conexao.senha,
            "sql": "SELECT GROUP_ID, DESCRIPTION FROM SEC_GROUPS ORDER BY GROUP_ID"
        }

        try:
            print(f"🔍 Cliente ID: {cliente_id} — Enviando requisição para API externa:", {
                "ip": config["ip"],
                "banco": config["banco"],
                "porta": config["porta"],
                "usuario": config["usuario"],
                # Não mostrar senha por segurança
            })
            
            resp = requests.post(
                "https://desenvapiversatil.com.br/firebird-query",
                json=config,
                timeout=15
            )
            
            print("✅ Resposta bruta:", resp.text[:200])  # Mostrar apenas parte inicial
            resp.raise_for_status()

            dados = resp.json()
            # Tratamento seguro da resposta
            grupos = dados if isinstance(dados, list) else dados.get("data", []) or dados.get("resultado", [])
            
            return JsonResponse({"status": "ok", "grupos": grupos})

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na API externa para cliente {cliente_id}:", e)
            return JsonResponse({
                "status": "erro",
                "mensagem": f"Erro na conexão com o banco de dados: {str(e)}",
                "cliente_id": cliente_id
            }, status=502)
            
        except Exception as e:
            print(f"❌ Erro interno para cliente {cliente_id}:", e)
            return JsonResponse({
                "status": "erro",
                "mensagem": f"Erro no processamento: {str(e)}",
                "cliente_id": cliente_id
            }, status=500)

    # 2. Se não for AJAX, renderiza a tela HTML com o ID do cliente
    return render(request, "admin/grupos_cliente.html", {"cliente_id": cliente_id})
# =========================
# API De Insert de Grupo
# =========================
@csrf_exempt
def cadastrar_grupo(request, cliente_id):
    if request.method != 'POST':
        return redirect("detalhe_cliente", cliente_id=cliente_id)
    
    try:
        # Buscar dados de conexão do banco de dados
        conexao = Conexao.objects.get(cliente_id=cliente_id)
    except Conexao.DoesNotExist:
        messages.error(request, f"Conexão não encontrada para o cliente ID {cliente_id}")
        return redirect("detalhe_cliente", cliente_id=cliente_id)
    
    # Obter dados do formulário
    group_id    = request.POST.get('group_id')
    description = request.POST.get('description')

    # Validação básica dos dados
    if not group_id or not description:
        messages.error(request, "Group ID e Description são obrigatórios.")
        return redirect("detalhe_cliente", cliente_id=cliente_id)
    
    # Tratamento seguro da porta
    try:
        porta = int(conexao.port_local)
    except (TypeError, ValueError):
        porta = 3050 # Fallback para porta padrão do Firebird

    # Construção segura da query SQL (evitando SQL Injection)
    try:
        # Convertendo group_id para número (validação adicional)
        group_id_int = int(group_id)

        # Escapando aspas simples na descrição
        description_safe = description.replace("'", "''")

        sql = f"INSERT INTO SEC_GROUPS (GROUP_ID, DESCRIPTION) VALUES ({group_id_int}, '{description_safe}')"
    except ValueError:
        messages.error(request, "Group ID deve ser um número inteiro.")
        return redirect("detalhe_cliente", cliente_id=cliente_id)
    
    # Montar payload dinâmico
    payload = {
        "ip": conexao.host,
        "banco": conexao.database_path,
        "porta": porta,
        "usuario": conexao.usuario,
        "senha": conexao.senha,
        "sql": sql
    }

    try:
        resp = requests.post(
            "https://desenvapiversatil.com.br/firebird-query",
            json=payload,
            timeout=15
        )

        # Verificar se a inserção bem sucedida
        if resp.status_code == 200:
            messages.success(request, "✅ Grupo cadastrado com sucesso!")
        else:
            messages.warning(request, "⚠️ Grupo cadastrado, mas com resposta inesperada do servidor")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao inserir grupo para cliente {cliente_id}:", e)
        messages.error(request, f"❌ Erro ao cadastrar grupo: {str(e)}")

    except Exception as e:
        print(f"❌ Erro interno ao inserir grupo para cliente {cliente_id}:", e)
        messages.error(request, f"❌ Erro interno: {str(e)}")

    return redirect("detalhe_cliente", cliente_id=cliente_id)