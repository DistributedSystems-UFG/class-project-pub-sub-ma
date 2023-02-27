-- tipoDispositivo: 1 - LED, 2 - Sensor Temperatura, 3 - Sensor Umidade, 4 - Sensor Luminosidade
CREATE TABLE Locais (
	id BIGINT NOT NULL AUTO_INCREMENT,
	nomeLocal VARCHAR(30) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT UC_NomeLoc UNIQUE (nomeLocal)
);

CREATE TABLE Dispositivos (
	id BIGINT NOT NULL AUTO_INCREMENT,
	id_local BIGINT NOT NULL,
	tipoDispositivo INTEGER NOT NULL,
	nomeDispositivo VARCHAR(30) NOT NULL,
	estado BOOLEAN,
	PRIMARY KEY (id),
	FOREIGN KEY (id_local) REFERENCES Locais(id),
	CONSTRAINT UC_NomeDisp UNIQUE (id_local, nomeDispositivo)
);

CREATE TABLE Usuarios (
	id BIGINT NOT NULL AUTO_INCREMENT,
	usuario VARCHAR(30) NOT NULL,
	senha VARCHAR(200) NOT NULL,
	nome VARCHAR(30) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT UC_User UNIQUE (usuario)
);

--senha123456
INSERT INTO Usuarios (usuario, senha, nome) VALUES ('ariel', '8a9f8cb0f26e12555e11a1683e5b4d5f5b25331afa8cc98c0c10def92790dcb8', 'Ariel Marte');
--batata123
INSERT INTO Usuarios (usuario, senha, nome) VALUES ('marco', '44e8e39e98069dd184fa75269329693d6c69326d276b2b7436b39f388dc3cce5', 'Marco');
--ufg123
INSERT INTO Usuarios (usuario, senha, nome) VALUES ('gustavo', 'cc3bae3976aa5948e6c62fe52088408f8ff337a991987f2e1c5bfa98851c374b', 'Gustavo');

CREATE TABLE DispositivosUsuario(
	id_usuario BIGINT NOT NULL,
	id_dispositivo BIGINT NOT NULL,
	FOREIGN KEY (id_usuario) REFERENCES Usuarios(id),
	FOREIGN KEY (id_dispositivo) REFERENCES Dispositivos(id)
);

INSERT INTO DispositivosUsuario VALUES (1, 1);
INSERT INTO DispositivosUsuario VALUES (1, 2);
INSERT INTO DispositivosUsuario VALUES (1, 3);
INSERT INTO DispositivosUsuario VALUES (1, 4);
INSERT INTO DispositivosUsuario VALUES (1, 5);
INSERT INTO DispositivosUsuario VALUES (1, 6);
INSERT INTO DispositivosUsuario VALUES (1, 7);
INSERT INTO DispositivosUsuario VALUES (1, 8);
INSERT INTO DispositivosUsuario VALUES (1, 9);
INSERT INTO DispositivosUsuario VALUES (2, 7);
INSERT INTO DispositivosUsuario VALUES (2, 8);
INSERT INTO DispositivosUsuario VALUES (2, 9);
INSERT INTO DispositivosUsuario VALUES (3, 4);
INSERT INTO DispositivosUsuario VALUES (3, 5);
INSERT INTO DispositivosUsuario VALUES (3, 6);
INSERT INTO DispositivosUsuario VALUES (3, 7);
INSERT INTO DispositivosUsuario VALUES (3, 8);
INSERT INTO DispositivosUsuario VALUES (3, 9);

CREATE TABLE DadosSensores (
	id BIGINT NOT NULL AUTO_INCREMENT,
	data DATETIME NOT NULL,
	id_sensor BIGINT NOT NULL,
	valor FLOAT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (id_sensor) REFERENCES Dispositivos(id)
);

CREATE TABLE Sessao (
	id BIGINT NOT NULL AUTO_INCREMENT,
	id_usuario BIGINT NOT NULL,
	token VARCHAR(200) NOT NULL,
	funcionalidade VARCHAR(200),
	data_expiracao DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (id_usuario) REFERENCES Usuarios(id),
	CONSTRAINT UC_Token UNIQUE (token, id_usuario)
);