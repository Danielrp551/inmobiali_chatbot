import re
import datetime
import json

def formatear_todos_los_campos(inmueble):
    # Convertir valores a cadenas legibles o predeterminadas
    def valor_o_no_disponible(valor):
        return str(valor) if valor is not None else "No disponible"

    info_formateada = (
        f"🏠 **Información Completa del Inmueble**\n"
        f"- **ID del Inmueble**: {valor_o_no_disponible(inmueble.get('id_inmueble'))}\n"
        f"- **Precio en Soles**: S/ {valor_o_no_disponible(inmueble.get('precio_soles'))}\n"
        f"- **Precio en Dólares**: USD {valor_o_no_disponible(inmueble.get('precio_dolares'))}\n"
        f"- **Dirección**: {valor_o_no_disponible(inmueble.get('direccion'))}\n"
        f"- **Ciudad**: {valor_o_no_disponible(inmueble.get('ciudad'))}\n"
        f"- **Metros Cuadrados**: {valor_o_no_disponible(inmueble.get('metros_cuadrados'))} m²\n"
        f"- **Dormitorios**: {valor_o_no_disponible(inmueble.get('dormitorios'))}\n"
        f"- **Baños**: {valor_o_no_disponible(inmueble.get('banios'))}\n"
        f"- **Estacionamientos**: {valor_o_no_disponible(inmueble.get('estacionamientos'))}\n"
        f"- **Detalles**: {valor_o_no_disponible(inmueble.get('detalles'))}\n"
        f"- **Texto de Precio**: {valor_o_no_disponible(inmueble.get('precio_texto'))}\n"
        f"- **Descripción**: {valor_o_no_disponible(inmueble.get('descripcion'))}\n"
        f"- **Imagen**: {valor_o_no_disponible(inmueble.get('imagen'))}\n"
        f"- **Link a la Propiedad**: {valor_o_no_disponible(inmueble.get('link_propiedad'))}\n"
        f"- **Filtro de Precio**: {valor_o_no_disponible(inmueble.get('filtro_precio'))}\n"
        f"- **Filtro por Metros Cuadrados**: {valor_o_no_disponible(inmueble.get('filtro_m2'))}\n"
        f"- **Filtro por Baños**: {valor_o_no_disponible(inmueble.get('filtro_banios'))}\n"
        f"- **Filtro por Dormitorios**: {valor_o_no_disponible(inmueble.get('filtro_dorm'))}\n"
        f"- **Descripción Optimizada**: {valor_o_no_disponible(inmueble.get('descripcion_optimizada'))}\n"
        f"- **Tipo**: {valor_o_no_disponible(inmueble.get('tipo'))}\n"
        f"- **Índice SEO**: {valor_o_no_disponible(inmueble.get('seo_index'))}\n"
        f"- **Slug SEO**: {valor_o_no_disponible(inmueble.get('seo_slug'))}\n"
        f"- **Título SEO**: {valor_o_no_disponible(inmueble.get('seo_title'))}\n"
        f"- **Descripción SEO**: {valor_o_no_disponible(inmueble.get('seo_description'))}\n"
        f"- **Filtro en Dólares**: {valor_o_no_disponible(inmueble.get('filtro_dolares'))}\n"
        f"- **ID del Asesor**: {valor_o_no_disponible(inmueble.get('id_asesor'))}\n"
    )
    return info_formateada

def json_a_lista(datos):
    # Asumimos que `datos` ya es un diccionario JSON
    resultado = [datos.get("intencion")]

    # Agregar "categoria" si está presente
    if "categoria" in datos:
        resultado.append(datos["categoria"])

    # Agregar "detalle" si está presente
    if "detalle" in datos:
        resultado.append(datos["detalle"])

    return resultado

def extraer_json(texto):
    # Expresión regular para capturar cualquier JSON completo en el formato { ... }, permitiendo saltos de línea
    patron = r'\{(?:.|\s)*?\}'

    # Buscar el JSON en el texto
    match = re.search(patron, texto)
    if match:
        # Convertir la cadena JSON capturada en un diccionario
        try:
            resultado = json.loads(match.group())
            return resultado
        except json.JSONDecodeError as e:
            print("Error de decodificación JSON:", e)
            return None
    else:
        print("Error: No se encontró un JSON válido en el texto.")
        return None

def format_number(numero_celular):
    # Verificar si el número ya comienza con "+51"
    if numero_celular.startswith("+51"):
        return numero_celular
    # Si el número comienza con "51" pero sin el "+", agregar el "+"
    elif numero_celular.startswith("51"):
        return f"+{numero_celular}"
    # Si el número no comienza con "51" ni "+51", agregar "+51" al inicio
    else:
        return f"+51{numero_celular}"


def formatear_horarios_disponibles(horarios):
    return " | ".join(horarios)

def formatear_historial_conversaciones(conversaciones):
    """Convierte un historial de conversaciones en un formato de string concatenado."""
    historial_completo = []
    
    for conversacion in conversaciones:
        # Llamar a formatear_conversacion para cada conversación en el historial
        historial_formateado = formatear_conversacion(conversacion)
        historial_completo.append(historial_formateado)
    
    return "\n\n".join(historial_completo)


def formatear_conversacion(conversacion):
    """Convierte una conversación en un formato de string con saltos de línea entre interacciones."""
    historial_formateado = []
    
    for interaccion in conversacion.get("interacciones", []):
        mensaje_cliente = interaccion.get("mensaje_cliente", "")
        mensaje_chatbot = interaccion.get("mensaje_chatbot", "")

        if mensaje_cliente:
            historial_formateado.append(f'Cliente: "{mensaje_cliente}"')
        if mensaje_chatbot:
            historial_formateado.append(f'Asesor: "{mensaje_chatbot}"')
    
    # Unir el historial en un solo string con saltos de línea
    return "\n".join(historial_formateado)


def extract_datetime(message):
    print("Mensaje recibido:", repr(message))
    # Expresiones regulares para distintos formatos de fecha y hora
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # AAAA-MM-DD
        r'(\d{2}/\d{2}/\d{4})',  # DD/MM/AAAA
        r'(\d{1,2} de [a-zA-Z]+)',  # D de Mes
    ]
    
    time_patterns = [
        r'(\d{1,2}:\d{2} ?[apAP]\.?[mM]\.?)',  # HH:MM AM/PM con o sin puntos
        r'(\d{1,2}:\d{2})',  # HH:MM (24 horas)
    ]
    
    # Buscar fecha en el mensaje
    user_date = None
    for pattern in date_patterns:
        match = re.search(pattern, message)
        if match:
            date_str = match.group(0)
            try:
                if '-' in date_str:
                    user_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                elif '/' in date_str:
                    user_date = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
                else:
                    day, month = date_str.split(' de ')
                    month_dict = {
                        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
                    }
                    user_date = datetime.date(datetime.datetime.now().year, month_dict[month.lower()], int(day))
            except ValueError:
                continue

            print("User date",user_date)

    # Buscar hora en el mensaje
    user_time = None
    for pattern in time_patterns:
        match = re.search(pattern, message)
        if match:
            time_str = match.group(0)
            print("Hora encontrada:", time_str)
            try:
                # Si incluye AM/PM en cualquier formato
                if re.search(r'[apAP][\.]?[mM][\.]?', time_str):
                    # Normalizamos el formato quitando espacios y puntos
                    time_str = re.sub(r'[\s\.]+', '', time_str).lower()
                    print("Hora normalizada y len :", time_str, time_str.__len__())
                    #user_time = datetime.datetime.strptime(time_str, '%I:%M%p').time()
                    # Procesar manualmente la hora AM/PM
                    hour, minute = map(int, time_str[:-2].split(':'))
                    am_pm = time_str[-2:]
                    if am_pm == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                        
                    user_time = datetime.time(hour, minute)                    
                    print("User time AMPM : ",user_time)
                    break # priorizar el formato 12h
                else:
                    if not user_time:
                        user_time = datetime.datetime.strptime(time_str, '%H:%M').time()
                        print("User time 24h:", user_time)
            except ValueError as e:
                print("Error al convertir la hora : ",e)
                continue
    
    if user_date and user_time:
        # Combinar la fecha y la hora en un solo objeto de fecha y hora
        print("Fecha y hora combinadas:", user_date, user_time)
        combined_datetime = datetime.datetime.combine(user_date, user_time)
        return combined_datetime.strftime('%Y-%m-%d'), combined_datetime.strftime('%H:%M')
    elif user_date:
        return user_date.strftime('%Y-%m-%d'), None
    elif user_time:
        return None, user_time.strftime('%H:%M')
    else:
        return None, None


def formatear_fecha_hora(fecha_str, hora_str):
    # Convertir la cadena de fecha a un objeto datetime
    fecha_dt = datetime.datetime.strptime(fecha_str, '%Y-%m-%d')
    
    # Convertir la cadena de hora a un objeto datetime para formatear
    hora_dt = datetime.datetime.strptime(hora_str, '%H:%M')

    # Formatear la fecha a un formato más legible
    fecha_formateada = fecha_dt.strftime('%A %d de %B').capitalize()

    # Convertir la hora a AM/PM manualmente
    def convertir_a_am_pm(hora):
        if hora.hour < 12:
            return f"{hora.hour}:{hora.strftime('%M')} a.m."
        elif hora.hour == 12:
            return f"12:{hora.strftime('%M')} p.m."
        else:
            return f"{hora.hour - 12}:{hora.strftime('%M')} p.m."

    hora_formateada = convertir_a_am_pm(hora_dt)

    return fecha_formateada, hora_formateada
