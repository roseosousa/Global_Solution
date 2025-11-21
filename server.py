"""Servidor Flask do projeto Global_Solution.

Versão canônica do servidor para uso local e em contêiner.
Mensagens expostas ao usuário estão em pt-BR.
"""

from datetime import datetime, timedelta
from functools import wraps
import os
import subprocess
import traceback

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

try:
    import jwt
except Exception:
    jwt = None

try:
    from setup_project import verify_password
except Exception:
    def verify_password(plain, hashed):
        try:
            import hashlib
            return hashlib.sha256(plain.encode('utf-8')).hexdigest() == hashed
        except Exception:
            return False


app = Flask(__name__, static_folder='web', static_url_path='/')
CORS(app)

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'ai_sales_copilot.db')
DELIVERABLES_DIR = os.path.join(ROOT, 'deliverables')

JWT_SECRET = os.environ.get('JWT_SECRET', 'please-change-this-secret')
JWT_ALGORITHM = 'HS256'

# Módulos auxiliares opcionais (podem faltar em ambientes de lint/test).
try:
    import seed_fixtures
    import automation_module
    import wellbeing_module
except Exception:
    seed_fixtures = None
    automation_module = None
    wellbeing_module = None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if jwt is None:
            return f(*args, **kwargs)
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'ok': False, 'error': 'Autenticação requerida'}), 401
        token = auth.split(' ', 1)[1].strip()
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'ok': False, 'error': 'Token expirado'}), 401
        except Exception:
            return jsonify({'ok': False, 'error': 'Token inválido'}), 401
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    nome = data.get('nome')
    senha = data.get('senha')

    if not nome:
        return jsonify({'ok': False, 'error': 'O nome é obrigatório'}), 400
    if not senha:
        return jsonify({'ok': False, 'error': 'A senha é obrigatória'}), 400

    try:
        import sqlite3

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            'SELECT id_funcionario, nome, cargo, senha_hash '
            'FROM FUNCIONARIOS WHERE nome = ?',
            (nome,),
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return jsonify({'ok': False, 'error': 'Usuário não encontrado'}), 404

        uid, uname, cargo, stored_hash = row

        if stored_hash and verify_password(senha, stored_hash):
            if jwt is None:
                token = None
            else:
                payload = {
                    'sub': uid,
                    'nome': uname,
                    'cargo': cargo,
                    'exp': datetime.utcnow() + timedelta(hours=1),
                }
                token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
                if isinstance(token, bytes):
                    token = token.decode('utf-8')

            resp = {
                'ok': True,
                'user': {'id': uid, 'nome': uname, 'cargo': cargo},
                'token': token,
            }
            return jsonify(resp)

        return jsonify({'ok': False, 'error': 'Credenciais inválidas'}), 401
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/seed', methods=['POST'])
@token_required
def api_seed():
    try:
        if seed_fixtures is None:
            raise RuntimeError('Módulo de seed não disponível')
        seed_fixtures.seed()
        return jsonify({'ok': True, 'message': 'Seed executado'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/deliverables', methods=['GET'])
@token_required
def api_deliverables():
    try:
        if not os.path.exists(DELIVERABLES_DIR):
            return jsonify({'ok': True, 'files': []})
        files = os.listdir(DELIVERABLES_DIR)
        files = [f for f in files if os.path.isfile(os.path.join(DELIVERABLES_DIR, f))]
        return jsonify({'ok': True, 'files': files})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/deliverables/<path:filename>')
@token_required
def download_deliverable(filename):
    if not os.path.exists(DELIVERABLES_DIR):
        return jsonify({'ok': False, 'error': 'Arquivo não encontrado'}), 404
    return send_from_directory(DELIVERABLES_DIR, filename, as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
