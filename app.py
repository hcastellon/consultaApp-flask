import os
import mysql.connector
from flask import Flask, render_template, request, session, redirect
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='static')
app.secret_key = 'mi_clave_secreta'  # Cambia esto por tu propia clave secreta

# Acceder a los secretos desde las variables de entorno
host = os.getenv('DATABASE_HOST')
usuario = os.getenv('DATABASE_USER')
database = os.getenv('DATABASE_NAME')


# Función para autenticar al usuario en la base de datos
def authenticate_user(username, password):
    # Establece la conexión a la base de datos
    connection = mysql.connector.connect(
        host=host,
        user=usuario,
        database=database
    )

    # Crea un cursor para ejecutar consultas SQL
    cursor = connection.cursor()

    # Consulta SQL para buscar al usuario en la base de datos
    query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
    values = (username, password)

    # Ejecuta la consulta
    cursor.execute(query, values)

    # Obtiene el resultado de la consulta
    user = cursor.fetchone()

    # Cierra el cursor y la conexión a la base de datos
    cursor.close()
    connection.close()

    # Si se encontró un usuario con las credenciales proporcionadas, retorna True; de lo contrario, retorna False
    if user:
        return True
    else:
        return False


def ejecutar_consulta():
    # Establecer la conexión con la base de datos
    conn = mysql.connector.connect(host=host, user=usuario, db='registrodb')

    # Crear un cursor para ejecutar la consulta
    cursor = conn.cursor()

    # Ejecutar la consulta
    cursor.execute('SELECT * FROM inf_profesor')

    # Obtener los resultados de la consulta
    resultados = cursor.fetchall()

    # Cerrar la conexión y el cursor
    cursor.close()
    conn.close()

    return resultados


# Ruta principal
@app.route('/')
def index():
    return render_template('login.html')


# Ruta para autenticarse
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Realiza la autenticación utilizando la función authenticate_user
    if authenticate_user(username, password):
        session['logged_in'] = True
        session['username'] = username
        return redirect('/consultas')
    else:
        session['logged_in'] = False
        error = 'Usuario o contraseña inválidos'  # Mensaje de error cuando el usuario es inválido
        return render_template('login.html', error=error)


# funcion para cerrar sesión
@app.route('/login', methods=['GET'])
def show_login():
    # Obtener el mensaje de cierre de sesión de la sesión
    logout_message = session.pop('logout_message', None)

    # Renderizar la página de inicio de sesión y pasar el mensaje de cierre de sesión como contexto
    return render_template('login.html', logout_message=logout_message)


# Ruta para mostrar la página de consultas
@app.route('/consultas')
def consultas():
    # Verificar si el usuario está autenticado
    if not session.get('logged_in'):
        return redirect('/login')

    # Obtener el nombre de usuario de la sesión
    username = session['username']

    opciones = [
        {
            'id': 1,
            'titulo': 'Consulta 1',
            'descripcion': 'Descripción de la consulta 1',
            'imagen': 'ruta_de_la_imagen_1.jpg'
        },
        {
            'id': 2,
            'titulo': 'Consulta 2',
            'descripcion': 'Descripción de la consulta 2',
            'imagen': 'ruta_de_la_imagen_2.jpg'
        },
        # Agrega más opciones de consulta si es necesario
    ]
    return render_template('consultas.html', opciones=opciones, username=username)


# Ruta para la consulta 1
@app.route('/consultas/consulta1', methods=['GET'])
def consulta1_get():
    # Verificar si el usuario está autenticado
    if not session.get('logged_in'):
        return redirect('/login')

    # Renderizar la página de consulta 1 y pasar los resultados como contexto
    return render_template('consulta1.html')


@app.route('/consultas/consulta1', methods=['POST'])
def consulta1_post():
    if not session.get('logged_in'):
        return redirect('/login')
    opcion_id = request.form['opcion_id']
    if opcion_id == '1':
        # Ejecutar la consulta y obtener los resultados
        obtener_resultados = ejecutar_consulta()
        return render_template('consulta1.html', resultados=obtener_resultados)
    elif opcion_id == '2':
        # Lógica para la segunda opción de consulta
        # ...
        return render_template('consulta2.html')
    else:
        # Opción inválida, puedes redirigir a una página de error o mostrar un mensaje de error en la misma página
        return render_template('error.html', mensaje='Opción inválida')


# Ruta para seleccionar variables
@app.route('/select')
def select():
    if not session.get('logged_in'):
        return redirect('/')

    # Renderiza el formulario de selección de variables
    return render_template('select.html')


# Función auxiliar para obtener el nombre de usuario desde la sesión
@app.context_processor
def inject_username():
    if 'username' in session:
        return dict(username=session['username'])
    return dict(username=None)


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    # Eliminar los datos de la sesión
    session.clear()

    # Redirigir al usuario a la página de inicio de sesión
    return redirect('/login')




if __name__ == '__main__':
    app.run(debug=True)
