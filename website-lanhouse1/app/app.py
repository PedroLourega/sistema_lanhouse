import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from app.models import cadastrar_usuario
import sys
from app import models

# Definindo o caminho absoluto do banco de dados
db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'db')  # Corrigido o caminho para fora de app
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
db_path = os.path.join(db_dir, 'novo_lanhouse.db')

# Adicionando o caminho correto do projeto para buscar os módulos
sys.path.append('e:/Codes/courses/a3-fadergs/website-lanhouse1')

# Caminho absoluto do banco de dados
DATABASE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'db', 'novo_lanhouse.db')

# Configuração do Flask para garantir que ele encontre os templates corretamente
app = Flask(__name__, template_folder='templates')  # Corrigido para buscar diretamente na pasta templates

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

# Função para cadastrar o usuário
def cadastrar_usuario(nome, email, nickname):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Inserir os dados do novo usuário na tabela
    cursor.execute(''' 
        INSERT INTO usuarios (nome, email, nickname)
        VALUES (?, ?, ?)
    ''', (nome, email, nickname))
    
    conn.commit()
    conn.close()

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
    
    return render_template('cadastro.html')

# Rota para a página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Rota para listar os usuários
@app.route('/listar_usuarios')
def listar_usuarios():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()
    
    return render_template('listar_usuarios.html', usuarios=usuarios)

if __name__ == '__main__':
    app.run(debug=True)
