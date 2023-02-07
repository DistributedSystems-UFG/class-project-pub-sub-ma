import grpc
from concurrent import futures
import SensorService_pb2
import SensorService_pb2_grpc

channel = grpc.insecure_channel('146.148.42.190'+':'+'50051')
tiposDispositivos = {1 : 'LED', 2: 'Sensor de Temperatura', 3: 'Sensor Umidade', 4: 'Sensor Luminosidade'}
metadata = None


def definirMetadados(usuario: str, senha: str):
    global metadata
    metadata = [('username', usuario), ('password', senha)]

def listarDispositivos():
    stub = SensorService_pb2_grpc.SensorServiceStub(channel)
    em = SensorService_pb2.EmptyMessage()
    response = stub.ListarDispositivos(em, metadata=metadata)
    return response.dispositivos


def listarLeds(local: str, nomeDispositivo: str):
    stub = SensorService_pb2_grpc.SensorServiceStub(channel)
    
    ledStatus = SensorService_pb2.LedStatus(nomeDispositivo = nomeDispositivo, localizacao = local)
    response = stub.ListarLeds(ledStatus,  metadata=metadata)
    return response.status

def acionarLed(local: str, nomeDispositivo: str, estado : int):
    stub = SensorService_pb2_grpc.SensorServiceStub(channel)
    
    ledStatus = SensorService_pb2.LedStatus(estado = estado, nomeDispositivo = nomeDispositivo, localizacao = local)
    response = stub.AcionarLed(ledStatus,  metadata=metadata)
    return response

def listarLeituraPorParametros(localizacao: str, data: str, nomeDispositivo: str):
    stub = SensorService_pb2_grpc.SensorServiceStub(channel)
    
    param = SensorService_pb2.Parametros(localizacao = localizacao, data = data, nomeDispositivo = nomeDispositivo)        
    response = stub.ListarLeiturasSensores(param,  metadata=metadata)
    print('Dados: ' + str(response.dados))
    
def consultarUltimaLeitura(localizacao: str, nomeDispositivo: str, data: str = None):
    stub = SensorService_pb2_grpc.SensorServiceStub(channel)
    
    param = SensorService_pb2.Parametros(localizacao = localizacao, data = data, nomeDispositivo = nomeDispositivo)        
    response = stub.ConsultarUltimaLeituraSensor(param,  metadata=metadata)
    return response

def converterListaDispositivosParaDict(dispositivos: list):
    dispositivosPorLocal = {}
    i = 1
    for d in dispositivos:
        if d.localizacao not in dispositivosPorLocal:
            dispositivosPorLocal[d.localizacao] = []
        dispositivosPorLocal[d.localizacao].append(d)
        i += 1
    return dispositivosPorLocal

def getDispositivoPorNomeELocal(local: str, nomeDispositivo: str, dispositivosPorLocal: dict):
    for localizacao, dispositivos in dispositivosPorLocal.items():
        if not local.upper() == localizacao.upper():
            continue
        for disp in dispositivos:
            if nomeDispositivo.upper() == disp.nomeDispositivo.upper():
                return disp
    
    return None

def menuLed(led: SensorService_pb2.Dispositivo):
    listaStatus = listarLeds(local=led.localizacao, nomeDispositivo=led.nomeDispositivo)
    status = listaStatus[0]
    print('O dispositivo ' + led.nomeDispositivo + ' se encontra ' + ('Ligado' if status.estado == 1 else 'Desligado') + '\n')
    print('Deseja ' + ('desligar' if status.estado == 1 else 'Ligar') + '? S/N ')
    acao = str(input())
    if acao.upper() == 'S':
        novoStatus = acionarLed(nomeDispositivo=led.nomeDispositivo, local=led.localizacao, estado=(0 if status.estado == 1 else 1))
        print(led.nomeDispositivo + ' agora se encontra ' + ('Ligado' if novoStatus.estado == 1 else 'Desligado'))

def menuSensor(sensor: SensorService_pb2.Dispositivo):
    dado = consultarUltimaLeitura(nomeDispositivo=sensor.nomeDispositivo, localizacao=sensor.localizacao, data=None)
    print('Leitura atual: ' + "{:.2f}".format(dado.valor) + '\n')
    print('Deseja listar historico de leituras? S/N ')
    resp = str(input())
    if resp.upper() == 'S':
        data = None
        print('Utilizao data especifica? S/N ')
        filtrar = str(input())
        if filtrar.upper() == 'S':
            data = str(input('Data (dd/mm/aaaa): '))
        listarLeituraPorParametros(data=data, localizacao=sensor.localizacao, nomeDispositivo=sensor.nomeDispositivo)
    


if __name__ == '__main__': 
    dispositivosConsuldados = None
    autenticado = False

    while not autenticado:
        usuario = str(input('Usuario: '))
        senha = str(input('Senha: '))
        try:
            definirMetadados(usuario, senha)
            dispositivosConsuldados = listarDispositivos()
            autenticado = True
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                print('Usuario ou senha incorretos. Tente novamente.\n')
            else:
                raise e

    dispositivosPorLocal = converterListaDispositivosParaDict(dispositivosConsuldados)
    
    while True:
        for local, dispositivos in dispositivosPorLocal.items():
            print('\nLocal: ' + local)
            for disp in dispositivos:
                print('\t' + tiposDispositivos[disp.tipoDispositivo])
                print('\t' + 'Nome: ' + disp.nomeDispositivo)
                if disp.tipoDispositivo > 1:
                    dado = consultarUltimaLeitura(nomeDispositivo=disp.nomeDispositivo, localizacao=disp.localizacao, data=None)
                    print('\t\t' + "{:.2f}".format(dado.valor))
                elif disp.tipoDispositivo == 1:
                    status = listarLeds(local=disp.localizacao, nomeDispositivo=disp.nomeDispositivo)
                    print('\t\t' + ('Ligado' if status[0].estado == 1 else 'Desligado'))
                print('\n')
        
        print('Informe o local e nome do dispositivo\n')
        localIn = str(input('Local: '))
        nomeDispIn = str(input('Nome dispositivo: '))
        dispSelecionado = getDispositivoPorNomeELocal(localIn, nomeDispIn, dispositivosPorLocal)
        if dispSelecionado.tipoDispositivo == 1:
            menuLed(dispSelecionado)
        elif dispSelecionado.tipoDispositivo > 1:
            menuSensor(dispSelecionado)
        print('=============================================================\n')