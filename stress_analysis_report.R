user_lib <- Sys.getenv('R_LIBS_USER')
if (user_lib == '') user_lib <- file.path(Sys.getenv('HOME'), 'R', 'library')
if (!dir.exists(user_lib)) dir.create(user_lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(user_lib, .libPaths()))
required <- c('RSQLite', 'dbplyr', 'dplyr', 'ggplot2')
for (pkg in required) if (!require(pkg, quietly = TRUE)) install.packages(pkg, repos = 'https://cloud.r-project.org', lib = user_lib)

library(RSQLite)
library(dbplyr)
library(dplyr)
library(ggplot2)

db_path <- 'ai_sales_copilot.db'
con <- dbConnect(RSQLite::SQLite(), dbname = db_path)

funcionarios_df <- dbReadTable(con, 'FUNCIONARIOS')
log_estresse_df <- dbReadTable(con, 'LOG_ESTRESSE')

if (nrow(log_estresse_df) > 0) {
  dados_analise <- log_estresse_df %>% left_join(funcionarios_df, by = 'id_funcionario')
  bem_estar_por_cargo <- dados_analise %>% group_by(cargo) %>% summarise(media_sentimento = mean(score_sentimento, na.rm = TRUE), num_logs = n()) %>% arrange(media_sentimento)
  p_estresse <- ggplot(bem_estar_por_cargo, aes(x = reorder(cargo, media_sentimento), y = media_sentimento, fill = cargo)) + geom_col() + geom_hline(yintercept = 0, linetype = 'dashed', color = 'red') + labs(title = 'Nível Agregado de Estresse por Cargo', x = 'Cargo', y = 'Score Médio') + coord_flip() + theme_minimal()
  ggsave('dashboard_estresse_por_cargo.png', plot = p_estresse, width = 8, height = 5)
  p_simple <- ggplot(bem_estar_por_cargo, aes(x = cargo, y = media_sentimento, fill = cargo)) + geom_col() + theme_minimal() + labs(title = 'Média de Score de Sentimento por Cargo', x = 'Cargo', y = 'Score médio')
  ggsave('stress_by_cargo.png', plot = p_simple, width = 8, height = 5)
}

if (nrow(funcionarios_df) > 0) {
  kpi <- funcionarios_df %>% group_by(cargo) %>% summarise(tempo_manual = mean(tempo_operacional_manual, na.rm = TRUE), tempo_reduzido = mean(tempo_reduzido_copilot, na.rm = TRUE)) %>% mutate(pct_reducao = ifelse(tempo_manual > 0, (tempo_manual - tempo_reduzido) / tempo_manual * 100, 0))
  p_kpi <- ggplot(kpi, aes(x = reorder(cargo, pct_reducao), y = pct_reducao, fill = cargo)) + geom_col() + labs(title = 'Percentual de Redução de Tempo Operacional por Cargo', x = 'Cargo', y = '% Redução') + theme_minimal()
  ggsave('kpi_reducao_tempo.png', plot = p_kpi, width = 8, height = 5)
  p_eff <- ggplot(kpi, aes(x = reorder(cargo, pct_reducao), y = pct_reducao, fill = cargo)) + geom_col() + geom_text(aes(label = paste0(round(pct_reducao, 1), '%')), vjust = -0.5) + labs(title = 'Redução Percentual de Tempo Operacional por Cargo', x = 'Cargo', y = '% Redução') + theme_classic()
  ggsave('dashboard_eficiencia_operacional.png', plot = p_eff, width = 8, height = 5)
}

dbDisconnect(con)