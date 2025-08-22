from django.db import models

# =============================
# Dados do Cliente
# =============================

class Cliente(models.Model):
    nome  = models.CharField(max_length=100)
    cnpj  = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    ativo = models.BooleanField(default=True)
    token  = models.CharField(max_length=255, blank=True, null=True, unique=True)  # novo campo

    def __str__(self):
        return self.nome

class Conexao(models.Model):
    cliente       = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='conexoes')
    nome          = models.CharField(max_length=100)
    host          = models.CharField(max_length=100)
    port_local    = models.CharField(max_length=50, default='3050')
    database_path = models.CharField(max_length=255)
    usuario       = models.CharField(max_length=50)
    senha         = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nome} ({self.cliente.nome})"

class Permissao(models.Model):
    cliente   = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='permissoes')
    modulo    = models.CharField(max_length=100)
    permitido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente.nome} - {self.modulo}"

# =============================
# Segurança (por cliente)
# =============================

class SecGroup(models.Model):
    cliente     = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='sec_groups')
    group_id    = models.CharField(max_length=50)
    description = models.CharField(max_length=255)

    class Meta:
        unique_together = ('cliente', 'group_id')

    def __str__(self):
        return f"{self.group_id} ({self.cliente.nome})"

class SecGroupApp(models.Model):
    cliente        = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='sec_group_apps')
    cod            = models.AutoField(primary_key=True)
    group          = models.ForeignKey(SecGroup, on_delete=models.CASCADE, related_name='apps')
    cod_modulo     = models.CharField(max_length=50)
    cod_projeto    = models.CharField(max_length=50)
    app_name       = models.CharField(max_length=100)
    priv_access    = models.BooleanField(default=False)
    priv_insert    = models.BooleanField(default=False)
    priv_update    = models.BooleanField(default=False)
    priv_export    = models.BooleanField(default=False)
    priv_print     = models.BooleanField(default=False)
    priv_jaentrego = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.app_name} - {self.group.group_id} ({self.cliente.nome})"

class SecSettings(models.Model):
    cliente   = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='sec_settings')
    set_name  = models.CharField(max_length=50)
    set_value = models.TextField()

    class Meta:
        unique_together = ('cliente', 'set_name')

    def __str__(self):
        return f"{self.set_name} ({self.cliente.nome})"

class SecUser(models.Model):
    cliente         = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='sec_users')
    login           = models.CharField(max_length=50)
    pswd            = models.CharField(max_length=255)
    name            = models.CharField(max_length=100)
    email           = models.EmailField()
    active          = models.BooleanField(default=True)
    activation_code = models.CharField(max_length=100, blank=True, null=True)
    priv_admin      = models.BooleanField(default=False)
    mfa             = models.BooleanField(default=False)
    picture         = models.ImageField(upload_to='pictures/', blank=True, null=True)
    role            = models.CharField(max_length=100)
    phone           = models.CharField(max_length=20)
    pswd_last_updated = models.DateTimeField(auto_now=True)
    mfa_last_updated  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cliente', 'login')

    def __str__(self):
        return f"{self.login} ({self.cliente.nome})"

class SecUsersGroups(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='sec_users_groups')
    login   = models.ForeignKey(SecUser, on_delete=models.CASCADE, related_name='groups')
    group   = models.ForeignKey(SecGroup, on_delete=models.CASCADE, related_name='users')

    class Meta:
        unique_together = ('cliente', 'login', 'group')

    def __str__(self):
        return f"{self.login.login} - {self.group.group_id} ({self.cliente.nome})"

# =============================
# Catálogo Geral de Projetos
# =============================

class ProjetoAplicacao(models.Model):
    cod            = models.AutoField(primary_key=True)
    nome_projeto   = models.CharField(max_length=100)
    nome_aplicacao = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome_projeto} - {self.nome_aplicacao}"

# =============================
# Subprojetos de Projetos
# =============================

class ProjetoAplicacaoSubprojeto(models.Model):
    cod_seq           = models.AutoField(primary_key=True)
    cod_relacao       = models.ForeignKey(ProjetoAplicacao, on_delete=models.CASCADE, related_name='subprojetos')
    nome_aplicacao    = models.CharField(max_length=100)
    nome_demonstracao = models.CharField(max_length=100)
    ativo             = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome_aplicacao} (Subprojeto de {self.cod_relacao.nome_projeto})"

# =============================
# Relacionamento Cliente ↔ Projeto ↔ Subprojeto
# =============================

class ClienteProjetoAplicacao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='projetos_vinculados')
    projeto = models.ForeignKey(ProjetoAplicacao, on_delete=models.CASCADE, related_name='clientes_vinculados')

    subprojeto = models.ForeignKey(
        ProjetoAplicacaoSubprojeto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes_vinculados'
    )

    ativo = models.BooleanField(default=True)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('cliente', 'projeto', 'subprojeto')

    def __str__(self):
        return f"{self.cliente.nome} ↔ {self.projeto.nome_projeto} ↔ {self.subprojeto.nome_aplicacao if self.subprojeto else 'sem sub'}"

# =============================
# Detalhes de Aplicações por Cliente-Projeto
# =============================

class ProjetoAplicacaoDetalhe(models.Model):
    cod_seq           = models.AutoField(primary_key=True)
    cliente_projeto   = models.ForeignKey(ClienteProjetoAplicacao, on_delete=models.CASCADE, related_name='detalhes')
    nome_aplicacao    = models.CharField(max_length=100)
    nome_demonstracao = models.CharField(max_length=100)
    ativo             = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome_aplicacao} ({self.cliente_projeto.cliente.nome})"

# =============================
# Aplicações de Subprojetos
# =============================

class AplicacaoSubprojeto(models.Model):
    subprojeto       = models.ForeignKey(
        ProjetoAplicacaoSubprojeto,
        on_delete=models.CASCADE,
        related_name='aplicacoes'
    )
    nome_aplicacao   = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome_aplicacao} (Subprojeto: {self.subprojeto.nome_aplicacao})"
