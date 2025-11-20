import sqlite3
from setup_project import setup_database, populate_training_data, add_employee_securely, insert_client
from automation_module import gerar_proposta_comercial
from wellbeing_module import registrar_log_estresse_e_pontuar


def main():
    setup_database()
    populate_training_data()
    uid = add_employee_securely('Tester POC', 'SDR', 'tester@2025')
    if not uid:
        conn = sqlite3.connect('ai_sales_copilot.db')
        c = conn.cursor()
        c.execute("SELECT id_funcionario FROM FUNCIONARIOS WHERE nome = ?", ('Tester POC',))
        r = c.fetchone()
        uid = r[0] if r else 1
        conn.close()
    cid = insert_client(
        'ACME Test Ltda',
        '00.000.000/0001-00',
        'Alice Test',
        'alice@test.com',
        uid,
    )
    print('IDs gerados -> funcionario:', uid, 'cliente:', cid)
    proposta = gerar_proposta_comercial(cid, 12345.67, uid)
    print('Proposta gerada em:', proposta)
    problema = 'Estou muito frustrado com as metas e sobrecarregado'
    resultado = registrar_log_estresse_e_pontuar(
        uid,
        problema,
        pontualidade_ok=True,
    )
    print('Resultado registro estresse:', resultado)


if __name__ == '__main__':
    main()
