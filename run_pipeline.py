

"""run_pipeline.py

Script simples para executar o pipeline de demonstração.

Ele é intencionalmente resiliente: importa módulos do projeto com
try/except (para permitir análise estática em ambientes sem dependências)
e tenta executar um relatório em R com fallback para `report_py.py`.
"""

import os
import subprocess
import sys
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'ai_sales_copilot.db')


def run_python_report():
    """Executa report_py.py se presente (fallback quando Rscript não está disponível)."""
    py = os.path.join(ROOT, 'report_py.py')
    if os.path.exists(py):
        print('Executando report_py.py...')
        proc = subprocess.run([sys.executable, py], capture_output=True, text=True)
        print('report_py.py exit:', proc.returncode)
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print('report stderr:', proc.stderr)
    else:
        print('Nenhum script de relatório disponível (report_py.py não encontrado).')


def main():
    """Executa o pipeline de demonstração.

    Passos:
    - importa módulos do projeto (com tolerância a falhas)
    - cria/valida o banco via `setup_project.setup_database()` quando disponível
    - popula fixtures via `seed_fixtures.seed()` quando disponível
    - gera uma proposta com `automation_module.gerar_proposta_comercial()` quando disponível
    - registra wellbeing via `wellbeing_module.registrar_log_estresse_e_pontuar()` quando disponível
    - tenta rodar relatório em R (Rscript), caso contrário executa `report_py.py`
    """

    print('Iniciando pipeline...')

    # Imports opcionais: falha ao importar não deve quebrar a análise estática
    setup_project = None
    seed_fixtures = None
    automation_module = None
    wellbeing_module = None

    try:
        import setup_project as _sp
        setup_project = _sp
    except Exception:
        print('Aviso: módulo setup_project não disponível (continuando)')

    try:
        import seed_fixtures as _sf
        seed_fixtures = _sf
    except Exception:
        print('Aviso: módulo seed_fixtures não disponível (continuando)')

    try:
        import automation_module as _am
        automation_module = _am
    except Exception:
        print('Aviso: módulo automation_module não disponível (continuando)')

    try:
        import wellbeing_module as _wm
        wellbeing_module = _wm
    except Exception:
        print('Aviso: módulo wellbeing_module não disponível (continuando)')

    # 1) Criar/validar DB
    try:
        if setup_project is not None and hasattr(setup_project, 'setup_database'):
            print('Criando/validando banco...')
            setup_project.setup_database()
        else:
            print('setup_project.setup_database() não disponível — pulando criação do DB')
    except Exception as e:
        print('Falha ao criar/validar DB:', e)
        print(traceback.format_exc())

    # 2) Popular fixtures
    try:
        if seed_fixtures is not None and hasattr(seed_fixtures, 'seed'):
            print('Populando fixtures...')
            seed_fixtures.seed()
        else:
            print('seed_fixtures.seed() não disponível — pulando seed')
    except Exception as e:
        print('Falha ao popular fixtures:', e)
        print(traceback.format_exc())

    # 3) Gerar proposta de demonstração
    try:
        if automation_module is not None and hasattr(automation_module, 'gerar_proposta_comercial'):
            print('Gerando proposta de demonstração...')
            path = automation_module.gerar_proposta_comercial(1, 19990, 1)
            print('Proposta gerada em:', path)
        else:
            print('automation_module.gerar_proposta_comercial() não disponível — pulando geração de proposta')
    except Exception as e:
        print('Falha ao gerar proposta:', e)
        print(traceback.format_exc())

    # 4) Registrar wellbeing demo
    try:
        if wellbeing_module is not None and hasattr(wellbeing_module, 'registrar_log_estresse_e_pontuar'):
            print('Registrando wellbeing demo...')
            res = wellbeing_module.registrar_log_estresse_e_pontuar(1, 'pipeline demo')
            print('Resultado wellbeing:', res)
        else:
            print('wellbeing_module.registrar_log_estresse_e_pontuar() não disponível — pulando wellbeing')
    except Exception as e:
        print('Falha ao registrar wellbeing:', e)
        print(traceback.format_exc())

    # 5) Relatório: tentar Rscript, fallback para Python
    try:
        rscript = os.path.join(ROOT, 'stress_analysis_report.R')
        if os.path.exists(rscript):
            print('Tentando rodar relatório em R (Rscript)...')
            try:
                proc = subprocess.run(['Rscript', rscript], capture_output=True, text=True)
                print('Rscript exit:', proc.returncode)
                if proc.stdout:
                    print(proc.stdout)
                if proc.returncode != 0:
                    print('Rscript retornou código diferente de zero — executando fallback Python')
                    run_python_report()
            except FileNotFoundError:
                print('Rscript não encontrado no PATH — usando fallback Python')
                run_python_report()
        else:
            print('R script não existe — executando fallback Python')
            run_python_report()
    except Exception as e:
        print('Erro ao tentar executar relatório:', e)
        print(traceback.format_exc())

    print('Pipeline finalizado.')


if __name__ == '__main__':
    main()
