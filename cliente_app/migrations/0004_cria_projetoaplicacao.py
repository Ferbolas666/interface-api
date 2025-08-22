# cliente_app/migrations/0004_cria_projetoaplicacao.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cliente_app', '0003_clienteseguranca_alter_conexao_port_local_secgroup_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjetoAplicacao',
            fields=[
                ('cod', models.AutoField(primary_key=True, serialize=False)),
                ('nome_projeto', models.CharField(max_length=100)),
                ('nome_aplicacao', models.CharField(max_length=100)),
            ],
        ),
    ]
