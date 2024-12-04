from components.twilio_component import TwilioManager
from api_keys.api_keys import recordatorio_ruleta

twilio_manager = TwilioManager()
template_content_sid = recordatorio_ruleta
parameters = '{"1": "Daniel"}'  # JSON string con parámetros

sid = twilio_manager.send_template_message(
    to_number='+51932709296',
    template_content_sid=template_content_sid,
    parameters=parameters
)