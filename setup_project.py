import sqlite3
from datetime import date

DB_NAME = 'ai_sales_copilot.db'

try:
    import bcrypt
except Exception:
    bcrypt = None


def hash_password(senha: str) -> str:
    """Hash a password using bcrypt when available, else fall back to sha256 hex.

    Returns the hashed password as a string. When bcrypt is available the
    returned value is the bcrypt hash (utf-8 decoded); otherwise a sha256 hex
    digest is returned for compatibility.
    """
    if bcrypt is not None:
        hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    import hashlib

    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored hash.

    If bcrypt is available and the stored hash looks like a bcrypt hash, use
    bcrypt.checkpw. Otherwise, fall back to sha256 comparison.
    """
    if not hashed:
        return False
    if bcrypt is not None and (hashed.startswith('$2') or hashed.startswith('$y$') or hashed.startswith('$b$')):
        try:
            return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    import hashlib

    return hashlib.sha256(plain.encode('utf-8')).hexdigest() == hashed


def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS FUNCIONARIOS (
            id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT NOT NULL,
            senha_hash TEXT,
            pontos_gamificacao INTEGER DEFAULT 0,
            tempo_operacional_manual REAL DEFAULT 180,
            tempo_reduzido_copilot REAL DEFAULT 0,
            nivel_estresse_agregado REAL DEFAULT 0.0
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS CLIENTES (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT NOT NULL,
            cnpj TEXT UNIQUE,
            decisor_nome TEXT,
            decisor_email TEXT,
            data_cadastro DATE,
            responsavel_vendas INTEGER
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS PROPOSTAS (
            id_proposta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            tipo TEXT,
            valor_total REAL,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            caminho_arquivo TEXT,
            FOREIGN KEY(id_cliente) REFERENCES CLIENTES(id_cliente)
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS ATIVIDADES (
            id_atividade INTEGER PRIMARY KEY AUTOINCREMENT,
            id_funcionario INTEGER,
            descricao TEXT,
            data_vencimento DATE,
            status TEXT DEFAULT 'PENDENTE',
            FOREIGN KEY(id_funcionario) REFERENCES FUNCIONARIOS(id_funcionario)
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS LOG_ESTRESSE (
            id_log INTEGER PRIMARY KEY AUTOINCREMENT,
            id_funcionario INTEGER,
            data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            descricao_problema TEXT,
            score_sentimento REAL,
            sugestao_ia TEXT,
            pontos INTEGER DEFAULT 0,
            FOREIGN KEY(id_funcionario) REFERENCES FUNCIONARIOS(id_funcionario)
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS DATASET_TREINAMENTO (
            id_dado INTEGER PRIMARY KEY AUTOINCREMENT,
            texto_problema TEXT NOT NULL,
            label_estresse INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def add_employee_securely(nome, cargo, senha):
    senha_hash = hash_password(senha)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO FUNCIONARIOS (nome, cargo, senha_hash) VALUES (?, ?, ?)", (nome, cargo, senha_hash))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def insert_client(nome_empresa, cnpj, decisor_nome, decisor_email, responsavel_vendas_id=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        insert_sql = (
            "INSERT INTO CLIENTES (nome_empresa, cnpj, decisor_nome, decisor_email, data_cadastro, responsavel_vendas) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        params = (
            nome_empresa,
            cnpj,
            decisor_nome,
            decisor_email,
            date.today().isoformat(),
            responsavel_vendas_id,
        )
        c.execute(insert_sql, params)
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def populate_training_data():
    samples = [
        ("Não consigo agendar nada esta semana, muito frustrado.", 1),
        ("A meta está muito alta e a pressão é grande.", 1),
        ("Tive um ótimo dia e converti leads!", 0),
        ("Dia tranquilo, tudo dentro do esperado.", 0),
        ("Perdendo muito tempo com relatórios manuais.", 1),
        ("A automação ajudou e aumentou minha produtividade.", 0),
    ]
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM DATASET_TREINAMENTO")
    if c.fetchone()[0] == 0:
        insert_sql = (
            "INSERT INTO DATASET_TREINAMENTO (texto_problema, label_estresse) "
            "VALUES (?, ?)"
        )
        c.executemany(insert_sql, samples)
        conn.commit()
    conn.close()


if __name__ == '__main__':
    setup_database()
    add_employee_securely('Maria SDR', 'SDR', 'SDR@2025')
    add_employee_securely('Carlos Closer', 'Closer', 'Closer@2025')
    add_employee_securely('Ana Engenheira', 'Engenheiro', 'Engenheiro@2025')
    populate_training_data()
    cid = insert_client('Tech Solutions Ltda', '12.345.678/0001-90', 'Fernando Silva', 'fernando.s@techsol.com', 2)
    print('Setup concluído. DB:', DB_NAME)
