import sqlite3
import os
from datetime import datetime

db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db')
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Função para conectar ao banco de dados
def conectar_banco():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db', 'novo_lanhouse.db')
    print("Caminho absoluto do novo banco de dados:", db_path)
    conn = sqlite3.connect(db_path)  # Caminho absoluto do banco de dados
    return conn

def criar_tabelas():
    conn = conectar_banco()
    cursor = conn.cursor()

    # Criação da tabela 'usuarios'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            nickname TEXT NOT NULL,
            horas INTEGER DEFAULT 0,
            minutos INTEGER DEFAULT 0
        )
    ''')

    # Criação da tabela 'historico'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            entrada DATETIME,
            saida DATETIME,
            tempo_total INTEGER,  -- tempo em minutos
            valor_total REAL,  -- valor calculado
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    conn.commit()
    conn.close()

# Função para cadastrar usuário no banco de dados
def cadastrar_usuario(nome, email, nickname):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (nome, email, nickname)
        VALUES (?, ?, ?)
    ''', (nome, email, nickname))
    conn.commit()
    conn.close()

# Função para adicionar histórico no banco de dados
def adicionar_historico(usuario_id, entrada, saida, tempo_total, valor_total):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO historico (usuario_id, entrada, saida, tempo_total, valor_total)
        VALUES (?, ?, ?, ?, ?)
    ''', (usuario_id, entrada, saida, tempo_total, valor_total))
    conn.commit()
    conn.close()

def calcular_valor(tempo_total):
    preco_por_minuto = 0.5  # Preço por minuto, como exemplo
    desconto = 0
    
    if tempo_total >= 60:
        desconto = 0.07  # 7% de desconto para 1h ou mais
    if tempo_total >= 120:
        desconto = 0.09  # 9% de desconto para 2h ou mais
    if tempo_total >= 180:
        desconto = 0.11  # 11% de desconto para 3h ou mais
    if tempo_total >= 240:
        desconto = 0.13  # 13% de desconto para 4h ou mais
    if tempo_total >= 300:
        desconto = 0.15  # 15% de desconto para 5h ou mais

    valor_total = tempo_total * preco_por_minuto
    valor_com_desconto = valor_total * (1 - desconto)
    
    return valor_com_desconto

# Função para criar a tabela de histórico ao iniciar a aplicação
def criar_tabela_historico():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            entrada DATETIME,
            saida DATETIME,
            tempo_total INTEGER,  -- tempo em minutos
            valor_total REAL,  -- valor calculado
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()
    conn.close()

def alterar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Adiciona a coluna 'horas' à tabela 'usuarios', se ela não existir
    cursor.execute('''ALTER TABLE usuarios ADD COLUMN horas INTEGER DEFAULT 0;''')
    
    conn.commit()
    conn.close()
# Criação da tabela de histórico ao iniciar a aplicação
criar_tabelas()

