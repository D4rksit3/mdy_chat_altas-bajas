from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

from pymongo import MongoClient
import pandas as pd
import random, os

app = Flask(__name__)
app.secret_key = os.urandom(24)


login_manager = LoginManager()
login_manager.init_app(app)





# Función para cargar el usuario a partir del ID guardado en la sesión
@login_manager.user_loader
def load_user(user_id):
    # Aquí puedes agregar la lógica para cargar el usuario a partir del ID
    user = next((user for user in users if user.username == user_id), None)
    if user:
        return User(user.username, user.password)
    return None

# Configuración de la base de datos MongoDB
mongodb_host = '10.200.52.229'
mongodb_port = 27017
mongodb_database = 'rocketchat'
collection_name = 'users'

@app.route('/')
def home():
    return redirect(url_for('login'))
    
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET'])
@login_required
def upload():
    return render_template('upload.html')


@app.route('/uploads', methods=['POST'])
@login_required
def upload_file():
    def generar_codigo_aleatorio():
        codigo = ""
        for _ in range(16):
            digito = random.randint(0, 9)  # Genera un número aleatorio entre 0 y 9
            codigo += str(digito)  # Concatena el dígito al código
        return codigo
    
    file = request.files['file']
    df = pd.read_excel(file)
    
    # Conectarse a la base de datos MongoDB
    client = MongoClient(f'mongodb://{mongodb_host}:{mongodb_port}/?tls=false&directConnection=true')
    db = client[mongodb_database]
    collection = db[collection_name]
    
    usuarios_registrados = []
    usuarios_no_registrados = []

    for index, row in df.iterrows():
        username = row['username']
        name = row['name']
        user = "user"
        usersin = user.strip('\'"')

        if collection.find_one({'username': username}):
            usuarios_registrados.append(username)
            continue

        codigo_aleatorio = generar_codigo_aleatorio()

        data = {
            "_id": codigo_aleatorio,
            "services": {
                "password": { "bcrypt": "$2b$10$Ca/UXh5uGq6C30VyU64MZ.8TPR/VYpHopUn5qEKjzZSqGK1OLr8SC" },
                "email2fa": { "enabled": "true" }
            },
            "username": username,
            "emails": [
                { "address": username + '@mdy', "verified": False }
            ],
            "type": usersin,
            "status": "offline",
            "active": "true",
            
            "roles": [ "bot" ],
            "name": name,
            "requirePasswordChange": True,
            "settings": {}

        }

        collection.insert_one(data)
        usuarios_no_registrados.append(username)

    client.close()

    return render_template('res.html', usuarios_registrados=usuarios_registrados, usuarios_no_registrados=usuarios_no_registrados)

@app.route('/baja', methods=['GET'])
@login_required
def baja():
    return render_template('baja.html')

@app.route('/bajas', methods=['POST'])
@login_required
def bajas():
    file = request.files['file']
    df = pd.read_excel(file)
    
    # Conectarse a la base de datos MongoDB
    client = MongoClient(f'mongodb://{mongodb_host}:{mongodb_port}/?tls=false&directConnection=true')
    db = client[mongodb_database]
    collection = db[collection_name]

    user_baja = []



    
    for index, row in df.iterrows():
        username = row['username']
        data = {'username':username}

        collection.delete_many(data)
        user_baja.append(username)
    client.close()

    return render_template('res_baja.html', user_baja=user_baja)

# Simulación de una base de datos de usuarios


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_id(self):
        return self.username

users = [
    User(username='jroque', password='Mdy12345*'),
    User(username='galfaro', password='gabro')
]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Aquí puedes agregar la lógica para verificar el nombre de usuario y la contraseña
        # por ejemplo, comparando con una base de datos o con datos almacenados en alguna otra forma
        user = next((user for user in users if user.username == username and user.password == password), None)



        if user:

            # Iniciar sesión de usuario
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Credenciales inválidas')

    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    # Cerrar sesión de usuario
    logout_user()
    
    # Redireccionar al login
    return redirect(url_for('login'))

@app.errorhandler(401)
def unauthorized(error):
    # Renderizar una plantilla con el mensaje de error
    return render_template('401.html', message='Necesitas iniciar sesion para acceder a está vista.'), 401

@app.errorhandler(404)
def unauthorized(error):
    # Renderizar una plantilla con el mensaje de error
    return render_template('404.html', message='Está vista no existe.'), 404

@app.errorhandler(405)
def unauthorized(error):
    # Renderizar una plantilla con el mensaje de error
    return render_template('405.html', message='No tienes permitido ejecutar está vista.'), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
