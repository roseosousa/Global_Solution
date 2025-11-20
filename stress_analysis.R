# Requisito: Linguagem R e Análise de Dados
library(RSQLite)
library(dplyr)
library(ggplot2)

# --- 1. Conexão ao Banco de Dados ---
db_name <- "wellbeing_copilot.db" 
# Certifique-se de que o script Python (wellbeing_copilot.py) foi executado primeiro.
con <- dbConnect(RSQLite::SQLite(), dbname = db_name)

# Carregar dados
funcionarios_df <- dbReadTable(con, "FUNCIONARIOS")
log_estresse_df <- dbReadTable(con, "LOG_ESTRESSE")

dbDisconnect(con)

# Juntar dados de estresse com informações dos funcionários
dados_analise <- log_estresse_df %>%
  left_join(funcionarios_df, by = "id_funcionario")

# --- 2. Análise Estatística: Estresse Agregado por Cargo ---

# Calcula a média do score de sentimento por cargo
bem_estar_por_cargo <- dados_analise %>%
  group_by(cargo) %>%
  summarise(
    media_sentimento = mean(score_sentimento, na.rm = TRUE), # Score: -1 (Estresse) a 1 (Satisfação)
    num_logs = n(),
    media_pontos = mean(pontos_gamificacao.y, na.rm = TRUE) # Pontos médios da equipe (y = da tabela funcionarios)
  ) %>%
  arrange(media_sentimento)

print("--- DASHBOARD GERENCIAL: ÍNDICE DE BEM-ESTAR ---")
print(bem_estar_por_cargo)

# --- 3. Visualização (Para o Relatório/Vídeo) ---

# Cria um gráfico que demonstra o nível de estresse (sentimento) por cargo.
grafico_estresse_cargo <- ggplot(bem_estar_por_cargo, aes(x = reorder(cargo, media_sentimento), y = media_sentimento, fill = cargo)) +
  geom_bar(stat = "identity") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "red", linewidth = 1) +
  labs(
    title = "Nível Agregado de Estresse por Cargo (AI Well-being Copilot)",
    subtitle = "Score Médio de Sentimento: SDRs são o ponto de maior atenção.",
    x = "Cargo",
    y = "Score Médio de Sentimento (-1.0 a 1.0)"
  ) +
  theme_minimal() +
  scale_fill_manual(values = c("SDR" = "#dc3545", "Closer" = "#ffc107", "Engenheiro" = "#28a745")) +
  coord_flip() # Melhor para leitura
  
# Salva o gráfico PNG para inclusão no relatório PDF
ggsave("dashboard_estresse_por_cargo.png", plot = grafico_estresse_cargo, width = 8, height = 5)

print("\nAnálise completa. Gráfico 'dashboard_estresse_por_cargo.png' gerado para o Dashboard Gerencial.")

# --- C. Nova Análise: Eficiência Operacional ---
# Requisito: KPI Gerencial (Tempo Operacional Reduzido)

eficiencia_df <- funcionarios_df %>%
  mutate(
    tempo_economizado = tempo_reduzido_copilot, # Valor simulado em minutos/semana
    percentual_reducao = (tempo_economizado / tempo_operacional_manual) * 100
  ) %>%
  select(cargo, tempo_operacional_manual, tempo_economizado, percentual_reducao)

print("\n[C. Eficiência Operacional Simulado (Redução de Tempo)]")
print(eficiencia_df)

# Visualização da Redução de Tempo
grafico_eficiencia <- ggplot(eficiencia_df, aes(x = reorder(cargo, percentual_reducao), y = percentual_reducao, fill = cargo)) +
  geom_bar(stat = "identity") +
  labs(
    title = "Redução de Tempo Operacional por Cargo (Simulado - Minutos/Semana)",
    subtitle = "Métrica para justificar o investimento no AI Copilot.",
    x = "Cargo",
    y = "Redução Percentual de Tempo Gasto em Tarefas Repetitivas"
  ) +
  theme_classic()

ggsave("dashboard_eficiencia_operacional.png", plot = grafico_eficiencia, width = 8, height = 5)

print("\nGráfico 'dashboard_eficiencia_operacional.png' gerado.")