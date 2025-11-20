import sqlite3
import random

# ==============================================================================
# REQUISITO: PYTHON, BANCO DE DADOS, CYBERSECURITY (simulação)
# ==============================================================================

DB_NAME = 'ai_sales_copilot.db'


def setup_database():
    """Cria o banco de dados e as tabelas essenciais para o MVP."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    print("Configurando o banco de dados para Mapeamento de Estresse...")

    # Tabela 1: FUNCIONARIOS (Inclui campo para simular armazenamento seguro de senha)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FUNCIONARIOS (
            id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT NOT NULL, -- SDR, Closer, Engenheiro
            senha_hash TEXT,    -- Requisito: Cybersecurity
            pontos_gamificacao INTEGER DEFAULT 0,
            nivel_estresse_agregado REAL DEFAULT 0.0
        )
    """)

    # Tabela 2: LOG_ESTRESSE (Dados brutos para o ML e R)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LOG_ESTRESSE (
            id_log INTEGER PRIMARY KEY AUTOINCREMENT,
            id_funcionario INTEGER NOT NULL,
            data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            descricao_problema TEXT,  -- Input do usuário (análise de ML)
            score_sentimento REAL,    -- Output do modelo ML (ex: -1.0 a 1.0)
            sugestao_ia TEXT,         -- Alternativa dada pela IA
            FOREIGN KEY (id_funcionario) REFERENCES FUNCIONARIOS(id_funcionario)
        )
    """)

    # Tabela 3: ATIVIDADES (Para Gamificação: 'atividades não vencidas')
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ATIVIDADES (
            id_atividade INTEGER PRIMARY KEY AUTOINCREMENT,
            id_funcionario INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            data_vencimento DATE,
            status TEXT DEFAULT 'PENDENTE', -- PENDENTE, CONCLUIDA, VENCIDA
            FOREIGN KEY (id_funcionario) REFERENCES FUNCIONARIOS(id_funcionario)
        )
    """)

    conn.commit()
    conn.close()
    print("Configuração do Banco de Dados concluída.")


def add_sample_employees():
    """Adiciona alguns funcionários de exemplo para fins de teste."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    employees = [
        ("Maria Silva", "SDR", "hashed_senha_sdr1"),
        ("João Costa", "Closer", "hashed_senha_closer1"),
        ("Pedro Souza", "Engenheiro", "hashed_senha_eng1"),
    ]

    try:
        for nome, cargo, senha_hash in employees:
            # Simulação de inserção segura de senha
            cursor.execute(
                "INSERT INTO FUNCIONARIOS (nome, cargo, senha_hash) VALUES (?, ?, ?)",
                (nome, cargo, senha_hash),
            )

        conn.commit()
        print("Funcionários de exemplo adicionados.")
    except sqlite3.IntegrityError:
        print("Funcionários já existem.")
    finally:
        conn.close()


# ==============================================================================
# REQUISITO: MACHINE LEARNING / REDES NEURAIS (NLP/Análise de Sentimento)
# ==============================================================================


def analyze_sentiment(text):
    """
    Simula um modelo de NLP para Análise de Sentimento em português.
    Retorna um score de -1.0 (Alto Estresse/Negativo) a 1.0 (Baixo Estresse/Positivo).
    """
    stress_words = [
        "difícil",
        "estresse",
        "frustrada",
        "cobrança",
        "não consigo",
        "pressão",
        "perdendo",
    ]

    # Score base aleatório para simulação (variabilidade)
    score = random.uniform(-0.1, 0.4)

    # Lógica de ajuste baseada em palavras-chave (simulando a complexidade do modelo)
    if any(word in text.lower() for word in stress_words):
        score -= 0.6  # Reduz o score se houver palavras de estresse

    # Garante que o score esteja no range [-1.0, 1.0]
    final_score = max(-1.0, min(1.0, score))
    return final_score


def suggest_alternative(score, cargo):
    """Gera uma alternativa/sugestão de suporte baseada no score de estresse e cargo."""
    if score < -0.3:
        if cargo == 'SDR':
            return (
                "A IA detectou alto estresse. Sugerimos usar o GPT para aprimorar 5 e-mails de decisores "
                "e buscar novos contatos no LinkedIn, focando em diversificar os canais."
            )

        # Closer / Engenheiro
        return (
            "A IA detectou alto estresse. Sugerimos fazer uma pausa de 10 minutos. "
            "Revise o passo a passo da documentação no 'Copilot' para simplificar sua próxima proposta/ projeto."
        )

    if score > 0.3:
        return (
            "Ótimo estado de ânimo! Continue assim e compartilhe sua estratégia de sucesso "
            "com a equipe."
        )

    return (
        "Estado neutro. Lembre-se de priorizar as atividades mais críticas "
        "para garantir os pontos de Gamificação."
    )


# ==============================================================================
# REQUISITO: GAMIFICAÇÃO & Integração Principal
# ==============================================================================


def registrar_log_estresse_e_pontuar(id_funcionario, problema_descrito, pontualidade_ok=True):
    """
    Função principal que integra ML, Banco de Dados e Lógica de Gamificação.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Obter informações do funcionário (para sugestão específica)
    cursor.execute(
        "SELECT cargo FROM FUNCIONARIOS WHERE id_funcionario = ?",
        (id_funcionario,),
    )
    result = cursor.fetchone()
    if not result:
        print(f"Funcionário com ID {id_funcionario} não encontrado.")
        conn.close()
        return

    cargo = result[0]

    # 2. Análise de Sentimento (ML)
    score = analyze_sentiment(problema_descrito)
    sugestao = suggest_alternative(score, cargo)

    # 3. Gamificação: Cálculo da Pontuação
    pontos_ganhos = 0

    # Bonificação 1: Pontualidade (Bater ponto no horário)
    if pontualidade_ok:
        pontos_ganhos += 5
        print("Bônus: +5 pontos por Pontualidade!")

    # Bonificação 2: Atividades não vencidas
    # Verifica se o funcionário tem atividades VENCIDAS (Status = 'VENCIDA')
    cursor.execute(
        "SELECT COUNT(*) FROM ATIVIDADES WHERE id_funcionario = ? AND status = 'VENCIDA'",
        (id_funcionario,),
    )
    vencidas = cursor.fetchone()[0]

    if vencidas == 0:
        pontos_ganhos += 10
        print("Bônus: +10 pontos por 100% das Atividades em Dia!")

    # 4. Inserir Log de Estresse (BD)
    cursor.execute(
        """
        INSERT INTO LOG_ESTRESSE (id_funcionario, descricao_problema, score_sentimento, sugestao_ia)
        VALUES (?, ?, ?, ?)
        """,
        (id_funcionario, problema_descrito, score, sugestao),
    )

    # 5. Atualizar Pontuação do Funcionário (Gamificação)
    cursor.execute(
        """
        UPDATE FUNCIONARIOS SET pontos_gamificacao = pontos_gamificacao + ? WHERE id_funcionario = ?
        """,
        (pontos_ganhos, id_funcionario),
    )

    conn.commit()
    conn.close()
    print("\n--- RELATÓRIO DE SUPORTE ---")
    print(f"Score de Estresse (IA): {score:.2f} (Entre -1.0 e 1.0)")
    print(f"Sugestão da IA: {sugestao}")
    print(f"Pontos Ganhos Nesta Rodada: {pontos_ganhos}")
    print("-----------------------------\n")


# ==============================================================================
# Execução do MVP
# ==============================================================================


if __name__ == '__main__':
    setup_database()
    add_sample_employees()

    # Adicionar uma atividade vencida para João (Closer, id=2) para testar a Gamificação
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    insert_sql = (
        "INSERT INTO ATIVIDADES (id_funcionario, descricao, data_vencimento, status) "
        "VALUES (?, ?, ?, ?)"
    )
    cursor.execute(
        insert_sql,
        (2, "Fechamento de 2ª Proposta Piloto", "2025-11-16", "VENCIDA"),
    )
    conn.commit()
    conn.close()
    print("--- SIMULAÇÃO SDR (ID 1): ALTO ESTRESSE ---")
    # Maria (SDR, ID 1) descreve a frustração
    problema = (
        "Estou frustrada porque pesquiso o dia todo e o decisor nunca me retorna. "
        "A meta é impossível de bater."
    )
    registrar_log_estresse_e_pontuar(
        id_funcionario=1,
        problema_descrito=problema,
        pontualidade_ok=True,
    )

    print("--- SIMULAÇÃO CLOSER (ID 2): ESTRESSE MODERADO, COM ATIVIDADE VENCIDA ---")
    # João (Closer, ID 2) descreve uma dificuldade
    problema2 = (
        "Tive dificuldades em contornar uma objeção de custo hoje. "
        "O cliente está resistente."
    )
    registrar_log_estresse_e_pontuar(
        id_funcionario=2,
        problema_descrito=problema2,
        pontualidade_ok=False,  # Perde bônus de pontualidade
    )

    print("--- RESULTADO FINAL DE PONTUAÇÃO ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, pontos_gamificacao, cargo FROM FUNCIONARIOS")
    for nome, pontos, cargo in cursor.fetchall():
        print(f"{nome} ({cargo}): {pontos} pontos.")

    conn.close()
