from email.mime.text import MIMEText
import datetime
import smtplib
from config import Config

def enviar_email_verificacion(destinatario, nombre, token):

    # Leer el archivo HTML
    with open('verificacionMail.html', 'r', encoding='utf-8') as archivo_html:
        contenido_html = archivo_html.read()
    
    anio = str(datetime.datetime.now().year)

    contenido_html = contenido_html.replace("{anio}", anio)
    contenido_html = contenido_html.replace("{nombre}", nombre)
    contenido_html = contenido_html.replace("{token}", token)

    msg = MIMEText(contenido_html, 'html', "utf-8")
    msg['Subject'] = 'Verificación de cuenta'
    #msg['From'] = Config.MAIL_ORIGEN
    msg['From'] = 'NoResponder@gmail.com'
    msg['To'] = destinatario

    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        server.starttls()
        server.login(Config.MAIL_ORIGEN, Config.MAIL_PASSWORD)
        server.send_message(msg)

def enviar_email_recuperacion(destinatario, nombre, token):
    
    #template_path = Path(__file__).parent.parent / "email_templates" / "recuperar.html"
    #with open(template_path, "r", encoding="utf-8") as f:
    
    # Leer el archivo HTML
    with open('emailRecuperacion.html', "r", encoding="utf-8") as archivo_html:
        html = archivo_html.read()

    anio = str(datetime.datetime.now().year)
    
    html = html.replace("{{nombre}}", nombre)
    html = html.replace("{{token}}", token)
    html = html.replace("{{anio}}", anio)

    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = "Recuperación de contraseña"
    msg["From"] = "no-reply@tu-dominio.com"
    msg["To"] = destinatario

    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        server.starttls()
        server.login(Config.MAIL_ORIGEN, Config.MAIL_PASSWORD)
        server.send_message(msg)