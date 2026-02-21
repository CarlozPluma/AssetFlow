-- schema.sql

CREATE TABLE IF NOT EXISTS departamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    centro_custo TEXT
);

CREATE TABLE IF NOT EXISTS colaboradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    cargo TEXT,
    id_departamento INTEGER,
    ativo BOOLEAN DEFAULT 1,
    FOREIGN KEY (id_departamento) REFERENCES departamentos(id)
);

CREATE TABLE IF NOT EXISTS ativos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_patrimonio TEXT UNIQUE NOT NULL,
    tipo TEXT NOT NULL,
    marca TEXT,
    modelo TEXT,
    num_serie TEXT UNIQUE,
    especificacoes TEXT,
    data_compra DATE,
    valor_compra DECIMAL(10,2),
    status TEXT CHECK(status IN ('Disponível', 'Em Uso', 'Manutenção', 'Descarte')) DEFAULT 'Disponível',
    observacoes TEXT,
    responsavel_atual TEXT
);

-- Adicione as outras tabelas (movimentacoes, manutencoes) e a VIEW aqui...

-- Tabela de Atribuições (O vínculo entre o Ativo e o Colaborador)
CREATE TABLE IF NOT EXISTS atribuicoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ativo INTEGER,
    colaborador_id INTEGER,
    data_entrega DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_devolucao DATETIME,
    status_termo TEXT DEFAULT 'Pendente',
    FOREIGN KEY (id_ativo) REFERENCES ativos(id),
    FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL, -- Em um sistema real, usaríamos hash (PBKDF2)
    role TEXT DEFAULT 'tecnico'
);

CREATE TABLE IF NOT EXISTS equipamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_equipamento TEXT NOT NULL,
    tipo TEXT NOT NULL,
    patrimonio TEXT UNIQUE NOT NULL,
    responsavel_id INTEGER,
    FOREIGN KEY (responsavel_id) REFERENCES usuarios (id)
);

-- Criar um usuário padrão para teste (Admin / admin123)
INSERT OR IGNORE INTO usuarios (username, password, role) VALUES ('admin', 'admin123', 'admin');

-- Garante que a versão antiga seja removida antes de criar a nova
DROP VIEW IF EXISTS vw_resumo_inventario; 

CREATE VIEW vw_resumo_inventario AS
SELECT 
    a.tag_patrimonio,
    a.tipo,
    a.modelo,
    a.status,
    COALESCE(c.nome, 'DISPONÍVEL') as responsavel_atual
FROM ativos a
LEFT JOIN atribuicoes atr ON a.id = atr.id_ativo AND atr.data_devolucao IS NULL
LEFT JOIN colaboradores c ON atr.colaborador_id = c.id;