# cliente_app/migrations/0005_cria_projetoaplicacaodetalhe.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('cliente_app', '0004_cria_projetoaplicacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjetoAplicacaoDetalhe',
            fields=[
                ('cod_seq', models.AutoField(primary_key=True, serialize=False)),
                ('nome_aplicacao', models.CharField(max_length=100)),
                ('nome_demonstracao', models.CharField(max_length=100)),
                ('ativo', models.BooleanField(default=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aplicacoes_detalhes', to='cliente_app.cliente')),
                ('projeto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aplicacoes', to='cliente_app.projetoaplicacao')),
            ],
        ),
    ]
