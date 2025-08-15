-- Arquivo: optimization_indexes.sql
-- Tracing ID: INDEX_OPTIMIZATION_20250127_001
-- Data: 2025-01-27
-- Versão: 1.0
-- Status: 🔴 CRÍTICO - Criação de Índices Otimizados
-- Justificativa: Índices criados com base nas queries críticas identificadas pelo script de análise de performance.

-- Índices para tabela keywords
CREATE INDEX IF NOT EXISTS idx_keywords_domain ON keywords(domain);
-- Justificativa: Otimiza buscas por domínio (query: SELECT * FROM keywords WHERE domain = ?)

CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);
-- Justificativa: Otimiza buscas por palavra-chave (query: SELECT * FROM keywords WHERE keyword LIKE ?)

CREATE INDEX IF NOT EXISTS idx_keywords_position ON keywords(position);
-- Justificativa: Otimiza buscas por posição (query: SELECT * FROM keywords WHERE position > ?)

-- Índices para tabela analytics
CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date);
-- Justificativa: Otimiza buscas por intervalo de datas (query: SELECT * FROM analytics WHERE date BETWEEN ? AND ?)

CREATE INDEX IF NOT EXISTS idx_analytics_keyword_id ON analytics(keyword_id);
-- Justificativa: Otimiza buscas por keyword_id (query: SELECT * FROM analytics WHERE keyword_id = ?)

-- Índices para tabela payments
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
-- Justificativa: Otimiza buscas por usuário (query: SELECT * FROM payments WHERE user_id = ?)

CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
-- Justificativa: Otimiza buscas por status de pagamento (query: SELECT * FROM payments WHERE status = ?)

-- Índices para tabela users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- Justificativa: Otimiza buscas por e-mail (query: SELECT * FROM users WHERE email = ?)

-- O índice primário (PRIMARY KEY) já cobre buscas por id em users (query: SELECT * FROM users WHERE id = ?)
-- Caso necessário, revisar índices compostos para queries multi-coluna 