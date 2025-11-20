import sqlite3
from datetime import datetime, timedelta, date
from pathlib import Path
from fpdf import FPDF

DB_PATH = 'ai_sales_copilot.db'


def _ensure_outputs_dir():
    out = Path('outputs')
    out.mkdir(exist_ok=True)
    return out


def _get_employee_name(id_funcionario):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT nome FROM FUNCIONARIOS WHERE id_funcionario = ?', (id_funcionario,))
    r = c.fetchone()
    conn.close()

    return r[0] if r else 'Responsavel Desconhecido'


def gerar_proposta_comercial(id_cliente, valor, id_responsavel):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT nome_empresa, decisor_nome, decisor_email FROM CLIENTES WHERE id_cliente = ?', (id_cliente,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    nome_empresa, decisor_nome, decisor_email = row
    nome_responsavel = _get_employee_name(id_responsavel)
    out = _ensure_outputs_dir()
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = out / f'Proposta_{id_cliente}_{ts}.pdf'
    pdf = FPDF()
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Proposta Comercial - AI Sales Copilot', 0, 1, 'C')
    pdf.ln(6)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Cliente: {nome_empresa}', 0, 1)
    decisor_info = f'{decisor_nome} - {decisor_email}'
    pdf.cell(0, 8, f'Decisor: {decisor_info}', 0, 1)
    pdf.cell(0, 8, f'Data: {date.today().strftime("%d/%m/%Y")}', 0, 1)
    pdf.ln(6)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Resumo da Proposta', 0, 1)
    pdf.set_font('Arial', '', 12)
    project_text = f'Projeto com valor total de R$ {valor:,.2f}. Entrega conforme escopo acordado.'
    pdf.multi_cell(0, 8, project_text)
    pdf.ln(6)
    pdf.cell(0, 8, f'Elaborado por: {nome_responsavel}', 0, 1)
    pdf.output(str(filename))
    insert_params = (id_cliente, 'Comercial', valor, str(filename))
    insert_sql = (
        'INSERT INTO PROPOSTAS (id_cliente, tipo, valor_total, caminho_arquivo) '
        'VALUES (?, ?, ?, ?)'
    )
    c.execute(insert_sql, insert_params)
    conn.commit()
    conn.close()

    return str(filename)


def gerar_proposta_customizacao(requisitos, horas_estimadas, id_cliente=None):
    out = _ensure_outputs_dir()
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = out / f'Proposta_Customizacao_{ts}.txt'
    content = []
    content.append('PROPOSTA DE CUSTOMIZACAO')
    if id_cliente:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT nome_empresa, decisor_nome FROM CLIENTES WHERE id_cliente = ?', (id_cliente,))
        row = c.fetchone()
        conn.close()
        if row:
            content.append(f'Cliente: {row[0]}')
            content.append(f'Decisor: {row[1]}')
    content.append(f'Data: {date.today().isoformat()}')
    content.append('\nREQUISITOS TECNICOS:')
    content.append(requisitos)
    content.append('\nESTIMATIVA DE ESFORCO:')
    content.append(f'{horas_estimadas} horas')
    out_text = '\n\n'.join(content)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(out_text)
    if id_cliente:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        insert_params = (id_cliente, 'Customizacao', None, str(filename))
        insert_sql = (
            'INSERT INTO PROPOSTAS (id_cliente, tipo, valor_total, caminho_arquivo) '
            'VALUES (?, ?, ?, ?)'
        )
        c.execute(insert_sql, insert_params)
        conn.commit()
        conn.close()
    return str(filename)


def generate_bpmn_diagram(titulo, descricao):
    descricao_lower = descricao.lower()
    keywords = [
        'customizacao',
        'customizacao',
        'integracao',
        'api',
        'workflow',
        'integracao',
    ]
    is_complex = any(k in descricao_lower for k in keywords)
    lines = [f'BPMN: {titulo}', '', 'START']
    lines.append('Task: Validar escopo de proposta')
    if is_complex:
        lines.append('Gateway: Requer analise tecnica? -> SIM')
        lines.append('Task: Engenheiro avalia integracao e APIs')
        lines.append('Task: Gerar diagrama tecnico e plano de testes')
        lines.append('Task: Validar com cliente')
    else:
        lines.append('Gateway: Requer analise tecnica? -> NAO')
        lines.append('Task: Closer finaliza contrato padrao')
    lines.append('END')
    out = _ensure_outputs_dir()
    filename = out / f'BPMN_{titulo.replace(" ", "_")}.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return str(filename)


def gerar_cronograma_implementacao(id_cliente, data_inicio):
    start = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    etapas = [
        ('Setup', 'Alinhamento tecnico e configuracoes iniciais'),
        ('Piloto', 'Execucao do piloto e coleta de feedback'),
        ('Ajustes', 'Correcao e melhoria conforme piloto'),
        ('Treinamento', 'Treinamento final e documentacao'),
    ]
    out = _ensure_outputs_dir()
    filename = out / f'Cronograma_{id_cliente}_{data_inicio}.txt'
    lines = [f'Cronograma de Implementacao - Cliente {id_cliente}', f'Inicio: {start.isoformat()}', '']
    current = start
    for i, (fase, desc) in enumerate(etapas, start=1):
        end = current + timedelta(days=6)
        lines.append(f'Semana {i}: {current.isoformat()} a {end.isoformat()}')
        lines.append(f'  Fase: {fase}')
        lines.append(f'  Atividades: {desc}')
        lines.append('')
        current = end + timedelta(days=1)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return str(filename)
