from  components.email_component import EmailManager

email_manager = EmailManager("smtp.gmail.com",587,"eselrey551@gmail.com","jhjx qnbi oaaq sree")

inmueble_info = {
    "id_inmueble": "40",
    "direccion": "AV BENAVIDES CERCA A LA AV REPUBLICA DE PANAMA",
    "ciudad": "Miraflores, Lima",
    "precio_texto": "S/ 5,700 - USD 390,000"
}
cliente_info = {
    "nombre":  "Carlos",
    "email": "carlos.perez@example.com",
    "telefono": "+51 987654321"
}        
email_manager.enviar_correo_asesor("Daniel Rivas","daniel.erp.26@gmail.com",inmueble_info,cliente_info)