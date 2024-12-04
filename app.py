import json
import threading
import time
import os
import hmac
import re
import hashlib
from datetime import datetime, timedelta
from api_keys.api_keys import recordatorio_ruleta
from flask import Flask, request, jsonify
from components.twilio_component import TwilioManager
from components.openai_component import OpenAIManager
from components.database_mongodb_component import DataBaseMongoDBManager
from components.database_mysql_component import DataBaseMySQLManager
from components.email_component import EmailManager
from helpers.helpers import extraer_json

app = Flask(__name__)

# Inicializar Componentes
twilio = TwilioManager()
openai = OpenAIManager()
dbMongoManager = DataBaseMongoDBManager()
dbMySQLManager = DataBaseMySQLManager()
email_manager = EmailManager("smtp.gmail.com",587,"eselrey551@gmail.com","jhjx qnbi oaaq sree")

# Diccionario para almacenar temporizadores activos por cliente
timers = {}

# Función para enviar la respuesta al cliente después del retardo
def enviar_respuesta(cliente, cliente_nuevo):
    print("Enviando respuesta a:", cliente["celular"])

    # Obtener la conversación actual del cliente
    conversation_actual = dbMongoManager.obtener_conversacion_actual(cliente["celular"])

    # Obtener el historial de conversaciones del cliente en caso tenga
    conversation_history = dbMongoManager.obtener_historial_conversaciones(cliente["celular"])
    
    # obtener o crear cliente y retornar cliente
    cliente_mysql = dbMySQLManager.insertar_obtener_cliente_por_celular(
        nombre= "",
        celular = cliente["celular"],
    )

    # actualizo fecha de ultima interaccion
    #dbMySQLManager.actualizar_fecha_ultima_interaccion(cliente_mysql["id_cliente"], datetime.now())

    #verifica si tiene una conversacion activa y sino la crea -> mysql
    #conversacion_mysql = dbMySQLManager.obtener_conversacion_activa(cliente_mysql["id_cliente"])
    #if not conversacion_mysql:
        # Crear conversación activa en MySQL si no existe
    #    conversacion_id_mysql = dbMySQLManager.insertar_conversacion(
    #        cliente_id=cliente_mysql["id_cliente"],
    #        mensaje="Inicio de conversación",
    #        tipo_conversacion="activa",
    #        resultado=None,
    #        estado_conversacion="activa"
    #    )
    #else:
    #    conversacion_id_mysql = conversacion_mysql["conversacion_id"]    

    # obtiene la conversacion actual del cliente -> mongo
    conversation_actual = dbMongoManager.obtener_conversacion_actual(cliente["celular"])

    # obtiene historial de conversaciones del cliente -> mongo
    conversation_history = dbMongoManager.obtener_historial_conversaciones(cliente["celular"])

    # mapeo de intenciones
    intencion = openai.mapear_intenciones(conversation_actual, conversation_history)
    print("Intencion antes extraer json:", intencion)
    intencion = extraer_json(intencion)
    print("Intencion mapeada json:", intencion)

    if intencion["intencion"]=="informacion_inmueble":
        print("Ingreso a la intencion 1: ")
        # obtener inmueble por id
        inmueble =  dbMySQLManager.obtener_inmueble_por_id(intencion["inmueble_id"])

        print("Inmueble encontrado:", inmueble)
        response_message = openai.consulta_informacion_inmueble(inmueble, conversation_actual)
        # responder con la informacion del inmueble
        #response_message = "El inmueble solicitado es el siguiente: ... "
    if intencion["intencion"]=="contactar_asesor":
        print("Ingreso a la intencion 2: ")
        # obtener asesor
        print("Inmueble id:", intencion["inmueble_id"])
        asesor = dbMySQLManager.obtener_asesor_disponible(intencion["inmueble_id"])
        print("Asesor encontrado:", asesor)        
        if asesor is not None and intencion["inmueble_id"] is not None and intencion["inmueble_id"] != "":
        # responder con la informacion del asesor
            response_message = f"""{{"mensaje": "¡Hola! Ya hemos informado a {asesor["nombre"]}, el asesor encargado del inmueble, para que se contacte contigo lo más pronto posible. Si necesitas algo adicional mientras tanto, no dudes en escribirme. 😊"}}"""

            # info inmueble
            inmueble =  dbMySQLManager.obtener_inmueble_por_id(intencion["inmueble_id"])
            print("Inmueble encontrado:", inmueble)
            # enviar correo al asesor
            inmueble_info = {
                "id_inmueble": intencion["inmueble_id"],
                "direccion": inmueble["direccion"],
                "ciudad": inmueble["ciudad"],
                "precio": inmueble["precio_texto"]
            }
            cliente_info = {
                "nombre":  intencion["nombre"],
                "email": "carlos.perez@example.com",
                "telefono": "+51 987654321"
            }        
            consulta_id = dbMySQLManager.crearConsulta(cliente_mysql["id_cliente"],intencion["inmueble_id"])
            if consulta_id:
                print("Consulta creada en MySQL:", consulta_id)
                email_manager.enviar_correo_asesor(asesor["nombre"],asesor["correo"],inmueble_info,cliente_info)
            else:
                print("Consulta ya existente en MySQL.")
                response_message = f"""{{"mensaje": "El asesor ya ha sido informado de tu interés en el inmueble. ¿Hay algo más en lo que pueda ayudarte? 😊"}}"""

        else:
            response_message = f"""{{"mensaje": "Lamentablemente el inmueble no tiene un asesor asociado. ¿Hay algo más en lo que pueda ayudarte? 😊"}}"""
    
        # mensaje al cliente
        #response_message = f"""{{"mensaje": "¡Hola! Ya hemos informado a {asesor["nombre"]}, el asesor encargado del inmueble, para que se contacte contigo lo más pronto posible. Si necesitas algo adicional mientras tanto, no dudes en escribirme. 😊
        #                    "}}"""
    if intencion["intencion"]=="consulta_general":
        print("Ingreso a la intencion 3: ")
        # responder con la informacion general
        #response_message = f"""{{"mensaje": "Gracias por tu consulta, ahora te la respondo."}}"""
        response_message = openai.consulta_general(conversation_actual)

    print("Response message:", response_message)
    response_message = extraer_json(response_message)
    print("Response message json:", response_message)
    response_message = response_message["mensaje"]
    response_message = response_message.replace("Asesor: ", "").strip('"')
    twilio.send_message(cliente["celular"], response_message)

    # Guardar la respuesta en la conversación actual
    dbMongoManager.guardar_respuesta_ultima_interaccion_chatbot(cliente["celular"], response_message)
    # Eliminar el temporizador del cliente una vez que se haya respondido
    timers.pop(cliente["celular"], None)

@app.route('/bot', methods=['POST'])
def whatsapp_bot():
    try:
        incoming_msg = request.form.get('Body').lower()
        sender = request.form.get('From')
        celular = sender.split('whatsapp:')[1]
        print("Mensaje recibido:", incoming_msg)
        print("Remitente:", celular)
        
        # Obtener cliente de la base de datos
        cliente = dbMongoManager.obtener_cliente_por_celular(celular)
        cliente_nuevo = False
        if not cliente:
            cliente_nuevo = True
            cliente = dbMongoManager.crear_cliente(nombre="",celular=celular)
            print("Cliente creado:", cliente)
        print("Cliente encontrado en la base de datos:", cliente["nombre"])

        if not dbMongoManager.hay_conversacion_activa(celular):
            # Se crea una conversacion activa, solo se crea
            print("Creando una nueva conversación activa para el cliente.")
            dbMongoManager.crear_conversacion_activa(celular)
        # Verificar si ya hay un temporizador en curso para este cliente
        if celular in timers:
            # Si ya existe un temporizador, lo cancelamos
            timers[celular].cancel()
            print("Temporizador existente cancelado para el cliente:", cliente["nombre"])
                        # Agrega la interacción del cliente a la conversación actual
            dbMongoManager.guardar_mensaje_cliente_ultima_interaccion(celular, incoming_msg)
            print("Interacción del cliente guardada en la conversación actual.")
        else:
            # Si no existe un temporizador, crear una nueva interacción
            print("Creando una nueva interacción para el cliente.")
            dbMongoManager.crear_nueva_interaccion(celular, incoming_msg)            

        # Crear un nuevo temporizador de 60 segundos antes de responder
        timer = threading.Timer(2, enviar_respuesta, args=[cliente,cliente_nuevo])
        timers[celular] = timer
        timer.start()
        print("Nuevo temporizador iniciado para el cliente:", sender)

        return 'OK', 200

    except Exception as e:
        print("Error en whatsapp_bot:", e)
        return "Error interno del servidor", 500

@app.route('/enviar-mensaje-clientes', methods=['POST'])
def enviar_mensaje_clientes():
    if os.path.exists("enviar_mensaje_clientes.lock"):
        print("Ya se está enviando un mensaje a los clientes")
        return "Ya se está enviando un mensaje a los clientes", 400
    with open("enviar_mensaje_clientes.lock", "w") as f:
        f.write("lock")

    try:
        while True:
            print("Iniciando conversacion con clientes ...")

            # obtenemos los clientes
            clientes = []

            for cliente in clientes:
                twilio.send_template_message(cliente["celular"], recordatorio_ruleta,{"1":cliente["nombre"]})    
                #marco como enviado
    except Exception as e:
        print("Error en enviar_mensaje_clientes:", e)
    finally:
        os.remove("/tmp/enviar_mensaje_clientes.lock")

            

def start_background_threads():
    # Iniciar el hilo en segundo plano para iniciar conversaciones automáticamente
    # threading.Thread(target=iniciar_conversacion_leads).start()
    # Iniciar el hilo en segundo plano para verificar conversaciones inactivas
    #threading.Thread(target=).start()
    print("Hilo de verificación de conversaciones")
    # Iniciar el hilo en segundo plano para limpiar citas no confirmadas
    # threading.Thread(target=limpiar_citas_no_confirmadas).start()
    # Iniciar otro hilo, si es necesario
    # threading.Thread(target=verificar_estados_clientes).start()

#start_background_threads()

if __name__ == '__main__':
    # Iniciar la aplicación Flask
    app.run(host='0.0.0.0',port=5000)
