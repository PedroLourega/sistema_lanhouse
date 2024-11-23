from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Função para conectar ao banco de dados
def get_db():
    conn = sqlite3.connect('lanhouse.db')
    conn.row_factory = sqlite3.Row  # Para retornar resultados como dicionários
    return conn

# Função para converter minutos em horas e minutos
def converter_para_horas_minutos(minutos):
    horas = minutos // 60
    minutos_restantes = minutos % 60
    return f"{horas}h {minutos_restantes}m"

# Rota para a página principal
@app.route('/')
def index():
    print("Aplicação Flask iniciada!")  # Adicionando um print para confirmar que o Flask iniciou
    return render_template('index.html')

# Rota para cadastrar um usuário
@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        nickname = request.form['nickname']

        if not nome or not email or not nickname:
            return "Erro: Todos os campos devem ser preenchidos."

        # Conectar ao banco de dados e inserir o usuário
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO usuarios (nome, email, nickname) 
            VALUES (?, ?, ?) 
        ''', (nome, email, nickname))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_usuarios'))  # Redireciona para a página de listagem de usuários
    return render_template('cadastrar_usuario.html')

# Rota para listar usuários
@app.route('/listar_usuarios')
def listar_usuarios():
    try:
        print("Conectando ao banco de dados...")  # Mensagem de debug
        conn = get_db()
        cursor = conn.cursor()
        print("Executando consulta SQL...")  # Mensagem de debug
        cursor.execute('''
            SELECT id, nome, nickname FROM usuarios
        ''')
        usuarios = cursor.fetchall()
        print(f"Usuários retornados: {usuarios}")  # Verifique se os dados estão sendo retornados
        conn.close()

        if usuarios:
            return render_template('listar_usuarios.html', usuarios=usuarios)
        else:
            return "Nenhum usuário encontrado."
    except Exception as e:
        return f"Ocorreu um erro ao listar os usuários: {e}"

# Rota para calcular o valor da sessão
@app.route('/calcular_valor', methods=['GET', 'POST'])
def calcular_valor():
    if request.method == 'POST':
        entrada = request.form['entrada']
        saida = request.form['saida']

        try:
            formato = "%H:%M"
            hora_entrada = datetime.strptime(entrada, formato)
            hora_saida = datetime.strptime(saida, formato)

            if hora_saida < hora_entrada:
                return "Erro: A hora de saída não pode ser anterior à hora de entrada."

            tempo_total = (hora_saida - hora_entrada).seconds // 60
            horas = tempo_total // 60
            minutos = tempo_total % 60
            valor_horas = horas * 30
            valor_minutos = minutos * 0.5
            descontos = [0.07, 0.09, 0.11, 0.13, 0.15]
            desconto = descontos[min(horas - 1, 4)] if horas > 0 else 0
            valor_bruto = valor_horas + valor_minutos
            valor_final = valor_bruto * (1 - desconto)
            return render_template('calcular_valor.html', valor_bruto=valor_bruto, valor_final=valor_final)
        except ValueError:
            return "Erro: Formato de hora inválido."

    return render_template('calcular_valor.html')

# Rota para registrar o tempo de uso do usuário
@app.route('/registrar_tempo', methods=['GET', 'POST'])
def registrar_tempo():
    if request.method == 'POST':
        # Pega os dados enviados pelo formulário
        usuario_id = request.form['usuario_id']
        entrada = request.form['entrada']
        saida = request.form['saida']

        try:
            # Converte os horários de entrada e saída para objetos datetime
            formato = "%H:%M"
            entrada = datetime.strptime(entrada, formato)
            saida = datetime.strptime(saida, formato)

            # Calcula a diferença de tempo em minutos
            tempo_usado = (saida - entrada).seconds / 60  # Convertendo segundos para minutos

            # Agora, registre o tempo no banco de dados
            conn = get_db()
            cursor = conn.cursor()

            # Inserindo os dados na tabela de registros
            cursor.execute('''
                INSERT INTO registro_uso (usuario_id, entrada, saida, tempo_usado)
                VALUES (?, ?, ?, ?)
            ''', (usuario_id, entrada.strftime(formato), saida.strftime(formato), tempo_usado))

            conn.commit()
            conn.close()

            # Mensagem de sucesso
            return f'Tempo registrado com sucesso! Usuário {usuario_id} usou {tempo_usado} minutos.'
        except ValueError as e:
            # Captura de erro específico para formatação das horas
            return f"Erro: Formato de hora inválido. Detalhes: {e}"
        except Exception as e:
            # Captura de erro geral
            return f'Ocorreu um erro ao registrar o tempo: {e}'
    
    # Caso seja um GET (quando a página é carregada), busca os usuários cadastrados
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, nickname FROM usuarios')
        usuarios = cursor.fetchall()
        conn.close()

        # Exibe a página com o formulário e a lista de usuários
        return render_template('registrar_tempo.html', usuarios=usuarios)
    except Exception as e:
        return f'Ocorreu um erro ao acessar o banco de dados: {e}'

if __name__ == "__main__":
    app.run(debug=True)
