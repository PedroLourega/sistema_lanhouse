import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

# Configuração do Flask para buscar templates fora da pasta 'app'
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Caminho do banco de dados
db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'db')
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
DATABASE_PATH = os.path.join(db_dir, 'novo_lanhouse.db')

# Configuração para mensagens flash
app.secret_key = 'seu_segredo_aqui'

# Função para conectar ao banco de dados
def conectar_banco():
    print("Caminho do banco de dados:", DATABASE_PATH)  # Verificando o caminho
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

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

# Criar tabelas ao iniciar
criar_tabelas()

# Função para cadastrar usuário
def cadastrar_usuario(nome, email, nickname):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO usuarios (nome, email, nickname)
        VALUES (?, ?, ?)
    ''', (nome, email, nickname))
    conn.commit()
    conn.close()

# Rota para a página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Rota para cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        nickname = request.form['nickname']
        cadastrar_usuario(nome, email, nickname)
        flash('Usuário cadastrado com sucesso!', 'success')
    return render_template('cadastro.html')

# Rota para listar usuários
@app.route('/listar_usuarios')
def listar_usuarios():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()
    return render_template('listar_usuarios.html', usuarios=usuarios)

# Rota para calcular a sessão
@app.route('/calcular_sessao', methods=['GET', 'POST'])
def calcular_sessao():
    resultado = None
    if request.method == 'POST':
        entrada = request.form['entrada']
        saida = request.form['saida']
        
        try:
            # Convertendo as horas e minutos de entrada e saída
            entrada_hora, entrada_minuto = map(int, entrada.split(":"))
            saida_hora, saida_minuto = map(int, saida.split(":"))
            
            # Calcular o tempo total em minutos
            tempo_entrada = entrada_hora * 60 + entrada_minuto
            tempo_saida = saida_hora * 60 + saida_minuto
            tempo_total = tempo_saida - tempo_entrada
            
            # Cálculo do valor por hora e por minuto
            horas = tempo_total // 60  # Calcula o número de horas
            minutos = tempo_total % 60  # Calcula os minutos restantes

            valor_horas = horas * 30  # R$30 por hora
            valor_minutos = minutos * 0.5  # R$0,50 por minuto
            
            # Aplicando descontos progressivos conforme a quantidade de horas
            descontos = [0.07, 0.09, 0.11, 0.13, 0.15]  # Descontos progressivos para 1h, 2h, 3h, 4h, 5h+
            desconto = descontos[min(horas - 1, 4)] if horas > 0 else 0  # Aplica o desconto de acordo com a quantidade de horas

            # Calculando o valor bruto e o valor final com o desconto
            valor_bruto = valor_horas + valor_minutos  # Valor sem desconto
            valor_final = valor_bruto * (1 - desconto)  # Valor com o desconto aplicado

            # Formatando o tempo em horas e minutos
            tempo_formatado = f"{horas}h {minutos}m"
            
            # Salvando os resultados
            resultado = {
                'tempo': tempo_formatado,
                'valor_bruto': valor_bruto,
                'valor_final': valor_final
            }
        except Exception as e:
            flash(f"Erro ao calcular: {e}", 'error')

    return render_template('calcular_sessao.html', resultado=resultado)

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True)
