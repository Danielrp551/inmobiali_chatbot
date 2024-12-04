import mysql.connector
from mysql.connector import Error
from datetime import datetime

class DataBaseMySQLManager:
    def __init__(self):
        self.connection = self._connect()

    def _reconnect_if_needed(self):
        """Reconnects if the current connection is not active."""
        if not self.connection.is_connected():
            print("Reconectando a MySQL...")
            self.connection = self._connect()    

    def _connect(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='danielrp551',
                database='chatbot_inmobiali',
                password='26deJULIO@'
                #host='chatbot-mysql.c5yiocg6aj0e.us-east-2.rds.amazonaws.com',
                #database='chatbot_maqui',
                #user='admin',
                #password='zQumSnUd9MNtjcsK'
            )
            if connection.is_connected():
                print("Conectado a MySQL")
            return connection
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return None

    def obtener_clientes(self):
        self._reconnect_if_needed()
        """Obtiene todos los clientes de la base de datos."""
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM clientes"
        cursor.execute(query)
        return cursor.fetchone()

    def marcar_enviado_cliente(self, cliente_id):
        self._reconnect_if_needed()
        cursor = self.connection.cursor(dictionary=True)
        query = "UPDATE clientes SET mensaje_enviado = true WHERE cliente_id = %s"
        cursor.execute(query, (cliente_id))
        self.connection.commit()
        return cursor.fetchone()    

    def obtener_id_cliente_por_celular(self, celular):
        self._reconnect_if_needed()
        """Obtiene el cliente_id usando el número de celular."""
        cursor = self.connection.cursor()
        query = "SELECT id_cliente FROM clientes WHERE celular = %s"
        cursor.execute(query, (celular,))
        result = cursor.fetchone()
        return result[0] if result else None

    def existe_cliente_por_celular(self, celular):
        self._reconnect_if_needed()
        """Verifica si un cliente ya existe en la base de datos usando el número de celular."""
        return self.obtener_id_cliente_por_celular(celular) is not None

    def insertar_cliente(self, documento_identidad, tipo_documento, nombre, apellido, celular, email,estado="activo"):
        self._reconnect_if_needed()
        """Inserta un nuevo cliente en la tabla de clientes si no existe ya."""
        if not self.existe_cliente_por_celular(celular):
            cursor = self.connection.cursor()
            query = """INSERT INTO clientes (documento_identidad, tipo_documento, nombre, apellido, celular, email,estado)
                       VALUES (%s, %s, %s, %s, %s, %s,%s)"""
            cursor.execute(query, (documento_identidad, tipo_documento, nombre, apellido, celular, email,estado))
            self.connection.commit()
            print("Cliente insertado en MySQL.")
            return cursor.lastrowid
        else:
            print("El cliente ya existe en MySQL.")
            return self.obtener_id_cliente_por_celular(celular)
        
    def insertar_obtener_cliente_por_celular(self, nombre, celular):
        self._reconnect_if_needed()
        if not self.existe_cliente_por_celular(celular):
            cursor = self.connection.cursor()
            query = """INSERT INTO clientes (nombre,celular)
                       VALUES (%s, %s)"""
            cursor.execute(query, (nombre, celular))
            self.connection.commit()
            return {
                "id_cliente": cursor.lastrowid,
                "nombre": nombre,
                "celular": celular,
                "fecha_registro": datetime.now()
            }

        else:
            cursor = self.connection.cursor(dictionary=True)
            query = """SELECT * FROM clientes WHERE celular = %s"""
            cursor.execute(query, (celular,))
            return cursor.fetchone()


    def obtener_cliente(self, cliente_id):
        self._reconnect_if_needed()
        """Obtiene los datos de un cliente por su ID."""
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM clientes WHERE cliente_id = %s"
        cursor.execute(query, (cliente_id,))
        return cursor.fetchone()
           
    def obtener_todos_los_clientes(self):
        self._reconnect_if_needed()
        """Obtiene los datos de un cliente por su ID."""
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM clientes"
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_inmueble_por_id(self, inmueble_id):
        self._reconnect_if_needed()
        """Obtiene los datos de un inmueble por su ID."""
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM inmuebles WHERE id_inmueble = %s"
        cursor.execute(query, (inmueble_id,))
        return cursor.fetchone()
    
    def obtener_asesor_disponible(self, inmueble_id):
        if(inmueble_id is None or inmueble_id == ""):
            return None
        self._reconnect_if_needed()
        """Obtiene los datos de un asesor disponible para un inmueble."""
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM asesores WHERE id_asesor = (SELECT id_asesor FROM inmuebles WHERE id_inmueble = %s)"
        cursor.execute(query, (inmueble_id,))
        return cursor.fetchone()
    
    def crearConsulta(self, cliente_id, inmueble_id):
        self._reconnect_if_needed()
        if( self.consulta_existe(cliente_id, inmueble_id) ):
            return None
        
        """Crea una nueva consulta en la base de datos."""
        cursor = self.connection.cursor()
        query = """INSERT INTO consultas (id_cliente, id_inmueble)
                   VALUES (%s, %s)"""
        cursor.execute(query, (cliente_id, inmueble_id))
        self.connection.commit()
        return cursor.lastrowid
    
    def consulta_existe(self, cliente_id, inmueble_id):
        self._reconnect_if_needed()
        """Verifica si ya existe una consulta en la base de datos."""
        cursor = self.connection.cursor()
        query = "SELECT * FROM consultas WHERE id_cliente = %s AND id_inmueble = %s"
        cursor.execute(query, (cliente_id, inmueble_id))
        return cursor.fetchone() is not None

    

