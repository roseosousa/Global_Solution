# AI Sales Copilot — POC

Breve: prova de conceito com módulos para criação de banco de dados (SQLite), automação de propostas (PDF), um módulo de wellbeing/sentimento e um relatório gerencial em R (com fallback em Python).

Pré-requisitos

- Python 3.8+ e pip
- (Opcional) R + Rscript para executar `stress_analysis_report.R` — o repositório também contém um fallback em Python (`report_py.py`).

Instalação rápida

```bash
pip install -r '/home/jenifer/Área de Trabalho/Global_Solution/requirements.txt'
```

Rodando o pipeline (rápido)

```bash
python3 run_pipeline.py
```

Isso:
# AI Sales Copilot — POC

Este repositório contém uma prova de conceito com:
- criação e populamento de um SQLite local (`ai_sales_copilot.db`)
- geração de propostas (PDF)
- módulo de wellbeing (análise de sentimento simulada)
- relatório gerencial em R (com fallback Python)

Leia `INSTALL.md` para instruções de instalação, execução local e uso com Docker.

Principais pontos:
- Servidor/API: `server.py` (Flask)
- UI: `web/` (one-page)
- Pipeline de demonstração: `run_pipeline.py`
- Scripts de relatório: `stress_analysis_report.R` (R) e `report_py.py` (Python fallback)

Para um guia de instalação e execução veja `INSTALL.md`.
```bash
