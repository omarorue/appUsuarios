from flask import Blueprint, render_template, redirect, request, session, url_for, current_app
from app.models.user_model import *
from app.utils.email import enviar_email_verificacion, enviar_email_recuperacion
import hashlib, uuid
import json
import os
from datetime import datetime, timedelta

auth_bp = Blueprint(
    'auth',
    __name__,
    template_folder='templates',
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)

anio = str(datetime.now().year)

#=============================================
#   Prueba
#=============================================
"""
@auth_bp.route('/')
def inicio():
    titulo = '⚠️ La cuenta no esta verificada.'
    mensaje = 'Por favor revisá tu email.'
    link = '/registro'
    return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)
"""
#=============================================


def generar_token():
    return hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest()

@auth_bp.route('/')
def inicio():
    if 'usuario_id' in session:
        return redirect(url_for('auth.dashboard'))
    
    return render_template('inicio.html')

@auth_bp.route('/registro', methods=['GET', 'POST'], endpoint='registro')
def registro():
    if request.method == 'POST':
        data = request.form.to_dict()
        #DNI = request.form.get('nro_documento')
        if chequear_nroDNI(data['nro_documento']) == 'ya_existe':
            # === Enviar Mensaje === #
            titulo = ' ❌ Nro de documento repetido.'
            mensaje = 'Ya hay un usuario con ese Nro'
            link = '/ingreso'
            return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)    
            #return "Ya existe un usuario con ese Nro de documento."
        data['password'] = hashlib.sha256(data['password'].encode()).hexdigest()
        token = generar_token()
        expira = (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')

        crear_usuario(data, token, expira)
        enviar_email_verificacion(data['email'],data['nombre'], token)
        # === Enviar Mensaje === #
        titulo = ' ✅ Registro exitoso'
        mensaje = 'Verificá tu correo.'
        link = '/'
        return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)
        #return "Registro exitoso. Verificá tu correo."

    return render_template('ingreso.html')    #la pag ingreso: reemplaza LOGIN, REGISTRO

@auth_bp.route('/verificar')
def verificar():
    token = request.args.get('token')
    if not token:
        # === Enviar Mensaje === #
        titulo = ' ❌ Error ❌'
        mensaje = 'Falta token de ingreso.'
        link = '/ingreso'
        return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)
        #return render_template('verificacion_estado.html', estado='falta_token')

    resultado = verificar_token(token)

    return render_template('verificacionRegistro.html', estado=resultado)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_ingresada = request.form['password']
        password_hash = hashlib.sha256(password_ingresada.encode()).hexdigest()

        usuario = obtener_usuario_por_email(email)   # Devuelve (id, email, password, verificado, nombre)

        if usuario:
            user_id, email, password_db, verificado, nombre = usuario

            if not verificado:
                # === Enviar Mensaje === #
                titulo = '⚠️ La cuenta no esta verificada.'
                mensaje = 'Por favor revisá tu email.'
                link = "/"
                return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)
                #return "Tu cuenta aún no está verificada. Por favor revisá tu email."

            if password_hash == password_db:
                session['usuario_id'] = user_id
                session['usuario_nombre'] = nombre
                session['usuario_email'] = email
                return redirect(url_for('auth.dashboard'))
            
        # === Enviar Mensaje === #
        titulo = '⚠️ Error '
        mensaje = 'Email o Contraseña incorrectos.'
        link = '/'
        return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)
        #return "Email o contraseña incorrectos."

    return render_template('ingreso.html', opcion='login')

@auth_bp.route('/dashboard')
def dashboard():
    hora = datetime.now().hour
    if 'usuario_id' not in session:
        return redirect('ingreso.html', opcion='login')
    
    nombre = session['usuario_nombre']
    mail = session['usuario_email']

    credito = buscar_credito(nombre, mail)
    
    return render_template('dashboard.html', nombre=nombre, hora=hora, credito=int(credito))
    #return f"Hola {session['usuario_nombre']}, {session['usuario_email']} ¡bienvenido a tu panel!"

@auth_bp.route('/logout')
def logout():
    session.clear()
    return render_template('inicio.html')

@auth_bp.route('/inicioRecuperacion')
def inicioRecuperacion():
    return render_template('ingreso.html', opcion='recuperar')

@auth_bp.route('/historial')
def historial():
    return render_template('historial.html')

@auth_bp.route('/preferencias')
def preferencias():
    return render_template('preferencias.html')

@auth_bp.route("/toggle/<int:nro>/<estado>")
def toggle(nro, estado):
    print(f"Toggle {nro} está {estado.upper()}")
    return "", 204

@auth_bp.route('/acerca')
def acerca():
    ruta = os.path.join(current_app.root_path, 'static', 'textos', "preguntas.txt")
    with open(ruta, "r" , encoding="utf-8") as file:
        preguntas = json.load(file)
    return render_template('acerca.html', preguntas=preguntas)

@auth_bp.route('/terminosPolitica', methods=['GET'])
def terminosPolitica():
    """
    ruta = os.path.join(current_app.root_path, 'static', 'textos', "terminosCondiciones.txt")
    with open(ruta, encoding='utf-8') as f:
        contenido = f.read()
    return render_template('terminosPolitica.html', contenido=contenido)
    """
    return render_template('terminosPolitica.html')

@auth_bp.route('/perfil')
def perfil():
    mail = session['usuario_email']
    nombre = session['usuario_nombre']
    datos = get_datos_usuario(mail, nombre)
    return render_template('perfil.html', mail=mail, nombre=nombre, datos=datos)

@auth_bp.route('/ingresoLogin')
def ingreso_login():
    return render_template('ingreso.html', opcion='login')

@auth_bp.route('/ingresoCambioPass')
def ingreso_cambioPass():
    return render_template('ingreso.html', opcion='cambioPass')

@auth_bp.route('/ingresoRecuperar')
def ingreso_recuperar():
    return render_template('ingreso.html', opcion='recuperar')

@auth_bp.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        email = request.form.get("email")
        documento = request.form.get("documento")

        usuario = get_usuario_verificado(email, documento)  #Devuelve: ('id', 'nombre', 'email')
        if not usuario:
            # === Enviar Mensaje === #
            titulo = ' ❌ Error ❌'
            mensaje = 'No existe cuenta verificada con esos datos.'
            link = '/ingresoRecuperar'
            return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)
            #return "Error: No existe cuenta verificada con esos datos."
        
        usuarioEmail = usuario[2]
        usuarioNombre = usuario[1]
        usuarioId = usuario[0]

        #token = generar_token()
        token = str(uuid.uuid4())
        set_token_recuperacion(usuarioId, token)  #Guarda el token y el intervalo en la BD

        enviar_email_recuperacion(usuarioEmail, usuarioNombre, token)
        
        # === Enviar Mensaje === #
        titulo = ' ✅ Mail Enviado'
        mensaje = 'Se envio un mail para poder cambiar de contraseña.'
        link = '/'
        return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)
        #return 'Se ha enviado un enlace para restablecer tu contraseña.'

    return redirect('/')
        
@auth_bp.route("/cambiar_password", methods=["GET", "POST"])
def cambiar_password():
    token = request.args.get("token")
    if not token:
        # === Enviar Mensaje === #
        titulo = ' ❌ Error ❌'
        mensaje = 'Falta token de ingreso.'
        link = '/ingreso'
        return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)

    if request.method == "POST":
        nueva = request.form["nueva"]
        confirmacion = request.form["confirmacion"]

        if nueva != confirmacion:
             # === Enviar Mensaje === #
            titulo = ' ⚠️Error '
            mensaje = 'Las contraseñas no coinciden.'
            link = '/ingresoLogin'
            return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)
            #return 'Las contraseñas no coinciden.'
        
        hash_pass = hashlib.sha256(nueva.encode()).hexdigest()

        if actualizar_password(token, hash_pass):
            # === Enviar Mensaje === #
            titulo = ' ✅ Contraseña cambiada'
            mensaje = 'Se ha cambiado la contraseña exitosamente!'
            link = '/'
            return render_template('error.html', titulo=titulo, mensaje=mensaje, volver=link)
            #return 'Contraseña actualizada correctamente.'
        else:
            return 'Token inválido o expirado.'

    return render_template("ingreso.html", token=token, opcion='cambioPass')

@auth_bp.route('/muestraOpcionesApp')
def mostrarPerfil():
    nombre = session['usuario_nombre']
    mail = session['usuario_email']
    apellido = buscarApellido(nombre, mail)
    return render_template('muestraOpcionesApp.html', nombre=nombre, mail=mail, apellido=apellido[0], anio=anio )
