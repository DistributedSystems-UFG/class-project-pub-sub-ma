import grpc
from kafka import KafkaProducer
from concurrent import futures
import mariadb
import sys
import json
from datetime import datetime, timedelta
import SensorService_pb2
import SensorService_pb2_grpc
from const import *
import hashlib
import uuid

"""
Definição da mensagem ACIONAR LED (JSON):
{
    "nomeDispositivo": "",
    "localizacao": ""
}

Definição da string funcionalidade:
funcao|localizacao|nomeDispositivo
"""

class SensorServer(SensorService_pb2_grpc.SensorServiceServicer):
    def __init__(self):
        self.usuario = None

    def ListarLeiturasSensores(self, request, context):
        if not self.is_authenticated(context):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid username or password')
            return SensorService_pb2.ListaDispositivos()

        conn = getConnection()
        sql = "SELECT D.id, DS.data, L.nomeLocal, D.nomeDispositivo, D.tipoDispositivo, DS.valor FROM DadosSensores AS DS INNER JOIN Dispositivos AS D ON D.id = DS.id_sensor INNER JOIN Locais AS L ON D.id_local = L.id "
        sql = sql + montarJoinCondicionalUsuario(self.usuario)
        sqlCond, paramCond = requestParaCondicional(request)
        if paramCond:
            sql = sql + " WHERE " + sqlCond
        params = tuple(paramCond)
        cur = conn.cursor()
        cur.execute(sql, params)
        listaDadosRetorno = SensorService_pb2.ListaDados()
        for id, data, nomeLocal, nomeDispositivo, tipoDispositivo, valor in cur:
            dadoRetorno = SensorService_pb2.Dado(id=id, data=data.strftime("%d/%m/%Y, %H:%M:%S"), localizacao=nomeLocal, nomeDispositivo=nomeDispositivo, tipoDispositivo=tipoDispositivo, valor=valor)
            listaDadosRetorno.dados.append(dadoRetorno)
        conn.close()    
        return listaDadosRetorno
        
        
    def ConsultarUltimaLeituraSensor(self, request, context):
        if not self.is_authenticated(context):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid username or password')
            return SensorService_pb2.ListaDispositivos()

        conn = getConnection()
        sql = "SELECT D.id, DS.data, L.nomeLocal, D.nomeDispositivo, D.tipoDispositivo, DS.valor FROM DadosSensores AS DS INNER JOIN Dispositivos AS D ON D.id = DS.id_sensor INNER JOIN Locais AS L ON D.id_local = L.id "
        sql = sql + montarJoinCondicionalUsuario(self.usuario)
        sqlCond, paramCond = requestParaCondicional(request)
        if paramCond:
            sql = sql + " WHERE " + sqlCond
        sql = sql + " ORDER BY DS.data DESC LIMIT 1"
        params = tuple(paramCond)
        cur = conn.cursor()
        cur.execute(sql, params)
        dadoRetorno = SensorService_pb2.Dado()
        for id, data, nomeLocal, nomeDispositivo, tipoDispositivo, valor in cur:
            dadoRetorno = SensorService_pb2.Dado(id=id, data=data.strftime("%d/%m/%Y, %H:%M:%S"), localizacao=nomeLocal, nomeDispositivo=nomeDispositivo, tipoDispositivo=tipoDispositivo, valor=valor)
        conn.close()    
        return dadoRetorno
    
    def AcionarLed(self, request, context):
        if not self.is_authenticated(context):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid username or password')
            return SensorService_pb2.ListaDispositivos()

        conn = getConnection()
        sql = 'SELECT D.id, L.nomeLocal, D.nomeDispositivo, D.estado FROM Dispositivos D INNER JOIN Locais AS L ON D.id_local = L.id  '
        sql = sql + montarJoinCondicionalUsuario(self.usuario) + ' WHERE D.tipoDispositivo = 1 AND L.nomeLocal = ? AND nomeDispositivo = ? LIMIT 1'
        sqlUpdate = 'UPDATE Dispositivos SET estado = ? WHERE id_local = ? AND nomeDispositivo = ?'
        idLocal = consultaLocal(request.localizacao)
        cur = conn.cursor()
        cur.execute(sql, (request.localizacao, request.nomeDispositivo,))
        idLed = None
        for id, nomeLocal, nomeDispositivo, estado in cur:
            idLed = id
        if idLed is None:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid username or password')
            return SensorService_pb2.ListaDispositivos()

        msg = montarMensagemAcionarLed(request.nomeDispositivo, request.localizacao)
        producer = KafkaProducer(bootstrap_servers=[BROKER_ADDR + ':' + BROKER_PORT])
        producer.send('ledcommand', key=msg.encode(), value=str(request.estado).encode())
        cur.execute(sqlUpdate, (request.estado, idLocal, request.nomeDispositivo,))
        conn.commit()
        cur.execute(sql, (request.localizacao, request.nomeDispositivo,))
        ledStatus = None
        for id, nomeLocal, nomeDispositivo, estado in cur:
            ledStatus = SensorService_pb2.LedStatus(estado = estado, nomeDispositivo = nomeDispositivo, localizacao = nomeLocal)
        conn.close()
        return ledStatus

    def ListarLeds(self, request, context):
        if not self.is_authenticated(context):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid username or password')
            return SensorService_pb2.ListaDispositivos()
        
        conn = getConnection()
        sql = 'SELECT D.id, L.nomeLocal, D.nomeDispositivo, D.estado FROM Dispositivos D INNER JOIN Locais AS L ON D.id_local = L.id  '
        sql = sql + montarJoinCondicionalUsuario(self.usuario) + ' WHERE D.tipoDispositivo = 1'
        cur = conn.cursor()
        sqlCond, paramCond = requestParaCondicional(request)
        sql = sql + " AND " + sqlCond
        cur.execute(sql, (paramCond))
        listaLedStatus = SensorService_pb2.ListaLedStatus()
        for id, nomeLocal, nomeDispositivo, estado in cur:
            ledStatus = SensorService_pb2.LedStatus(estado = estado, nomeDispositivo = nomeDispositivo, localizacao = nomeLocal)
            listaLedStatus.status.append(ledStatus)
        conn.close()
        return listaLedStatus      

    def ListarDispositivos(self, request, context):
        if not self.is_authenticated(context):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid username or password')
            return SensorService_pb2.ListaDispositivos()

        conn = getConnection()
        sql = 'SELECT D.id, L.nomeLocal, D.nomeDispositivo, D.tipoDispositivo FROM Dispositivos D INNER JOIN Locais AS L ON D.id_local = L.id  '
        sql = sql + montarJoinCondicionalUsuario(self.usuario)
        cur = conn.cursor()
        cur.execute(sql, )
        listaDispositivos = SensorService_pb2.ListaDispositivos()
        for id, nomeLocal, nomeDispositivo, tipoDispositivo in cur:
            dispositivo = SensorService_pb2.Dispositivo(tipoDispositivo=tipoDispositivo, nomeDispositivo = nomeDispositivo, localizacao = nomeLocal)
            listaDispositivos.dispositivos.append(dispositivo)
        conn.close()
        return listaDispositivos
    
    def ConsultarFuncionalidade(self, request, context):
        tokenConsultado, funcionalidadeConsultada, usuario = consultarSessaoPeloToken(request.token)
        if tokenConsultado is None:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid username or password')
            return SensorService_pb2.Sessao()
        sessao = SensorService_pb2.Sessao(token = tokenConsultado, funcionalidade = funcionalidadeConsultada)

        return sessao;

    def AutenticarUsuario(self, request, context):
        usuario = request.usuario
        senha = request.senha

        # Verifica se o usuário e a senha são válidos
        id, usuarioBanco, senhaBanco = consultarSenhaUsuarioPorNome(usuario)
        if usuarioBanco is not None:
            hash = hashlib.sha256(senha.encode()).hexdigest()
            if hash == senhaBanco:
                self.usuario = usuarioBanco
                token, funcionalidade, nome = gerarSessao(id)
                if token is not None:
                    sessao = SensorService_pb2.Sessao(token = token, funcionalidade = funcionalidade)
                    return sessao

        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details('Invalid username or password')
        return SensorService_pb2.ListaDispositivos()

    def is_authenticated(self, context):
         # Recupera o cabeçalho de autenticação
        auth_header = context.invocation_metadata()
        for key, value in auth_header:
            if key.lower() == 'token':
                token = value
            if key.lower() == 'funcionalidade':
                funcionalidade = value
        
        tokenConsultado, funcionalidadeConsultada, usuario = consultarSessaoPeloToken(token)
        if tokenConsultado is not None:
            self.usuario = usuario
            if not funcionalidadeConsultada == funcionalidade:
               atualizarFuncionalidadeSessao(token, funcionalidade)
            return True
            
        return False

def montarJoinCondicionalUsuario(nomeUsuario: str):
    return ' INNER JOIN Usuarios U ON U.usuario = \'' + nomeUsuario + '\' INNER JOIN DispositivosUsuario DU on DU.id_usuario = U.id AND D.id = DU.id_dispositivo '

def consultarSenhaUsuarioPorNome(nomeUsuario: str):
    sql = 'SELECT id, usuario, senha FROM Usuarios WHERE usuario = ? '
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql, (nomeUsuario,))
    for id, usuario, senha in cursor:
        return id, usuario, senha
    return None, None, None

def montarMensagemAcionarLed(nomeDispositivo: str, localizacao: str):
    comando = {'nomeDispositivo': nomeDispositivo, 'localizacao': localizacao}
    msg = json.dumps(comando)
    return msg


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

def requestParaCondicional(request):
    paramCond = []
    sqlCond = " L.nomeLocal = ? "
    paramCond.append(request.localizacao)
    try:
        if request.HasField('data'):
            dataConvertida = datetime.strptime(request.data, '%d/%m/%Y')
            sqlCond = sqlCond + (" AND " if sqlCond else "") + " date(DS.data) = ? "
            paramCond.append(dataConvertida)
    except Exception as e:
        1==1
    
    if request.HasField('nomeDispositivo'):
        sqlCond = sqlCond + (" AND " if sqlCond else "") + " D.nomeDispositivo = ? "
        paramCond.append(request.nomeDispositivo)
    return sqlCond, paramCond
 
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    SensorService_pb2_grpc.add_SensorServiceServicer_to_server(SensorServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


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


def gerarSessao(idUsuario):
    sql = 'SELECT token, data_expiracao, funcionalidade, U.usuario FROM Sessao S INNER JOIN Usuarios U ON S.id_usuario = U.id WHERE id_usuario = ?'
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql, (idUsuario,))
    for token, dataExpiracao, funcionalidade, usuario in cursor:
        if token is not None:
            if isTokenValido(dataExpiracao):
                return token, funcionalidade, usuario
            else:
                deletarSessaoExpirada(token)
    conn.close()
    return criarNovaSessao(idUsuario)

def isTokenValido(dataExpiracao):
    #dataExpiracaoConvertida = datetime.strptime(dataExpiracao, '%d/%m/%Y %H:%M:%S')
    dataAtual = datetime.now()
    if dataAtual > dataExpiracao:
        return False
    return True

def deletarSessaoExpirada(token):
    sql = 'DELETE FROM Sessao WHERE token = ?'
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql, (token,))
    conn.commit()
    conn.close()

def criarNovaSessao(idUsuario):
    token = uuid.uuid1()
    dataAtual= datetime.now()
    dataExpiracao = dataAtual + timedelta(days=2)
    funcionalidade = 'ListarDispositivos'
    sqlInsereNovaSessao = 'INSERT IGNORE INTO Sessao (token, id_usuario, funcionalidade, data_expiracao) VALUES (?, ?, ?, ?)'
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sqlInsereNovaSessao, (str(token), idUsuario, funcionalidade, dataExpiracao,))
    conn.commit()
    conn.close()
    return consultarSessaoPeloToken(token)

def consultarSessaoPeloToken(token):
    sql = 'SELECT token, data_expiracao, funcionalidade, U.usuario FROM Sessao S INNER JOIN Usuarios U ON S.id_usuario = U.id WHERE token = ?'
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql, (token,))
    for tokenConsultado, dataExpiracao, funcionalidade, usuario in cursor:
        if token is not None:
            if isTokenValido(dataExpiracao):
                return tokenConsultado, funcionalidade, usuario
    conn.close()
    return None, None, None

def atualizarFuncionalidadeSessao(token: str, funcionalidade: str):
    sql = 'UPDATE Sessao SET funcionalidade = ? WHERE token = ?'
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql, (funcionalidade, token))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    serve()
