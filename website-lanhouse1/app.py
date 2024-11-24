import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from models import cadastrar_usuario  

app = Flask(__name__)

# Definindo o caminho absoluto do banco de dados
DATABASE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db', 'lanhouse.db')

# Função para conectar ao banco de dados
def conectar_banco():
    print("Caminho do banco de dados:", DATABASE_PATH)  # Verificando o caminho
    conn = sqlite3.connect(DATABASE_PATH)  # Caminho absoluto do banco de dados
    return conn

# Necessário para usar flash
app.secret_key = 'seu_segredo_aqui'  # Altere isso para algo único para sua aplicação

# Função para criar as tabelas
def criar_tabelas():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            nickname TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Criação das tabelas ao iniciar a aplicação
criar_tabelas()

# Rota para o cadastro de usuário
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        nickname = request.form['nickname']
        
        # Cadastrar o usuário (insere no banco de dados)
        cadastrar_usuario(nome, email, nickname)
        
        # Após o cadastro, exibe a mensagem de sucesso com o flash
        flash('Usuário cadastrado com sucesso!', 'success')

        # Não redireciona, mantém na mesma página de cadastro
        return render_template('cadastro.html')
    
    return render_template('cadastro.html')

# Rota para a página inicial
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
