import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailManager:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def enviar_correo_asesor(self, nombre_asesor, email_asesor, inmueble_info, cliente_info):
        # Construir el asunto y el cuerpo del correo
        subject = f"Nuevo cliente interesado en el inmueble {inmueble_info['id_inmueble']}"
        body = (
            f"Hola {nombre_asesor},\n\n"
            f"Un cliente ha mostrado interés en el inmueble con ID {inmueble_info['id_inmueble']}.\n\n"
            f"Detalles del cliente:\n"
            f"- Nombre: {cliente_info.get('nombre', 'No disponible')}\n"
            f"- Correo: {cliente_info.get('email', 'No disponible')}\n"
            f"- Teléfono: {cliente_info.get('telefono', 'No disponible')}\n\n"
            f"Detalles del inmueble:\n"
            f"- Dirección: {inmueble_info.get('direccion', 'No disponible')}\n"
            f"- Ciudad: {inmueble_info.get('ciudad', 'No disponible')}\n"
            f"- Precio: {inmueble_info.get('precio_texto', 'No disponible')}\n\n"
            f"Por favor, contacta al cliente lo antes posible para brindarle más información.\n\n"
            f"Saludos,\n"
            f"Equipo de Soporte"
        )

        # Crear el mensaje MIME
        mensaje = MIMEMultipart()
        mensaje["From"] = self.smtp_user
        mensaje["To"] = email_asesor
        mensaje["Subject"] = subject
        mensaje.attach(MIMEText(body, "plain"))

        # Enviar el correo
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, email_asesor, mensaje.as_string())
                print("Correo enviado con éxito al asesor.")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
