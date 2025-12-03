CREATE TABLE grupos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
);

CREATE TABLE localizacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    latitude DECIMAL(12,6),
    longitude DECIMAL(12,6),
    descricao TEXT
);

CREATE TABLE amostras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_inclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grupo_id INT NOT NULL,
    localizacao_id INT NOT NULL,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
    FOREIGN KEY (localizacao_id) REFERENCES localizacao(id)
);

CREATE TABLE qualidade_agua (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amostra_id INT NOT NULL UNIQUE,
    temperatura_coleta DECIMAL(5,2),
    temperatura_analise DECIMAL(5,2),
    turbidez DECIMAL(10,2),
    ph_fita DECIMAL(4,2),
    ph_arduino DECIMAL(4,2),
    umidade DECIMAL(5,2),
    FOREIGN KEY (amostra_id) REFERENCES amostras(id)
);

CREATE TABLE condutividade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amostra_id INT NOT NULL UNIQUE,
    condutividade DECIMAL(10,2),
    FOREIGN KEY (amostra_id) REFERENCES amostras(id)
);
