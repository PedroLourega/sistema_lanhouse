from app import app
from flask import render_template, request, flash
from datetime import datetime
from app.models import calcular_valor, adicionar_historico, cadastrar_usuario

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

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

@app.route("/calcular_sessao", methods=['GET', 'POST'])
def calcular_sessao():
    resultado = None
    if request.method == 'POST':
        entrada = request.form['entrada']
        saida = request.form['saida']
        formato = "%H:%M"
        hora_entrada = datetime.strptime(entrada, formato)
        hora_saida = datetime.strptime(saida, formato)

        if hora_saida < hora_entrada:
            flash('Erro: A hora de saída não pode ser anterior à hora de entrada.', 'error')
            return render_template('calcular_sessao.html', resultado=resultado)

        tempo_total = (hora_saida - hora_entrada).seconds // 60
        horas = tempo_total // 60
        minutos = tempo_total % 60
        valor_horas = horas * 30
        valor_minutos = minutos * 0.5
        descontos = [0.07, 0.09, 0.11, 0.13, 0.15]
        desconto = descontos[min(horas - 1, 4)] if horas > 0 else 0
        valor_bruto = valor_horas + valor_minutos
        valor_final = valor_bruto * (1 - desconto)

        tempo_formatado = f"{horas}h {minutos}m"
        resultado = {
            'tempo': tempo_formatado,
            'valor_bruto': valor_bruto,
            'valor_final': valor_final
        }

    return render_template('calcular_sessao.html', resultado=resultado)

@app.route('/registrar_tempo', methods=['GET', 'POST'])
def registrar_tempo():
    if request.method == 'POST':
        usuario_id = int(request.form['usuario_id'])
        horas_adicionais = int(request.form['horas'])
        minutos_adicionais = int(request.form['minutos'])

        # Conectar ao banco e buscar o tempo atual do usuário
        conn = conectar_banco()
        cursor = conn.cursor()

        # Obter as horas e minutos do usuário
        cursor.execute('''
            SELECT horas, minutos FROM usuarios WHERE id = ?
        ''', (usuario_id,))
        usuario = cursor.fetchone()

        if usuario:
            horas_atual = usuario[0]
            minutos_atual = usuario[1]

            # Adicionar o tempo ao usuário
            total_minutos = minutos_atual + minutos_adicionais
            horas_totais = horas_atual + horas_adicionais + total_minutos // 60
            minutos_totais = total_minutos % 60

            # Calcular o valor com base no tempo registrado
            valor_horas = horas_totais * 30  
            valor_minutos = minutos_totais * 0.5  

            # Aplicar descontos progressivos
            descontos = [0.07, 0.09, 0.11, 0.13, 0.15] 
            desconto = descontos[min(horas_totais - 1, 4)] if horas_totais > 0 else 0 
            valor_bruto = valor_horas + valor_minutos  
            valor_final = valor_bruto * (1 - desconto)  

            # Atualizar o banco com o tempo e o valor
            cursor.execute('''
                UPDATE usuarios 
                SET horas = ?, minutos = ?, valor = ?
                WHERE id = ?
            ''', (horas_totais, minutos_totais, valor_final, usuario_id))

            conn.commit()
            flash('Tempo registrado com sucesso!', 'success')
        else:
            flash('Usuário não encontrado.', 'error')

        conn.close()

    # Exibir a lista de usuários para selecionar
    usuarios = listar_usuarios_banco()
    return render_template('registrar_tempo.html', usuarios=usuarios)

def listar_usuarios_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios
