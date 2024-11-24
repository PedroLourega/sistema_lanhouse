import sqlite3

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect('db/lanhouse.db')  # Caminho do banco de dados
    return conn

# Função para criar a tabela 'usuarios' se ela não existir
def criar_tabelas():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            nickname TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Função para cadastrar um usuário
def cadastrar_usuario(nome, email, nickname):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nome, email, nickname) VALUES (?, ?, ?)", (nome, email, nickname))
    conn.commit()
    conn.close()
