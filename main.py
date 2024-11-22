import sqlite3
from datetime import datetime, timedelta

# Conectar ao banco de dados (ou criar se não existir)
conn = sqlite3.connect('lanhouse.db')
cursor = conn.cursor()

# Função para converter minutos para horas e minutos
def converter_para_horas_minutos(minutos):
    horas = minutos // 60
    minutos_restantes = minutos % 60
    return f"{horas}h {minutos_restantes}m"

# Criar tabelas no banco de dados
def criar_tabelas():
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

# Função para cadastrar usuários no banco de dados
def cadastrar_usuario():
    nome = input("Digite o nome do usuário: ")
    email = input("Digite o e-mail do usuário: ")
    nickname = input("Digite o nickname do usuário: ")

    if not nome or not email or not nickname:
        print("Erro: Todos os campos devem ser preenchidos.\n")
        return

    cursor.execute(''' 
        INSERT INTO usuarios (nome, email, nickname) 
        VALUES (?, ?, ?)
    ''', (nome, email, nickname))
    conn.commit()
    print("Usuário cadastrado com sucesso!\n")

# Função para listar usuários com o tempo total registrado
def listar_usuarios():
    cursor.execute('''
        SELECT usuarios.id, usuarios.nome, usuarios.nickname, 
               IFNULL(SUM(historico.tempo_total), 0) AS tempo_total
        FROM usuarios
        LEFT JOIN historico ON usuarios.id = historico.usuario_id
        GROUP BY usuarios.id
    ''')
    usuarios = cursor.fetchall()

    if not usuarios:
        print("Nenhum usuário cadastrado.\n")
        return

    print("Usuários cadastrados:")
    for usuario in usuarios:
        tempo_formatado = converter_para_horas_minutos(usuario[3])
        print(f"ID: {usuario[0]}, Nome: {usuario[1]}, Nickname: {usuario[2]}, Horas acumuladas: [{tempo_formatado}]")
    print()

# Função para calcular o valor de uma sessão baseada nos horários de entrada e saída
def calcular_valor_sessao():
    while True:
        try:
            entrada = input("Digite o horário de entrada (formato HH:MM): ")
            saida = input("Digite o horário de saída (formato HH:MM): ")

            # Converter as strings para objetos datetime
            formato = "%H:%M"
            hora_entrada = datetime.strptime(entrada, formato)
            hora_saida = datetime.strptime(saida, formato)

            # Calcular a diferença entre os horários
            if hora_saida < hora_entrada:
                print("Erro: A hora de saída não pode ser anterior à hora de entrada.")
                continue

            tempo_total = (hora_saida - hora_entrada).seconds // 60  # tempo total em minutos
            print(f"Tempo total de uso: {tempo_total} minutos")

            # Calcular o valor com base no tempo
            horas = tempo_total // 60
            minutos = tempo_total % 60
            valor_horas = horas * 30
            valor_minutos = minutos * 0.5

            # Aplicar descontos
            descontos = [0.07, 0.09, 0.11, 0.13, 0.15]  # Até 5 horas ou mais
            desconto = descontos[min(horas - 1, 4)] if horas > 0 else 0
            valor_bruto = valor_horas + valor_minutos
            valor_final = valor_bruto * (1 - desconto)

            print(f"Valor sem desconto: R$ {valor_bruto:.2f}")
            print(f"Valor com desconto: R$ {valor_final:.2f}\n")
            break

        except ValueError:
            print("Entrada inválida. Por favor, digite os horários no formato HH:MM.")

# Função para registrar tempo de uso de um usuário
def registrar_tempo():
    listar_usuarios()
    
    try:
        usuario_id = int(input("Escolha o ID do usuário: "))
    except ValueError:
        print("Entrada inválida. Tente novamente.")
        return

    while True:
        try:
            horas = int(input("Quantas horas deseja adicionar? "))
            minutos = int(input("Quantos minutos deseja adicionar? "))
            if horas < 0 or minutos < 0:
                print("Horas e minutos devem ser positivos. Tente novamente.")
            else:
                break
        except ValueError:
            print("Entrada inválida. Por favor, digite números inteiros.")

    # Calcular o tempo total em minutos
    tempo_total = horas * 60 + minutos

    # Verificar se o usuário já tem tempo registrado
    cursor.execute(''' 
        SELECT tempo_total FROM historico WHERE usuario_id = ? 
    ''', (usuario_id,))
    resultado = cursor.fetchone()

    if resultado:
        tempo_total_antigo = resultado[0]
        tempo_total_atual = tempo_total_antigo + tempo_total
        cursor.execute(''' 
            UPDATE historico SET tempo_total = ? WHERE usuario_id = ?
        ''', (tempo_total_atual, usuario_id))
    else:
        cursor.execute(''' 
            INSERT INTO historico (usuario_id, tempo_total) 
            VALUES (?, ?)
        ''', (usuario_id, tempo_total))

    conn.commit()
    print(f"\nTempo registrado com sucesso para o usuário ID {usuario_id}!")
    tempo_formatado = converter_para_horas_minutos(tempo_total_atual if resultado else tempo_total)
    print(f"Tempo total acumulado: {tempo_formatado}\n")

# Menu principal
def menu():
    criar_tabelas()

    while True:
        print("1. Cadastrar usuário")
        print("2. Listar usuários")
        print("3. Registrar tempo de uso")
        print("4. Calcular valor de uma sessão")
        print("5. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_usuario()
        elif opcao == "2":
            listar_usuarios()
        elif opcao == "3":
            registrar_tempo()
        elif opcao == "4":
            calcular_valor_sessao()
        elif opcao == "5":
            print("Saindo...")
            conn.close()  # Fechar a conexão ao banco de dados
            break
        else:
            print("Opção inválida. Tente novamente.\n")

menu()

