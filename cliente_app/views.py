from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
# from weasyprint import HTML
from .models import Cliente
import json

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

@staff_member_required
def relatorio_clientes_view(request):
    clientes = Cliente.objects.all()

    # Exporta como PDF se tiver ?export=pdf
    if request.GET.get('export') == 'pdf':
        html = render_to_string('relatorio_clientes_pdf.html', {'clientes': clientes})
        pdf_file = HTML(string=html).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="relatorio_clientes.pdf"'
        return response

    # Caso contrário, exibe como HTML com botão
    return TemplateResponse(request, 'relatorio_clientes.html', {'clientes': clientes})
