import random
from setup_project import setup_database, add_employee_securely, insert_client, populate_training_data, DB_NAME
from wellbeing_module import analyze_sentiment, suggest_alternative
import sqlite3
from datetime import date, timedelta
import time


def _exec_write(query, params=(), retries=5):
    for i in range(retries):
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except sqlite3.OperationalError:
            time.sleep(0.1)
    return False


def seed():
    setup_database()
    populate_training_data()
    cargos = ['SDR', 'Closer', 'Engenheiro']
    employees = []
    for i in range(1, 11):
        nome = f'User{i} Test'
        cargo = random.choice(cargos)
        senha = f'pwd{i}2025'
        uid = add_employee_securely(nome, cargo, senha)
        if not uid:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('SELECT id_funcionario FROM FUNCIONARIOS WHERE nome = ?', (nome,))
            r = c.fetchone()
            uid = r[0] if r else None
            conn.close()
        if uid:
            tempo_manual = random.uniform(120, 300)
            tempo_reduzido = max(0, tempo_manual - random.uniform(10, 120))
            update_sql = (
                'UPDATE FUNCIONARIOS SET tempo_operacional_manual = ?, '
                'tempo_reduzido_copilot = ? WHERE id_funcionario = ?'
            )
            _exec_write(update_sql, (tempo_manual, tempo_reduzido, uid))
            employees.append((uid, nome, cargo))
    clients = []
    for j in range(1, 9):
        nome_empresa = f'Client{j} SA'
        cnpj = f'99.999.99{j:02d}/0001-9{j}'
        decisor = f'Decisor{j}'
        email = f'decisor{j}@client{j}.com'
        responsavel = random.choice(employees)[0]
        cid = insert_client(nome_empresa, cnpj, decisor, email, responsavel)
        if cid:
            clients.append((cid, nome_empresa))
    for cid, _ in clients:
        for k in range(random.randint(1, 3)):
            valor = random.uniform(5000, 120000)
            _exec_write(
                'INSERT INTO PROPOSTAS (id_cliente, tipo, valor_total, caminho_arquivo) VALUES (?, ?, ?, ?)',
                (cid, 'Comercial', valor, None),
            )
    for uid, _, _ in employees:
        for a in range(random.randint(0, 4)):
            vencida = random.choice([True, False, False])
            status = 'VENCIDA' if vencida else random.choice(['PENDENTE', 'CONCLUIDA'])
            dv = (date.today() - timedelta(days=random.randint(0, 20))).isoformat()
            _exec_write(
                'INSERT INTO ATIVIDADES (id_funcionario, descricao, data_vencimento, status) VALUES (?, ?, ?, ?)',
                (uid, f'Tarefa {a}', dv, status),
            )
    sample_texts = [
        'Estou muito frustrado com metas e pressao',
        'Tive um otimo dia, fechei 2 contratos',
        'Perdendo tempo com atividades manuais',
        'Uso automacao e me sinto mais produtivo',
        'Sobrecarga e prazos impossiveis',
        'Dia normal, sem novidades',
    ]
    for uid, _, cargo in employees:
        for _ in range(random.randint(1, 4)):
            texto = random.choice(sample_texts)
            score = analyze_sentiment(texto)
            sugest = suggest_alternative(score, cargo)
            insert_sql = (
                'INSERT INTO LOG_ESTRESSE (id_funcionario, descricao_problema, '
                'score_sentimento, sugestao_ia, pontos) VALUES (?, ?, ?, ?, ?)'
            )
            _exec_write(insert_sql, (uid, texto, score, sugest, random.randint(0, 15)))


if __name__ == '__main__':
    seed()
