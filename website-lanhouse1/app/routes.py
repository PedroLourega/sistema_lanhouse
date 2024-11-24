from main import app
from flask import render_template
from app.app import app  # Importando 'app' de 'app.py'
from flask import render_template, request, redirect, url_for, flash
from app.models import calcular_valor, adicionar_historico

#rotas
@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/calcular_sessao")
def calcular_sessao():
    return "calcular_sessao"

@app.route("/registro")
def registro():
    return "registro"

@app.route('/registrar_entrada_saida', methods=['POST'])
def registrar_entrada_saida():
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        entrada = request.form['entrada']  # Esperando um formato datetime
        saida = request.form['saida']
        
        # Converte as entradas de tempo para datetime
        from datetime import datetime
        entrada = datetime.strptime(entrada, '%Y-%m-%d %H:%M:%S')
        saida = datetime.strptime(saida, '%Y-%m-%d %H:%M:%S')
        
        # Calcula o tempo total em minutos
        tempo_total = (saida - entrada).total_seconds() / 60
        
        # Calcula o valor total
        valor_total = calcular_valor(tempo_total)
        
        # Adiciona o registro ao histórico
        adicionar_historico(usuario_id, entrada, saida, tempo_total, valor_total)
        
        flash('Sessão registrada com sucesso!', 'success')
        return redirect(url_for('home'))

@app.route('/historico')
def historico():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM historico')
    historico_sessoes = cursor.fetchall()
    conn.close()
    
    return render_template('historico.html', historico=historico_sessoes)

