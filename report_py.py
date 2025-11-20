import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB = 'ai_sales_copilot.db'


def generate_reports():
    conn = sqlite3.connect(DB)
    df_log = pd.read_sql_query('SELECT * FROM LOG_ESTRESSE', conn)
    df_func = pd.read_sql_query('SELECT * FROM FUNCIONARIOS', conn)
    conn.close()
    if df_log.empty or df_func.empty:
        print('Dados insuficientes para gerar relatório em Python.')
        return
    merged = df_log.merge(df_func, on='id_funcionario', suffixes=('_log', '_func'))
    avg_by_cargo = merged.groupby('cargo')['score_sentimento'].mean().reset_index()
    plt.figure(figsize=(8, 5))
    plt.bar(avg_by_cargo['cargo'], avg_by_cargo['score_sentimento'], color='tab:blue')
    plt.title('Média de Score de Sentimento por Cargo')
    plt.ylabel('Score médio')
    plt.xlabel('Cargo')
    plt.tight_layout()
    plt.savefig('report_py_stress_by_cargo.png')
    print('Gerado report_py_stress_by_cargo.png')
    # KPI
    kpi = (
        df_func
        .groupby('cargo')
        .agg({'tempo_operacional_manual': 'mean', 'tempo_reduzido_copilot': 'mean'})
        .reset_index()
    )
    kpi['pct_reducao'] = (
        (kpi['tempo_operacional_manual'] - kpi['tempo_reduzido_copilot'])
        / kpi['tempo_operacional_manual']
    ) * 100
    plt.figure(figsize=(8, 5))
    plt.bar(kpi['cargo'], kpi['pct_reducao'], color='tab:green')
    plt.title('Percentual de Redução de Tempo Operacional por Cargo')
    plt.ylabel('% Redução')
    plt.xlabel('Cargo')
    plt.tight_layout()
    plt.savefig('report_py_kpi_reducao.png')
    print('Gerado report_py_kpi_reducao.png')


if __name__ == '__main__':
    generate_reports()
