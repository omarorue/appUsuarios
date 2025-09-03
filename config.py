import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta')
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'appUsers'
    MAIL_ORIGEN = 'omarh.xx14@gmail.com'
    MAIL_PASSWORD = 'cscygiwtlmeanwoq'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
