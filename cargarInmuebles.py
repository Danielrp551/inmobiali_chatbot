import pymysql
import pandas as pd
import numpy as np
import re

# Función para extraer solo números de un valor
def extraer_numero(valor):
    if pd.isna(valor) or valor in [None, "", "nan"]:
        return None
    match = re.search(r'\d+', str(valor))
    return int(match.group()) if match else None

# Función para convertir valores a `float`
def convertir_a_float(valor):
    if pd.isna(valor) or valor in [None, "", "nan"]:
        return None
    try:
        return float(valor)
    except ValueError:
        return None

# Función para convertir valores a `int`
def convertir_a_int(valor):
    if pd.isna(valor) or valor in [None, "", "nan"]:
        return None
    try:
        return int(float(valor))
    except ValueError:
        return None

# Cargar el archivo CSV
file_path = 'unificado_con_tipo_seo.csv'
df = pd.read_csv(file_path)

# Limpieza de columnas específicas
df["metros cuadrados"] = df["metros cuadrados"].apply(extraer_numero)
df["dormitorios"] = df["dormitorios"].apply(extraer_numero)
df["banios"] = df["banios"].apply(extraer_numero)
df["estacionamientos"] = df["estacionamientos"].apply(extraer_numero)

# Convertir valores flotantes o booleanos
df["SEO:Index"] = df["SEO:Index"].apply(lambda x: 1 if str(x).lower() in ["yes", "true", "1"] else 0)

# Reemplazar cualquier valor `NaN` restante por `None`
df = df.where(pd.notnull(df), None)

# Conexión a la base de datos MySQL
connection = pymysql.connect(
    host='localhost',
    user='danielrp551',
    password='26deJULIO@',
    database='chatbot_inmobiali',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Query de inserción
insert_query = """
INSERT INTO INMUEBLES (
    precio_soles, precio_dolares, direccion, ciudad, 
    metros_cuadrados, dormitorios, banios, estacionamientos, 
    detalles, precio_texto, descripcion, imagen, 
    link_propiedad, filtro_precio, filtro_m2, filtro_banios, 
    filtro_dorm, descripcion_optimizada, tipo, seo_index, 
    seo_slug, seo_title, seo_description, filtro_dolares, id_asesor
) VALUES (
    %s, %s, %s, %s, 
    %s, %s, %s, %s, 
    %s, %s, %s, %s, 
    %s, %s, %s, %s, 
    %s, %s, %s, %s, 
    %s, %s, %s, %s, NULL
)
"""

# Inserción de datos
try:
    with connection.cursor() as cursor:
        for _, row in df.iterrows():
            # Crear tupla de datos
            data = (
                convertir_a_float(row.get("precio soles")),
                convertir_a_float(row.get("precio dolares")),
                row.get("direccion"),
                row.get("ciudad"),
                convertir_a_float(row.get("metros cuadrados")),
                convertir_a_int(row.get("dormitorios")),
                convertir_a_int(row.get("banios")),
                convertir_a_int(row.get("estacionamientos")),
                row.get("detalles"),
                row.get("precio texto"),
                row.get("descripcion"),
                row.get("imagen"),
                row.get("link_propiedad"),
                row.get("filtro_precio"),
                row.get("filtro_m2"),
                row.get("filtro_banios"),
                row.get("filtro_dorm"),
                row.get("descripcion_optimizada"),
                row.get("Tipo"),
                convertir_a_int(row.get("SEO:Index")),
                row.get("SEO:Slug"),
                row.get("SEO:Title"),
                row.get("SEO:Description"),
                row.get("filtro_dolares")
            )

            # Validar la tupla antes de insertar
            if len(data) != insert_query.count('%s'):
                print(f"Error: Número de argumentos no coincide para la fila: {data}")
                continue

            # Insertar datos en la base
            print(f"Insertando datos: {data}")  # Registro de la tupla
            cursor.execute(insert_query, data)

    connection.commit()
    print("Datos insertados correctamente.")
except Exception as e:
    print(f"Error al insertar datos: {e}")
finally:
    connection.close()
