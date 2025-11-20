## Instruções de instalação e execução (resumido e testado)

Pré-requisitos
- Python 3.8+ (recomendo 3.11)
- pip
- (Opcional) R + Rscript para gerar o relatório em R

Instalação (recomendada: virtualenv)

1. Crie e ative o venv

    cd /home/jenifer/Área de Trabalho/Global_Solution
    python3 -m venv .venv
    source .venv/bin/activate

2. Atualize e instale dependências

    python3 -m pip install --upgrade pip setuptools wheel
    python3 -m pip install -r requirements.txt

Popular banco de dados (fixtures)

1. Criar schema e popular dados de teste

    python3 setup_project.py
    python3 -c "import seed_fixtures; seed_fixtures.seed()"

Rodando localmente (desenvolvimento)

1. Executar o servidor em modo desenvolvimento

    export JWT_SECRET="uma-senha-forte-local"  # em produção defina um segredo seguro
    python3 server.py

2. Abrir o navegador em http://127.0.0.1:5000/

Testes

    pytest -q

Docker (produção)

Um `Dockerfile` otimizado (multi-stage, usuário não-root, imagem enxuta) foi adicionado. Eu não consegui construir a imagem neste ambiente porque o binário `docker` não está disponível aqui; você pode rodar os comandos abaixo na sua máquina/CI:

1. Build e rodar

    docker build -t global_solution:latest .
    docker-compose up --build -d

2. Ver logs

    docker-compose logs -f

Observações de produção
- Defina a variável de ambiente `JWT_SECRET` com um segredo forte antes de iniciar o container.
- Não execute o Flask com `debug=True` em produção — use `gunicorn` (o Dockerfile usa gunicorn no CMD).
- O projeto utiliza `bcrypt` quando disponível para armazenar senhas. Usuários criados pelo `seed_fixtures` usam hashes compatíveis.

Se você precisa de R dentro da imagem (para rodar `stress_analysis_report.R`) eu posso fornecer uma variante baseada em `rocker`/R (imagem maior). Atualmente a imagem multi-stage foi projetada para ser Python-first e pequena; me diga se prefere manter R embutido.
## Instruções de instalação e execução (resumo)

Pré-requisitos
- Python 3.8+
- pip
- (Opcional) R + Rscript para usar o relatório em R

Instalação Python (recomendado: venv)

```bash
cd /home/jenifer/Área de Trabalho/Global_Solution
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
```

Instalação (R) — opcional
- Certifique-se de ter `Rscript` disponível no PATH.
- Pacotes R usados: RSQLite, dbplyr, dplyr, ggplot2

```bash
R -e "install.packages(c('RSQLite','dbplyr','dplyr','ggplot2'), repos='https://cloud.r-project.org')"
```

Rodando localmente (demo)

1) Criar DB e popular fixtures:

```bash
python3 setup_project.py
python3 -c "import seed_fixtures; seed_fixtures.seed()"
```

2) Rodar servidor (desenvolvimento):

```bash
python3 server.py
# abrir http://127.0.0.1:5000/
```

Testes

```bash
pytest -q
```

Docker (produção)

O `Dockerfile` já instala dependências e inclui R. O `docker-compose.yml` foi configurado para executar o app usando `gunicorn`.

1) Build e up (produção):

```bash
docker build -t ai-sales-copilot .
docker-compose up --build -d
```

2) Ver logs:

```bash
docker-compose logs -f
```

Notas de segurança e operação
- Defina a variável de ambiente `JWT_SECRET` em produção para um segredo forte antes de subir o container.
 - Defina a variável de ambiente `JWT_SECRET` em produção para um segredo forte antes de subir o container.
 - O projeto agora usa `bcrypt` para armazenar senhas. Se você inspecionar a base de dados, as senhas serão armazenadas como hashes bcrypt. Para criar/atualizar usuários fora do app use `setup_project.add_employee_securely(nome, cargo, senha)` ou execute `seed_fixtures.seed()`.
- O token JWT emitido pelo endpoint `/api/login` expira em 1 hora por padrão.
- Não execute o Flask em modo `debug=True` em produção (o `docker-compose` já usa `gunicorn`).

Se quiser que eu gere um `dockerfile`/`compose` ainda mais enxuto (multi-stage, usuário não-root e imagens menores), posso fazer isso como próxima etapa.
