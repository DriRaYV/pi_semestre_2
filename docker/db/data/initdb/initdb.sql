CREATE TABLE qualidade_agua (
    id SERIAL PRIMARY KEY,

    produto VARCHAR(50),
    turbidez NUMERIC(10,2),
    fita_ph NUMERIC(10,2),
    ph_real NUMERIC(10,2),
    temperatura NUMERIC(10,2),
    umidade NUMERIC(10,2),
    cor VARCHAR(20),
    ph_tensao NUMERIC(10,2),
    constante INTEGER,

    data_registro TIMESTAMP DEFAULT NOW()
);


INSERT INTO qualidade_agua
(produto, turbidez, fita_ph, ph_real, temperatura, umidade, cor, ph_tensao, constante)
VALUES
('Limão', 366.39, 2.5, 3.50, NULL, NULL, 'Verde', 1.25, 5642),
('Amaciante', 731.15, 6, 6.88, NULL, NULL, 'Azul', 2.46, 5642),
('Bicarbonato', 109.28, 9, 6.05, NULL, NULL, 'Marrom', 2.16, 5642),
('Vinagre', 136, 5, 3.30, NULL, NULL, 'Laranja', 1.18, 5642),
('Água Bebedouro', 27.78, 5, 6.30, NULL, NULL, 'Cinza', 2.25, 5642);
