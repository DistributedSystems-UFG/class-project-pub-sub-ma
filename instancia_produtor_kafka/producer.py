from kafka import KafkaProducer, KafkaConsumer
import random
from datetime import datetime
import time
from const import *
import json
import sys
import threading
import board
import adafruit_dht
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


"""
Definição da mensagem ACIONAR LED (JSON):
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
leds = [
        {"corLed": "verde", "pin": 26, "estado": False}, 
        {"corLed": "vermelho", "pin": 16, "estado": False}, 
        {"corLed": "amarelo", "pin": 6, "estado": False},
        {"corLed": "vermelho", "pin": 13, "estado": False},
]

sensores = [{"sensor": "temperatura", "pin": 4}, {"sensor": "umidade", "pin": 4}, {"sensor": "luminosidade", "pin": 5}]
loc_disp = [
    {
        "localizacao": "sala",
        "dispositivos": [ 
            {
                "nomeDispositivo": "lampada",
                "tipoDispositivo": 1,
                "info": leds[0],
            },
            {
                "nomeDispositivo": "sensor de temperatura",
                "tipoDispositivo": 2,
                "info": sensores[0]
            },
        ]
    },
    {
        "localizacao": "varanda",
        "dispositivos": [ 
            {
                "nomeDispositivo": "lampada",
                "tipoDispositivo": 1,
                "info": leds[1],
            },
            {
                "nomeDispositivo": "sensor de temperatura",
                "tipoDispositivo": 2,
                "info": sensores[0]
            },
            {
                "nomeDispositivo": "sensor de umidade",
                "tipoDispositivo": 3,
                "info": sensores[1]
            },
            {
                "nomeDispositivo": "sensor de luminosidade",
                "tipoDispositivo": 4,
                "info": sensores[2]
            },
        ]
    },
    {
        "localizacao": "quarto",
        "dispositivos": [ 
            {
                "nomeDispositivo": "lampada",
                "tipoDispositivo": 1,
                "info": leds[2],
            },
            {
                "nomeDispositivo": "abajur",
                "tipoDispositivo": 1,
                "info": leds[3],
            },
            {
                "nomeDispositivo": "sensor de temperatura",
                "tipoDispositivo": 2,
                "info": sensores[0]
            },
        ]
    },
]

dhtDevice = adafruit_dht.DHT22(4)
producer = KafkaProducer(bootstrap_servers=[BROKER_ADDR + ':' + BROKER_PORT])

def decodeMessage(msg : str):
    dados = json.loads(msg)
    return dados

def iniciarGPIO():
    # Initialize GPIO
    GPIO.setwarnings(False) # Ignore warning for now
    for info in leds:
        GPIO.setup(info['pin'], GPIO.OUT, initial=(GPIO.LOW if info['estado'] == False else GPIO.HIGH))

def rodarComandoLED(ledpin: int, estado: int):
    GPIO.output(ledpin, GPIO.HIGH if estado == 1 else GPIO.LOW)

def getPinoPorNomeELocalizacao(localizacao: str, nomeDispositivo: str):
    for local in loc_disp:
        if not local['localizacao'] == localizacao:
            continue
        for disp in local['dispositivos']:
            if disp['nomeDispositivo'] == nomeDispositivo:
                return disp['info']['pin']

def consume_led_command():
    consumer = KafkaConsumer(bootstrap_servers=BROKER_ADDR+':'+BROKER_PORT)
    consumer.subscribe(topics=('ledcommand'))
    ledpin = 0
    for msg in consumer:
        estado = int(msg.value.decode())
        led = decodeMessage(msg.key.decode())
        ledpin = getPinoPorNomeELocalizacao(led['localizacao'], led['nomeDispositivo'])
        rodarComandoLED(ledpin, estado)

def lerUmidadeTemperatura(pin: int):
    try:
        temperatura_c = dhtDevice.temperature
        umidade = dhtDevice.humidity
        
        return temperatura_c, umidade
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        return None, None
    except Exception as error:
        dhtDevice.exit()
        raise error

def cadastrarDispositivos():
    msg = json.dumps(loc_disp)
    producer.send("dispositivos", value=msg.encode())

def getTodosSensoresCadastrados():
    sensores = []
    for loc in loc_disp:
        for disp in loc['dispositivos']:
            if disp['tipoDispositivo'] > 1:
                disp['localizacao'] = loc['localizacao']
                sensores.append(disp)
    return sensores

def rc_time(pin_to_circuit: int):
    count = 0
  
    #Output on the pin for 
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(0.1)

    #Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)
  
    #Count until the pin goes high
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1

    return count

def lerLuminosidade(pin_to_circuit: int):
    light_level = rc_time(pin_to_circuit)
    return light_level


def gerarDado(tipoSensor : int, localizacao : str, nomeDispositivo: str, pinoSensor: int):
    data = datetime.now()
    valor = None
    if tipoSensor == 2:
        valor = lerUmidadeTemperatura(pinoSensor)[0]
    elif tipoSensor == 3:
        valor = lerUmidadeTemperatura(pinoSensor)[1]
    elif tipoSensor == 4:
        valor = lerLuminosidade(pinoSensor)
    valor = float(valor) if valor is not None else None
    dado = {
        "data": data.strftime("%d/%m/%Y %H:%M:%S"),
        "localizacao": localizacao,
        "nomeDispositivo": nomeDispositivo,
        "valor": valor
    }
    msg = json.dumps(dado)
    return msg if dado['valor'] is not None else None

if __name__ == '__main__':
    cadastrarDispositivos()
    iniciarGPIO()
    trd =threading.Thread(target=consume_led_command)
    trd.start()

    sensoresCadastrados = getTodosSensoresCadastrados()
    while True:
        for sensor in sensoresCadastrados:
            msg = gerarDado(sensor['tipoDispositivo'], sensor['localizacao'], sensor['nomeDispositivo'], sensor['info']['pin'])
            if msg is None:
                continue
            producer.send(sensor['info']['sensor'], value=msg.encode())
        time.sleep(5)

    producer.flush() 


  
   
