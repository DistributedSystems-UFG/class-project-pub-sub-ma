from kafka import KafkaConsumer
from const import *
from datetime import datetime
import sys
import json
import mariadb

"""
Definição da mensagem (JSON):
{
    "nomeDispositivo": "",
    "localizacao": ""
}

Definicao da mensagem (JSON):
{
 "localizacao": "",
 "nomeDispositivo": "",
 "data": "yyyy-MM-dd HH:mm:ss",
 "valor": "99.99"
}

Definicao da mensagem de CADASTRO DE DISPOSITIVOS (JSON):
tipoDispositivo: 1 - LED, 2 - Sensor Temperatura, 3 - Sensor Umidade, 4 - Sensor Luminosidade
[{
    "localizacao": "",
    "dispositivos": [
        {
         "nomeDispositivo": ""
         "tipoDispositivo": "0"
        }
    ],
},]
"""

topicos = ['temperatura', 'umidade', 'luminosidade', 'dispositivos']

def getConnection():
    try:
        conn = mariadb.connect(
            user="root",
            password="root",
            host="localhost",
            port=3306,
            database="sensor"

        )
        
        return conn
    except mariadb.Error as e:
        print(f"Erro ao se conectar ao banco: {e}")
        sys.exit(1)

def decodeMessage(msg : str):
    dados = json.loads(msg)
    return dados

def persistirDados(dados : dict):
    idLocal = consultaLocal(dados['localizacao'])
    sqlConsultaId = 'SELECT id, id_local FROM Dispositivos WHERE id_local = ? AND nomeDispositivo = ? LIMIT 1'
    sql = 'INSERT INTO DadosSensores (data, id_sensor, valor) VALUES (?, ?, ?)'
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sqlConsultaId, (idLocal, dados['nomeDispositivo'],))
    idSensor = 0
    for id, id_local in cursor:
        idSensor = id
    print(idSensor)
    print((dados['localizacao'],dados['nomeDispositivo'],))
    data = datetime.strptime(dados['data'], '%d/%m/%Y %H:%M:%S')
    cursor.execute(sql, (data, idSensor, dados['valor'],))
    conn.commit()
    conn.close()

def consultaLocal(nomeLocal: str):
    sqlConsultaLocal = 'SELECT id FROM Locais WHERE nomeLocal = ? '
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sqlConsultaLocal, (nomeLocal,))
    idLocal = None
    for id in cursor:
        idLocal = id[0]
    conn.close()
    return idLocal

def cadastrarNovoLocal(nomeLocal: str):
    sql = 'INSERT INTO Locais (nomeLocal) VALUES (?)'
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql, (nomeLocal,))
    conn.commit()
    conn.close()
    return consultaLocal(nomeLocal)

def cadastrarDispositivos(msg: str):
    cadastro = decodeMessage(msg)
    for local in cadastro:
        idLocal = consultaLocal(local['localizacao'])
        if idLocal is None:
            idLocal = cadastrarNovoLocal(local['localizacao'])
        sql = 'INSERT IGNORE  INTO Dispositivos (id_local, tipoDispositivo, nomeDispositivo, estado) VALUES ( ?, ?, ?, ?)'
        for dispositivo in local['dispositivos']:
            conn = getConnection()
            cursor = conn.cursor()
            cursor.execute(sql, (idLocal, dispositivo['tipoDispositivo'], dispositivo['nomeDispositivo'], False if dispositivo['tipoDispositivo'] == 1 else None,))
            conn.commit()
            conn.close()


if __name__ == '__main__':
    consumer = KafkaConsumer(bootstrap_servers=[BROKER_ADDR + ':' + BROKER_PORT])
    consumer.subscribe(topicos)
    for msg in consumer:
        print(msg.value.decode())
        if msg.topic == 'dispositivos':
           cadastrarDispositivos(msg.value.decode()) 
        else :
            dados  = decodeMessage(msg.value.decode())
            persistirDados(dados)