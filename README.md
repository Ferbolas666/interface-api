# Interface API

Este projeto é uma aplicação Django para gerenciamento de clientes e administração personalizada.

## Estrutura do Projeto

```
interface-api/
├── admin-interface/           # Customizações de interface/admin
├── cliente_app/               # App principal de clientes
│   ├── migrations/            # Migrações do banco de dados
│   ├── static/                # Arquivos estáticos do app
│   ├── templates/             # Templates HTML do app
├── core/                      # Configurações principais do Django
├── static/                    # Arquivos estáticos globais
├── staticfiles/               # Coleta de arquivos estáticos
├── templates/                 # Templates globais
├── db.sqlite3                 # Banco de dados SQLite (desenvolvimento)
├── requirements.txt           # Dependências do projeto
├── manage.py                  # Gerenciador do Django
├── Dockerfile                 # Dockerfile para containerização
├── docker-compose.yml         # Orquestração com Docker Compose
```

## Como rodar o projeto localmente

1. Clone o repositório:
   ```sh
   git clone <url-do-repositorio>
   cd interface-api
   ```
2. Crie um ambiente virtual e ative-o:
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
4. Execute as migrações:
   ```sh
   python manage.py migrate
   ```
5. Inicie o servidor:
   ```sh
   python manage.py runserver
   ```

Acesse: http://127.0.0.1:8000/

## Como rodar com Docker

1. Construa e suba os containers:
   ```sh
   docker-compose up --build
   ```
2. O serviço estará disponível em http://localhost:8000/

## Migrações do Banco de Dados

Para criar novas migrações:
```sh
python manage.py makemigrations
```
Para aplicar migrações:
```sh
python manage.py migrate
```

## Como contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b minha-feature`)
3. Commit suas alterações (`git commit -m 'Minha feature'`)
4. Faça push para a branch (`git push origin minha-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.