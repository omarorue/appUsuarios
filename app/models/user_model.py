from flask import flash
from app import mysql
from datetime import datetime

def crear_usuario(data, token, expira):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO usuarios (
            nombre, apellido, email, password, nro_documento, telefono,
            cumple, credito, fecha_creacion, nro_habitacion,
            verificado, token, token_expira
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s)
    """, (
        data['nombre'], data['apellido'], data['email'], data['password'],
        data['nro_documento'], data['telefono'], data['cumple'],
        float(data.get('credito', 0.0)),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        data.get('nro_habitacion'), token, expira
    ))
    mysql.connection.commit()
    cur.close()

def verificar_token(token):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, token_expira, verificado FROM usuarios WHERE token = %s", (token,))
    resultado = cur.fetchone()
    
    if not resultado:
        return 'token_invalido'
    
    user_id, token_expira, verificado = resultado
    
    if verificado:
        return 'ya_verificado'
    
        #if datetime.strptime(token_expira, '%Y-%m-%d %H:%M:%S') < datetime.now():
    if token_expira < datetime.now():
        return 'token_expirado'
    
    cur.execute("UPDATE usuarios SET verificado = 1, token = NULL, token_expira = NULL WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    return 'verificacion_exitosa'

def obtener_usuario_por_email(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, email, password, verificado, nombre FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()
    cur.close()
    return usuario  # Devuelve (id, email, password, verificado, nombre)

def buscarApellido(nombre, email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT apellido FROM usuarios WHERE nombre = %s AND email = %s", (nombre, email,))
    apellido = cur.fetchone()
    cur.close()
    return apellido  # Devuelve (apellido)

def buscar_credito(nombre, email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT credito FROM usuarios WHERE nombre = %s AND email = %s" , (nombre, email))
    cred = cur.fetchone()
    credito = int(cred[0])
    cur.close()
    return credito

def chequear_nroDNI(nro_documento):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE nro_documento = %s", (nro_documento,))
    usuario_existente = cur.fetchone()
    cur.close()

    if usuario_existente:
       return 'ya_existe'
    
def get_datos_usuario(email, nombre):
    cur = mysql.connection.cursor()
    cur.execute("SELECT apellido, nro_documento, telefono, cumple, nro_habitacion FROM usuarios WHERE email = %s AND nombre = %s", (email, nombre,))
    usuario = cur.fetchone()
    return usuario

def get_usuario_verificado(email, documento):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT id, nombre, email
                FROM usuarios
                WHERE email=%s AND nro_documento=%s AND verificado=1
                """, (email, documento))
    return cur.fetchone()

def set_token_recuperacion(user_id, token):
    cur = mysql.connection.cursor()
    cur.execute("""
                UPDATE usuarios
                SET token=%s, token_expira=NOW() + INTERVAL 1 HOUR
                WHERE id=%s
                """, (token, user_id))
    mysql.connection.commit()
    cur.close()

def actualizar_password(token, password):
    cur = mysql.connection.cursor()
    cur.execute("""
                UPDATE usuarios
                SET password=%s, token=NULL, token_expira=NULL
                WHERE token=%s AND token_expira > NOW()
                """, (password, token))
    return cur.rowcount > 0