import sqlite3 #importa o módulo sqlite para interegir com o banco de dados
from datetime import datetime, timedelta #importa as classes para controlar as datas e horas

#conecta no banco de dados
conn = sqlite3.connect('lanhouse.db') #Conecta oo banco de dados "lanhouse.db"
cursor = conn.cursor()#cria um cursor para executar comandos sql

#converte minutos para horas e minutos
def converter_para_horas_minutos(minutos):
    horas = minutos // 60 #divide os minutos por 60 para acessar as horas
    minutos_restantes = minutos % 60 #obtém o "resto" dos minutos
    return f"{horas}h {minutos_restantes}m" #retorna uma string formatada

#criar tabelas no banco de dados
def criar_tabelas():#cria a tabela de usuarios com colunas de ID, nome, email e nickname
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome TEXT, 
            email TEXT, 
            nickname TEXT
        )
    ''')
    #cria a tabela de históricos
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            tempo_total INTEGER,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    conn.commit() #salva as alterações no banco

#função para cadastrar usuários no banco de dados
def cadastrar_usuario():
    nome = input("Digite o nome do usuário: ") #solicita o nome
    email = input("Digite o e-mail do usuário: ") #solicita o email
    nickname = input("Digite o nickname do usuário: ") #solicita o nick

    #verifica se tudo foi preenchido
    if not nome or not email or not nickname: 
        print("Erro: Todos os campos devem ser preenchidos.\n")#mensagem de rro :(
        return #sai da função

    #insere dados de usuario na tabela de usuarios
    cursor.execute(''' 
        INSERT INTO usuarios (nome, email, nickname) 
        VALUES (?, ?, ?)
    ''', (nome, email, nickname))
    conn.commit()#salva no banco
    print("Usuário cadastrado com sucesso!\n")#mostra na tela a mensagem de sucesso :)

#função para listar usuários com o tempo total registrado
def listar_usuarios():
    #consulta a lista de usuarios e e soma os tempos totais no historico
    cursor.execute('''
        SELECT usuarios.id, usuarios.nome, usuarios.nickname, 
               IFNULL(SUM(historico.tempo_total), 0) AS tempo_total
        FROM usuarios
        LEFT JOIN historico ON usuarios.id = historico.usuario_id
        GROUP BY usuarios.id
    ''')
    usuarios = cursor.fetchall() #recupera todos os registros da consulta

    #verifica se tem usuarios cadastrados
    if not usuarios:
        print("Nenhum usuário cadastrado.\n") #se não houver usuarios cadastrados mostra esta mensagem de erro
        return #sai da funcao sem exibir os usuarios

    #exibe os usuarios cadastrados e seus tempos totais já formatados
    print("Usuários cadastrados:")
    for usuario in usuarios: 
        tempo_formatado = converter_para_horas_minutos(usuario[3]) #formata o tempo total em horas e min
        print(f"ID: {usuario[0]}, Nome: {usuario[1]}, Nickname: {usuario[2]}, Horas acumuladas: [{tempo_formatado}]") #mostra os dados com o tempo já formatado
    print()

#calcula valor de uma sessão baseada nos horários de entrada e saída
def calcular_valor_sessao():
    while True: #valida a entrada do usuário
        try:
            entrada = input("Digite o horário de entrada (formato HH:MM): ")#solicita o horário de entrada
            saida = input("Digite o horário de saída (formato HH:MM): ")#solicita o horário de saída

            #converte as strings para objetos no datetime
            formato = "%H:%M"
            hora_entrada = datetime.strptime(entrada, formato)
            hora_saida = datetime.strptime(saida, formato)

            #verifica se a hora de saída é anterior a hora de entrada
            if hora_saida < hora_entrada:
                print("Erro: A hora de saída não pode ser anterior à hora de entrada.")
                continue #restarta 

            #calcula o tempo total em minutos    
            tempo_total = (hora_saida - hora_entrada).seconds // 60  #tempo total em minutos
            tempo_formatado = converter_para_horas_minutos(tempo_total)  #formatar em horas e minutos

            print(f"Tempo total de uso: {tempo_formatado}")#printa o tempo total

            #calcular o valor com base no tempo
            horas = tempo_total // 60 #obtem o numero de horas completas
            minutos = tempo_total % 60 #obtem os min restantes
            valor_horas = horas * 30 #calcula o valor das horas
            valor_minutos = minutos * 0.5 #calcula o valor dos min

            #aplicar descontos
            descontos = [0.07, 0.09, 0.11, 0.13, 0.15] #descontos progressivos
            desconto = descontos[min(horas - 1, 4)] if horas > 0 else 0 #aplica o desconto referente 
            valor_bruto = valor_horas + valor_minutos #calcula o valor sem desconto
            valor_final = valor_bruto * (1 - desconto) #calcula o valor com desconto

            #exibe os valores calculados
            print(f"Tempo total: {tempo_formatado}") 
            print(f"Valor sem desconto: R$ {valor_bruto:.2f}")
            print(f"Valor com desconto: R$ {valor_final:.2f}\n")
            break #finaliza o laço

        except ValueError:
            print("Entrada inválida. Por favor, digite os horários no formato HH:MM.") #caso o valor seja digitado errado, mostra esta mensagem


#função para registrar tempo de uso de um usuário
def registrar_tempo():
    listar_usuarios() #exibe os usuarios
    
    try:
        usuario_id = int(input("Escolha o ID do usuário: ")) #solicita o id
    except ValueError:
        print("Entrada inválida. Tente novamente.") #mostra quando é digitado entradas invalidas
        return #saida

    while True: #valida as entradas de horas e mins
        try:
            horas = int(input("Quantas horas deseja adicionar? ")) #solicita horas
            minutos = int(input("Quantos minutos deseja adicionar? ")) #solicita minutos
            if horas < 0 or minutos < 0:
                print("Horas e minutos devem ser positivos. Tente novamente.") #valida numeros positivos
            else:
                break #saida com entradas validas
        except ValueError:
            print("Entrada inválida. Por favor, digite números inteiros.") #mostra essa mensagem quando é digitado entradas invalidas

    #calcula o tempo total em minutos
    tempo_total = horas * 60 + minutos

    #verifica se o usuário já tem algum tempo registrado no histórico
    cursor.execute(''' 
        SELECT tempo_total FROM historico WHERE usuario_id = ? 
    ''', (usuario_id,))
    resultado = cursor.fetchone()

    if resultado: #se ja existir tempo registrado, atualiza o tempo total
        tempo_total_antigo = resultado[0]
        tempo_total_atual = tempo_total_antigo + tempo_total
        cursor.execute(''' 
            UPDATE historico SET tempo_total = ? WHERE usuario_id = ?
        ''', (tempo_total_atual, usuario_id))
    else: #caso não tenha, insere um tempo novo no histórico do usuario
        cursor.execute(''' 
            INSERT INTO historico (usuario_id, tempo_total) 
            VALUES (?, ?)
        ''', (usuario_id, tempo_total))

    conn.commit() #salva no banco de dados as alterações 
    print(f"\nTempo registrado com sucesso para o usuário ID {usuario_id}!")
    tempo_formatado = converter_para_horas_minutos(tempo_total_atual if resultado else tempo_total) #formata o tempo total
    print(f"Tempo total acumulado: {tempo_formatado}\n")

#menu principal
def menu():
    criar_tabelas()  #garante que as tabelas existam no banco de dados

    while True:  #loop infinito para mostrar o menu
        print("--------------------------------")
        print("--x---Sistema-da-Lan-House---x--")
        print("--------------------------------")
        print("1. Cadastrar usuário")
        print("2. Listar usuários")
        print("3. Calcular valor de sessão")
        print("4. Registrar tempo de uso")
        print("5. Sair")
        print("--------------------------------")

        try:
            escolha = int(input("Escolha uma opção: "))  #solicita a escolha do usuário
        except ValueError:
            print("Entrada inválida...Favor digite um número correspondente à opção.")  #trata de entradas não válidas
            continue  #restart menu

        #executa a ação correspondente à escolha do usuário
        if escolha == 1:
            cadastrar_usuario()
        elif escolha == 2:
            listar_usuarios()
        elif escolha == 3:
            calcular_valor_sessao()
        elif escolha == 4:
            registrar_tempo()
        elif escolha == 5:
            print("Encerrando o programa. Até a próxima!")
            break  #saida
        else:
            print("Opção inválida... por favor, tente novamente.")  #trata das escolhas não válidas

#inicia o programa chamando a função menu()
if __name__ == "__main__":
    menu()

