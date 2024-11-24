import sqlite3
from datetime import datetime

DB_PATH = "db/lanhouse.db"

def conectar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    return conn, cursor

def criar_tabelas():
    conn, cursor = conectar_banco()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome TEXT, 
            email TEXT, 
            nickname TEXT
        )
    ''')
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            tempo_total INTEGER,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()
    conn.close()

# Chamamos a função para criar as tabelas ao iniciar o app
criar_tabelas()

def cadastrar_usuario(nome, email, nickname):
    conn, cursor = conectar_banco()
    cursor.execute('''
        INSERT INTO usuarios (nome, email, nickname) 
        VALUES (?, ?, ?)
    ''', (nome, email, nickname))
    conn.commit()
    conn.close()

def listar_usuarios():
    conn, cursor = conectar_banco()
    cursor.execute('''
        SELECT usuarios.id, usuarios.nome, usuarios.nickname, 
               IFNULL(SUM(historico.tempo_total), 0) AS tempo_total
        FROM usuarios
        LEFT JOIN historico ON usuarios.id = historico.usuario_id
        GROUP BY usuarios.id
    ''')
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios
