import os
from django.http import JsonResponse
from django.conf import settings

#Simulando CNPJ/USUÁRIO
def listar_arquivos(request):
    cnpj = request.GET.get('cnpj')
    usuario = request.GET.get('usuario')

    #Caminho da pasta onde os arquivos estão
    base_path = os.path.join(settings.MEDIA_ROOT, f'{cnpj}/{usuario}')
    base_url = f'{settings.MEDIA_URL}{cnpj}/{usuario}/'

    if not os.path.exists(base_path):
        return JsonResponse({'success': False, 'message': 'Diretório não encontrado.'})
    
    arquivos = []
    for nome in os.listdir(base_path):
        caminho_completo = os.path.join(base_path, nome)
        if os.path.isfile(caminho_completo):
            arquivos.append({
                'nome': nome,
                'url': request.build_absolute_uri(base_url + nome)
            })

    return JsonResponse({'success': True, 'arquivos': arquivos})
