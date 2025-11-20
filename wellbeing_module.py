import sqlite3

DB_PATH = 'ai_sales_copilot.db'


def analyze_sentiment(texto):
    text = texto.lower()
    negative = [
        'frustr',
        'frustrado',
        'frustrada',
        'estress',
        'estressado',
        'estressada',
        'pressao',
        'dificil',
        'impossivel',
        'perdendo',
        'sobrecarregado',
    ]
    positive = [
        'otimo',
        'sucesso',
        'bom',
        'bem',
        'consegui',
        'produtividade',
    ]
    neg_count = sum(1 for w in negative if w in text)
    pos_count = sum(1 for w in positive if w in text)
    if neg_count + pos_count == 0:
        return 0.0
    score = (pos_count - neg_count) / max(1, (pos_count + neg_count))
    if score > 1.0:
        score = 1.0
    if score < -1.0:
        score = -1.0
    return float(score)


def suggest_alternative(score, cargo):
    intensity = 'leve'
    if score <= -0.6:
        intensity = 'alto'
    elif score <= -0.3:
        intensity = 'medio'
    if cargo == 'SDR':
        if score < -0.3:
            return (
                f'Pausa ativa recomendada ({intensity}). '
                'Use templates e automacao para 3 follow-ups.'
            )
        return 'Mantenha o ritmo e compartilhe taticas.'

    if cargo == 'Closer':
        if score < -0.3:
            return f'Revisar playbook e pedir apoio de um mentor ({intensity}).'
        return 'Boa performance.'

    if cargo == 'Engenheiro':
        if score < -0.3:
            return (
                f'Automatizar geracao de diagramas e dividir tarefas ({intensity}).'
            )
        return 'Continue iterando sobre automacoes.'
    return 'Considere conversar com o time e fazer uma pausa curta.'


def registrar_log_estresse_e_pontuar(id_funcionario, problema, pontualidade_ok=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT cargo, pontos_gamificacao FROM FUNCIONARIOS WHERE id_funcionario = ?', (id_funcionario,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    cargo, pontos_atuais = row
    score = analyze_sentiment(problema)
    sugestao = suggest_alternative(score, cargo)
    pontos = 0
    if pontualidade_ok:
        pontos += 5
    c.execute("SELECT COUNT(*) FROM ATIVIDADES WHERE id_funcionario = ? AND status = 'VENCIDA'", (id_funcionario,))
    vencidas = c.fetchone()[0]
    if vencidas == 0:
        pontos += 10
    insert_sql = (
        'INSERT INTO LOG_ESTRESSE (id_funcionario, descricao_problema, '
        'score_sentimento, sugestao_ia, pontos) VALUES (?, ?, ?, ?, ?)'
    )
    c.execute(insert_sql, (id_funcionario, problema, score, sugestao, pontos))
    novo_total = pontos_atuais + pontos
    update_sql = (
        'UPDATE FUNCIONARIOS SET pontos_gamificacao = ?, '
        'nivel_estresse_agregado = ? WHERE id_funcionario = ?'
    )
    c.execute(update_sql, (novo_total, score, id_funcionario))
    conn.commit()
    conn.close()
    return {'score': score, 'sugestao': sugestao, 'pontos': pontos, 'novo_total': novo_total}
