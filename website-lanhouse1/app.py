from flask import Flask, render_template, request, redirect, url_for
from models import cadastrar_usuario, listar_usuarios

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        nickname = request.form['nickname']
        cadastrar_usuario(nome, email, nickname)
        return redirect(url_for('usuarios'))
    return render_template('cadastro.html')

@app.route('/usuarios')
def usuarios():
    usuarios = listar_usuarios()
    return render_template('usuarios.html', usuarios=usuarios)

if __name__ == '__main__':
    app.run(debug=True)
