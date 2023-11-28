import json
import os
import oracledb
import pandas as pd
import datetime
import time
import sys
import re

def salvar_dados_json(dados):
    with open('dados.json', 'w') as arquivo:
        json.dump(dados, arquivo)

def carregar_dados_json():
    try:
        with open('dados.json', 'r') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return {"usuario": {}}

# Validações de cadastro
def validar_cpf(cpf):
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    return True

def validar_senha(senha):
    maiuscula = False
    minuscula = False
    numero = False

    for c in senha:
        if c.isupper():
            maiuscula = True
        if c.islower():
            minuscula = True
        if c.isdigit():
            numero = True

    return maiuscula and minuscula and numero

def validar_genero(genero):
    if len(genero) != 1 or not genero.isalpha():
        return False
    return True


def validar_email(email):
    return "@" in email

def validar_formato_data(data):
    # Padrão de expressão regular para o formato de data dd/mm/yyyy
    padrao_data = re.compile(r'^\d{2}/\d{2}/\d{4}$')

    # Verifica se a entrada corresponde ao padrão
    return bool(padrao_data.match(data))

def validar_formato_horario(horario):
    # Padrão de expressão regular para o formato de horário HH:mm
    padrao_horario = re.compile(r'^[0-2][0-9]:[0-5][0-9]$')

    # Verifica se a entrada corresponde ao padrão
    return bool(padrao_horario.match(horario))

# fazer login do usuario
def fazer_login():
    if not os.path.exists('dados.json'):
        print("\33[1;37mDesculpe..Parece que ainda não foi feito nenhum cadastro!\33[m")
        return None

    dados = carregar_dados_json()
    usuario = dados['usuario']
    email = input("E-mail: ")
    senha = input("Senha: ")

    # Crie um cursor para executar as consultas
    inst_login = conn.cursor()

    inst_login.execute(
        f"SELECT * FROM USUARIO WHERE email = '{email}' AND senha = '{senha}'")

    cliente_db = inst_login.fetchone()

    if cliente_db is not None:
        usuario['id'] = cliente_db[0]
        usuario['nome'] = cliente_db[1]
        usuario['cpf'] = cliente_db[2]
        usuario['idade'] = str(cliente_db[3])
        usuario['sexo'] = cliente_db[4]
        usuario['email'] = cliente_db[5]
        usuario['senha'] = cliente_db[6]
        usuario['objetivo'] = cliente_db[7]
        salvar_dados_json(dados)
        return cliente_db[0]  # Retorna o ID do usuário
    else:
        print("\33[1;31mEmail ou senha incorretos.\33[m")
        return None

# Cadastrar usuario
def cadastrar_usuario():
    dados = carregar_dados_json()
    usuario = dados['usuario']
    print("\n\33[1;33mVamos realizar seu cadastro :)\33[m")
    usuario['nome'] = input("nome: ")

    while True:
        usuario['cpf'] = input("CPF:")
        if validar_cpf(usuario['cpf']):
            break
        else:
            print("\33[1;31mCPF inválido. Deve conter 11 dígitos numéricos.\33[m")

    usuario['idade'] = input("idade: ")

    while True:
        usuario['sexo'] = input("sexo(M ou F):").upper()
        if validar_genero(usuario['sexo']):
            break
        else:
            print("\33[1;31mOpção inválida. Informe apenas M para masculino e F para feminino\33[m")

    while True:
        usuario['email'] = input("Email:")
        if validar_email(usuario['email']):
            break
        else:
            print("\33[1;31mEmail inválido.\33[m")
    while True:
        usuario['senha'] = input("Senha:")
        if validar_senha(usuario['senha']):
            break
        else:
            print(
                "\33[1;33mSenha inválida. Deve conter pelo menos: \n* uma letra maiúscula \n* uma letra minúscula \n* um número\33[m")
  
    print("\nPara darmos andamento precisamos saber seu objetivo por aqui!\n\33[1;33m Vamos trazer tudo personalizado para você :)\33[m")
    print("""
        1 - Estou grávida
        2 - Quero melhorar minha saúde
        3 - Quero saber como posso evitar doenças transmissiveis
        4 - Quero ter hábitos saúdaveis
    """)
    while True:
        usuario['objetivo'] = input("Qual o seu objetivo:")
        if usuario['objetivo'] not in {"1", "2", "3", "4"}:
            print("\33[1;31m Opção inválida\33[m")
        else:
            break

    print("\n*Confirme seus dados*\n")
    for campo, valor in usuario.items():
        print(f"\33[1;33m{campo}.........: {valor}\33[m")
    while True:
        finalizando = input("Os seus dados estão corretos (N / S)? \n").upper()
        if finalizando == "N":
            print("\33[1;33m Refazer cadastro, selecione o número 1 novamente e preencha as informações.\33[m")
            break
        if finalizando == "S":
            try:
                cadastro_cliente = f"""INSERT INTO USUARIO(nome, cpf, idade, sexo, email, senha, objetivo) 
                                      VALUES ('{usuario['nome']}', '{usuario['cpf']}', '{usuario['idade']}', 
                                              '{usuario['sexo']}', '{usuario['email']}', '{usuario['senha']}', '{usuario['objetivo']}')"""
                inst_cadastro.execute(cadastro_cliente)
                conn.commit()

                # Verifica se o cadastro foi bem-sucedido antes de tentar obter o ID
                if inst_cadastro.rowcount > 0:
                    inst_cadastro.execute(f"SELECT id FROM USUARIO WHERE email = '{usuario['email']}' AND senha = '{usuario['senha']}'")
                    usuario_id = inst_cadastro.fetchone()
                    if usuario_id:
                        usuario['id'] = usuario_id[0]
                    else:
                        print("\33[1;31mNão foi possível obter o ID do usuário.\33[m")
                else:
                    print("\33[1;31mOcorreu um erro no cadastro. Tente novamente.\33[m")
            except Exception as e:
                print(f"\33[1;31mOcorreu um erro em seu cadastro: {e}. Tente se cadastrar novamente!\33[m")
            else:
                print(f"\n\33[1;33mBem vindo(a) {usuario['nome']}!\33[m \nEstamos felizes em ter você aqui conosco!")
                salvar_dados_json(dados)  # Salva o JSON atualizado
            break

# Menu principal
def exibir_menu():
    print("\n\33[1;36;46m RESUMO \33[m ")
    time.sleep(0.5)
    print("\n\33[1;33mUltimo regitsro de atividades cadastradas:\33[m")
    ultimo_registro_sono(usuario_id)
    ultimo_registro_atividade(usuario_id)
    time.sleep(0.7)
    print("\n\33[1;33mMetas\33[m")
    visualizar_metas(usuario_id)
    time.sleep(0.7)
    print("\n\33[1;33mExames\33[m")
    visualizar_exames(usuario_id)
    time.sleep(0.7)
    print("\n\33[1;33mPara ter uma vida mais saúdavel, não se esqueça! \33[m")
    print("""<- Se movimente ->
<- Arrume a postura ->
<- Já se hidratou hoje? Não se esqueça ->
<- Não esqueça de marcar exames de rotina ->
    """)
    time.sleep(0.7)
    
    exibir_alertas(usuario_id)

    time.sleep(1)

    while True:
        print("""\n1 - Explorar
2 - Configurações
3 - Artigos
0 - Voltar a tela principal
    """)

        menu = input("\33[1;37mO que deseja fazer :)\33[m")
        if menu == "1":
            explorar_menu()
        elif menu == "2":

            while True:
                print("""
                        1 - Verificar perfil
                        2 - Mostrar dados de saúde 
                        3 - Visualizar estatistica saude
                        4 - Exportar dados (relatorio)
                        0 - Voltar
                    """)
                config = input("Opçaõ:")
                if config == "1":
                    visualizar_perfil()
                elif config == "2":
                    dados_saude()
                elif config == "3":
                    # Chamar função visualizar estatítica
                    print("\33[1;32mEstatistica\33[m")
                    visualizar_estatisticas_saude(usuario_id)
                elif config == "4":
                    exportar_dados_relatorio(usuario_id)
                elif config == "0":
                    print("Voltando...")
                    break
                else:
                    print("\33[1;31mOpção inválida!\33[m")
        elif menu == "3":
            exibir_artigos(usuario_id)
        elif menu == "0":
            return True  # alterei
        else:
            print("\33[1;31mOpção inválida!\33[m")

# Exibir no menu principal
# Resumo de atividades
# ultima atividade fisica
def ultimo_registro_atividade(usuario_id):
    try:
        inst_ultimo_registro = conn.cursor()
        inst_ultimo_registro.execute(
            f"SELECT TIPO_ATIVIDADE, DURACAO, DATA_ATIVIDADE FROM ATIVIDADE_FISICA WHERE ID_USUARIO = {usuario_id} ORDER BY DATA_ATIVIDADE DESC FETCH FIRST 1 ROW ONLY"
        )
        ultimo_registro = inst_ultimo_registro.fetchone()

        if ultimo_registro:
            tipo_atividade, duracao, data_atividade = ultimo_registro
            print(f"\n* Último registro de atividade física ")
            print(f"  - Atividade: {tipo_atividade}")
            print(f"  - Duração: {duracao} minutos")
            print(f"  - Data da atividade: {data_atividade}")
        else:
            print("\n* Nenhum registro de atividade física encontrado. \33[1;33mRegistre suas atividades físicas :) \33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao obter último registro de atividade física: {e}\33[m")


# ultimo registro de sono
def ultimo_registro_sono(usuario_id):
    try:
        inst_ultimo_registro = conn.cursor()
        inst_ultimo_registro.execute(
            f"SELECT DURACAO_SONO, DATA_REGISTRO FROM SONO WHERE ID_USUARIO = {usuario_id} ORDER BY DATA_REGISTRO DESC FETCH FIRST 1 ROW ONLY"
        )
        ultimo_registro = inst_ultimo_registro.fetchone()

        if ultimo_registro:
            duracao_sono, data_registro = ultimo_registro
            print(f"* Último registro de sono ")
            print(f"  - Duração do sono: {duracao_sono} minutos")
            print(f"  - Data do registro: {data_registro}")
        else:
            print(" * Nenhum registro de sono encontrado. \33[1;33mRegistre seu sono :) \33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao obter último registro de sono: {e}\33[m")


# Alertas
# Fazer alertas de acordo com que o usuaro cadastrou seu objetivo dentro do APP
def exibir_alertas(usuario_id):
    print("\33[1;32m\nAlertas\33[m")

    objetivo = consultar_objetivo(usuario_id)
    objetivo = str(objetivo)  # Converte o objetivo para uma string
    if objetivo:
        # Exibe uma mensagem específica com base no objetivo
        if objetivo == '1':
            print("""
\33[1;33mAqui estão cinco alertas importantes para mulheres grávidas:\33[m
1.Cuidado com a alimentação: É importante manter uma dieta saudável e equilibrada durante a gravidez.\n Evite alimentos crus ou mal cozidos, como carnes, ovos e peixes, pois eles podem conter bactérias prejudiciais à saúde.\n\Além disso, evite alimentos processados e açúcar em excesso, pois eles podem aumentar o risco de complicações na gravidez.
                  
2.Mantenha-se hidratada: Beba bastante água e líquidos saudáveis para manter-se hidratada.\n A desidratação pode levar a complicações na gravidez, como parto prematuro e baixo peso ao nascer.
                
3.Evite o estresse: O estresse pode afetar negativamente a saúde da mãe e do bebê.\n Tente relaxar e encontrar maneiras de reduzir o estresse, como meditação, ioga ou exercícios leves.
                
4.Faça exercícios regulares: Exercícios leves e regulares podem ajudar a manter a saúde da mãe e do bebê durante a gravidez.\n Caminhar, nadar e ioga são ótimas opções.
                
5.Mantenha-se informada: Mantenha-se atualizada sobre as últimas informações e recomendações para mulheres grávidas.\n Fale com seu médico regularmente e siga suas orientações para garantir uma gravidez saudável e segura.

                Espero que isso ajude! 😊
""")
        elif objetivo == '2':
           print("""
\33[1;33mAqui estão cinco dicas para melhorar a saúde:\33[m
1. Cuidado com a alimentação: É importante manter uma dieta saudável e equilibrada.\n Evite alimentos processados e açúcar em excesso, pois eles podem aumentar o risco de complicações de saúde.\n Em vez disso, opte por alimentos ricos em nutrientes, como frutas, legumes e grãos integrais.

2. Mantenha-se hidratado: Beba bastante água e líquidos saudáveis para manter-se hidratado.\n A desidratação pode levar a complicações de saúde, como fadiga, dores de cabeça e tonturas.

3. Durma o suficiente: O sono é essencial para a saúde.\n Tente dormir pelo menos 7 horas por noite para ajudar a manter seu corpo e mente saudáveis.

4. Faça exercícios regulares: Exercícios leves e regulares podem ajudar a manter a saúde do corpo e da mente.\n Caminhar, nadar e ioga são ótimas opções.

5. Mantenha-se informado: Mantenha-se atualizado sobre as últimas informações e recomendações para uma vida saudável.\n Fale com seu médico regularmente e siga suas orientações para garantir uma vida saudável e segura.

Espero que isso ajude! 😊
""")

        elif objetivo == '3':
           print("""
\33[1;33mAqui estão cinco formas simples de prevenir doenças transmissíveis:\33[m
1. Mantenha as mãos sempre limpas.
2. Deixe os ambientes arejados.
3. Use preservativo.
4. Vá ao dentista regularmente.
5. Cuide do seu pet.

Espero que isso ajude! 😊
""")
        elif objetivo == '4':
            print("""
\33[1;33mAqui estão cinco dicas para ter hábitos saudáveis:\33[m
1. Cuidado com a alimentação: É importante manter uma dieta saudável e equilibrada.\n Evite alimentos processados e açúcar em excesso, pois eles podem aumentar o risco de complicações de saúde.\n Em vez disso, opte por alimentos ricos em nutrientes, como frutas, legumes e grãos integrais.

2. Mantenha-se hidratado: Beba bastante água e líquidos saudáveis para manter-se hidratado.\n A desidratação pode levar a complicações de saúde, como fadiga, dores de cabeça e tonturas.

3. Durma o suficiente: O sono é essencial para a saúde.\n Tente dormir pelo menos 7 horas por noite para ajudar a manter seu corpo e mente saudáveis.

4. Faça exercícios regulares: Exercícios leves e regulares podem ajudar a manter a saúde do corpo e da mente.\n Caminhar, nadar e ioga são ótimas opções.

5. Mantenha-se informado: Mantenha-se atualizado sobre as últimas informações e recomendações para uma vida saudável.\n Fale com seu médico regularmente e siga suas orientações para garantir uma vida saudável e segura.

Espero que isso ajude! 😊
""")

        else:
            print("Objetivo não reconhecido.")
    else:
        print("\33[1;31mObjetivo não encontrado para este usuário.\33[m")

#Consultando objetivo
def consultar_objetivo(usuario_id):
    try:
        inst_exibir_objetivo = conn.cursor()
        inst_exibir_objetivo.execute(f"SELECT OBJETIVO FROM USUARIO WHERE ID = {usuario_id}")
        objetivo = inst_exibir_objetivo.fetchone()  

        if objetivo:
            return objetivo[0]  # Retorna o valor do objetivo
        else:
            print(f"\33[1;31mObjetivo não encontrado para o usuário com ID {usuario_id}.\33[m")
            return None

    except Exception as e:
        print(f"\33[1;31mErro ao consultar o objetivo: {e}\33[m")
        return None

# Artigos
def exibir_artigos(usuario_id):
    print("\33[1;32m\nArtigos\33[m")

    objetivo = consultar_objetivo(usuario_id)
    objetivo = str(objetivo)  # Converte o objetivo para uma string
    if objetivo:
        # Exibe uma mensagem específica com base no objetivo
        if objetivo == '1':
            print("Você está grávida! Confira nossos artigos sobre cuidados durante a gestação e alimentação saudável para grávidas.")
        elif objetivo == '2':
            print("Quer melhorar sua saúde? Descubra como hábitos simples e a prática regular de exercícios podem ajudar.")
        elif objetivo == '3':
            print("Prevenir doenças transmissíveis é essencial. Conheça mais sobre o uso de preservativos e faça exames regulares para DSTs.")
        elif objetivo == '4':
            print("Manter hábitos saudáveis é fundamental. Leia nossos artigos sobre dicas para hábitos saudáveis e a importância do sono na saúde.")
        else:
            print("Objetivo não reconhecido.")

        artigos = consultar_artigos_no_banco(objetivo)
        if artigos:
            for artigo in artigos:
                print(f"\n\33[1;33m- {artigo['titulo']}\33[m")
                print(f"  {artigo['conteudo']}")
        else:
            print("\33[1;31mNenhum artigo encontrado para este objetivo.\33[m")
    else:
        print("\33[1;31mObjetivo não encontrado para este usuário.\33[m")



def consultar_artigos_no_banco(objetivo):
    time.sleep(0.5)
    artigos_por_objetivo = {
        '1': [
            {'titulo': '\33[1;33mCuidados durante a gestação\33[m', 'conteudo':'Saber sobre os cuidados na gravidez é importante para garantir uma gestação saudável tanto para a mãe quanto para o bebê.\nOs exames de acompanhamento obstétrico, incluindo as triagens genéticas, permitem a detecção precoce de problemas de saúde na gestante e no bebe,\nsendo possível tratá-los ou minimizar riscos e complicações.\nEntre no site para mais informações:https://salomaozoppi.com.br/saude/cuidados-na-gravidez '},
            {'titulo': '\33[1;33mAlimentação saudável para grávidas\33[m', 'conteudo': 'A gestação é uma fase especial na vida de muitas mulheres e que exige cuidados específicos com a saúde da mamãe e do bebê.\nÉ importante que as gestantes realizem todos os exames médicos necessários e cuidem do próprio bem-estar. Na alimentação está uma das chaves para o desenvolvimento saudável da criança.\nA insegurança em relação aos hábitos alimentares e possíveis restrições ou dietas é algo comum entre as futuras mamães. Assim sendo, nós separamos 7 dicas importantes sobre alimentação saudável para gestantes que você precisa conhecer.\nEntre no site para mais informações:https://ayrozaribeiro.com.br/materias/alimentacao-saudavel-para-gestantes/'},
        ],
        '2': [
            {'titulo': '\33[1;33mComo melhorar a saúde com hábitos simples\33[m', 'conteudo':'Manter a saúde em dia é essencial para garantir disposição, bem-estar e qualidade de vida.\nAlgumas medidas simples, como ter uma dieta balanceada e praticar atividades físicas, podem ter impacto positivo.\nConfira sete hábitos fundamentais para ter mais saúde!\nEntre no site para mais informações:https://www.minhavida.com.br/materias/materia-23364'},
            {'titulo': '\33[1;33mImportância da atividade física para a saúde\33[m', 'conteudo': ' A atividade física produz substâncias capazes de reduzir a pressão arterial por até 24h,\n diminuindo o risco de complicações e agravamento de doenças cardiovasculares,\ncomo acidente vascular encefálico, infarto e doença arterial \nobstrutiva periférica.\nEntre no site para mais informações:https://www.tjdft.jus.br/informacoes/programas-projetos-e-acoes/pro-vida/dicas-de-saude/pilulas-de-saude/importancia-da-atividade-fisica-para-a-saude#:~:text=%E2%80%8B%20A%20atividade%20f%C3%ADsica%20produz,e%20doen%C3%A7a%20arterial%20obstrutiva%20perif%C3%A9rica.'},
        ],
        '3': [
            {'titulo': '\33[1;33mPrevenção de doenças transmissíveis\33[m', 'conteudo':'A doença sexualmente transmissível (DST) é uma doença que é passada de uma pessoa para outra pessoa ao ter relações sexuais.\nAs DSTs afetam milhões de pessoas em todo o mundo.\nNenhum grupo está imune. Você pode estar infectado, independentemente do seu sexo, raça, situação econômica ou idade.\n Doenças sexualmente transmissíveis podem ter efeitos graves e permanentes na sua saúde.\n Ter uma doença sexualmente transmissível aumenta o risco de contrair o vírus da imunodeficiência humana, ou HIV, o que pode levar à síndrome da imunodeficiência adquirida (SIDA/AIDS).\nEntre no site para mais informações:https://portaldacoloproctologia.com.br/sua-saude/prevencao-das-doencas-sexualmente-transmissiveis-dsts/'},
            {'titulo': '\33[1;33mUso de preservativos e saúde sexual\33[m', 'conteudo':'“Sabemos que a camisinha é um eficaz contraceptivo para evitar gravidez, mas atualmente ainda é o único método capaz de evitar diversas infecções sexualmente transmissíveis,\ncomo sífilis, gonorreia, clamídia, HPV e herpes”, destacou a médica infectologista Naiara Melo\nEntre no site para mais informações: https://portal.rr.gov.br/noticias/item/7433-especialistas-de-saude-ressaltam-importancia-do-uso-de-preservativo-nas-relacoes-sexuais#:~:text=%E2%80%9CSabemos%20que%20a%20camisinha%20%C3%A9,a%20m%C3%A9dica%20infectologista%20Naiara%20Melo.'},
        ],
        '4': [
            {'titulo': '\33[1;33mDicas para manter hábitos saudáveis\33[m', 'conteudo':'Muito se houve falar sobre a importância dos hábitos saudáveis para mais longevidade e bem-estar.\nProfissionais de várias áreas da saúde recomendam a adoção de uma rotina saudável como elemento decisivo ao tratar doenças como diabetes,\n hipertensão, depressão e ansiedade\nA Unimed-BH é uma grande incentivadora da mudança de hábitos e sabemos que dar o primeiro passo pode ser um grande desafio.\n A boa notícia é que vale muito a pena e neste artigo, vamos revelar alguns segredos que podem facilitar o processo.\nEntre no site para mais informações:https://viverbem.unimedbh.com.br/para-participar/movimento-mude-1-habito/habitos-saudaveis/'},
            {'titulo': '\33[1;33mImportância do sono na saúde\33[m', 'conteudo':'É durante o sono que o organismo exerce as principais funções restauradoras do corpo, como o reparo dos tecidos,\no crescimento muscular e a síntese de proteínas. Durante este momento, é possível repor energias e regular o metabolismo,\nfatores essenciais para manter corpo e mente saudáveis. Dormir bem é um hábito que deve ser incluído na rotina de todos.\nEntre no site para mais informações: https://copass-saude.com.br/posts/dormir-bem-a-importancia-de-uma-boa-noite-de-sono#:~:text=%C3%89%20durante%20o%20sono%20que,manter%20corpo%20e%20mente%20saud%C3%A1veis.'},
        ],
    }

    return artigos_por_objetivo.get(objetivo, [])


#Configurações
# Visualizar perfil dando a possibilidade de fazer alteração
def visualizar_perfil():
    dados = carregar_dados_json()
    usuario = dados['usuario']

    if usuario:
        while True:
            print("\nAqui estão seus dados:")
            for campo, valor in usuario.items():
                print(f"\33[1;33m{campo}.........: {valor}\33[m")

            print("""
                1 - Fazer alteração
                2 - Excluir perfil
                0 - Voltar
            """)
            opcao = input("O que deseja fazer: ")

            if opcao == "1":
                while True:
                    campos = input("\nO que deseja editar (exemplo: nome): ")
                    if campos in usuario:
                        novo_valor = input(f"Digite um novo valor para '{campos}': ")
                        print("\33[1;33mAtualizado com sucesso!\33[m")
                        usuario[campos] = novo_valor

                        # Atualiza os dados no banco de dados
                        inst_visualizar_perfil = conn.cursor()
                        inst_visualizar_perfil.execute(
                            f"UPDATE USUARIO SET {campos} = '{novo_valor}' WHERE id = {usuario['id']}")
                        conn.commit()
                        salvar_dados_json(dados)
                        break
                    else:
                        print("\33[1;31mOps, parece que esse campo não existe! Por favor, tente novamente.\33[m")
            elif opcao == "2":
                if excluir_perfil(usuario['id']):
                    print("\33[1;33mRetornando para a tela de login...\33[m")
                    return
            elif opcao == "0":
                break
            else:
                print("\33[1;31mOpção inválida!\33[m")
    else:
        print("\33[1;31mUsuário não encontrado. Por favor, faça o login.\33[m")
        
def excluir_perfil(usuario_id):
    confirmacao = input("\nTem certeza de que deseja excluir seu perfil? (Digite 'sim' para confirmar): ")
    if confirmacao.lower() == 'sim':
        try:
            inst_excluir_perfil = conn.cursor()

            # Excluir dados relacionados ao usuário (ajuste conforme a estrutura real do seu banco)
            inst_excluir_perfil.execute(f"DELETE FROM ATIVIDADE_FISICA WHERE ID_USUARIO = {usuario_id}")
            inst_excluir_perfil.execute(f"DELETE FROM ALIMENTACAO WHERE ID_USUARIO = {usuario_id}")
            inst_excluir_perfil.execute(f"DELETE FROM META WHERE ID_USUARIO  = {usuario_id}")
            inst_excluir_perfil.execute(f"DELETE FROM EXAME WHERE ID_USUARIO = {usuario_id}")
            inst_excluir_perfil.execute(f"DELETE FROM SONO WHERE ID_USUARIO = {usuario_id}")
            inst_excluir_perfil.execute(f"DELETE FROM USUARIO WHERE ID = {usuario_id}")
            conn.commit()

            print("\33[1;33mPerfil excluído com sucesso!\33[m")
            print("\33[1;32mSaindo de Saúde 360°.\33[m")
            sys.exit()
            return True
        except Exception as e:
            print(f"\33[1;31mErro ao excluir o perfil: {e}\33[m")
            return False
    else:
        print("\33[1;33mOperação de exclusão cancelada.\33[m")
        return False


# Registro de atividades
# Usuário todos os dados que ele registrou
def dados_saude():
    visualizar_alimentacao(usuario_id)
    visualizar_atividade(usuario_id)
    visualizar_exames(usuario_id)
    visualizar_metas(usuario_id)


# Visualizar estatistica
def visualizar_estatisticas_saude(usuario_id):
    # Obter dados do sono, alimentação e atividade física
    dados_sono = obter_dados_sono(usuario_id)
    dados_atividade = obter_dados_atividade(usuario_id)

    # Calcular estatísticas
    media_duracao_sono = calcular_media_duracao_sono(dados_sono)
    total_horas_atividade = calcular_total_horas_atividade(dados_atividade)

    # Exibir estatísticas
    print(f"\n\33[1;33mAqui estão suas estátistica:\33[m\n")
    print(f"Média de duração do sono: {media_duracao_sono} minutos")
    print(f"Total de horas de atividade física: {total_horas_atividade} horas")
    print("\n\33[1;33mEstatísticas de saúde visualizadas com sucesso!\33[m")


# Função para obter dados de sono
def obter_dados_sono(usuario_id):
    inst_obter_dados_sono = conn.cursor()
    inst_obter_dados_sono.execute(f"SELECT META_SONO, DURACAO_SONO, DATA_REGISTRO FROM SONO WHERE ID_USUARIO = {usuario_id}")
    dados_sono = inst_obter_dados_sono.fetchall()
    return dados_sono


# Função para obter dados de atividade física
def obter_dados_atividade(usuario_id):
    inst_obter_dados_atividade = conn.cursor()
    inst_obter_dados_atividade.execute(f"SELECT TIPO_ATIVIDADE, DURACAO, DATA_ATIVIDADE FROM ATIVIDADE_FISICA WHERE ID_USUARIO = {usuario_id}")
    dados_atividade = inst_obter_dados_atividade.fetchall()
    return dados_atividade

# Função para calcular média de duração do sono
def calcular_media_duracao_sono(dados_sono):
    if not dados_sono:
        return 0  # ou outra lógica, dependendo do seu caso
    duracoes = [sono[1] for sono in dados_sono if sono[1] is not None]
    if not duracoes:
        return 0  # ou outra lógica, se não houver durações válidas
    media_duracao = sum(duracoes) / len(duracoes)
    return round(media_duracao, 2)  # arredonda para duas casas decimais, ajuste conforme necessário


# Função para calcular total de horas de atividade física
def calcular_total_horas_atividade(dados_atividade):
    if not dados_atividade:
        return 0
    total_minutos = sum([int(atividade[1]) for atividade in dados_atividade if atividade[1] is not None])
    total_horas = total_minutos / 60
    return round(total_horas, 2)  # arredonda para duas casas decimais, ajuste conforme necessário



# Buscar no banco
def buscar_usuario(usuario_id):
    cursor = conn.cursor()
    consulta = f"SELECT ID, NOME, CPF, IDADE, SEXO, EMAIL, OBJETIVO FROM usuario WHERE ID = {usuario_id}"
    cursor.execute(consulta)
    usuario = cursor.fetchone()

    # Transforma o resultado em um dicionário
    if usuario:
        keys = ["ID", "NOME", "CPF", "IDADE", "SEXO", "EMAIL", "OBJETIVO"]
        return dict(zip(keys, usuario))
    
    
def buscar_atividade(usuario_id):
    cursor = conn.cursor()
    consulta = f"SELECT ID_ATIVIDADE, TIPO_ATIVIDADE, DURACAO, DATA_ATIVIDADE FROM atividade_fisica WHERE ID_USUARIO = {usuario_id}"
    cursor.execute(consulta)
    atividades = cursor.fetchall()

    # Transforma o resultado em uma lista de dicionários
    if atividades:
        keys = ["ID_ATIVIDADE", "TIPO_ATIVIDADE", "DURACAO", "DATA_ATIVIDADE"]
        return [dict(zip(keys, atividade)) for atividade in atividades]

def buscar_alimentacao(usuario_id):
    cursor = conn.cursor()
    consulta = f"SELECT ID_ALIMENTACAO, TIPO_REFEICAO, ALIMENTOS_CONSUMIDOS, DATA_ALIMENTACAO FROM ALIMENTACAO WHERE ID_USUARIO = {usuario_id}"
    cursor.execute(consulta)
    alimentacoes = cursor.fetchall()

    # Transforma o resultado em uma lista de dicionários
    if alimentacoes:
        keys = ["ID_ALIMENTACAO", "TIPO_REFICAO", "ALIMENTOS_CONSUMIDOS", "DATA_ALIMENTACAO"]
        return [dict(zip(keys, alimentacao)) for alimentacao in alimentacoes]


def buscar_sono(usuario_id):
    cursor = conn.cursor()
    consulta = f"SELECT ID_SONO, META_SONO, DURACAO_SONO, DATA_REGISTRO FROM SONO WHERE ID_USUARIO = {usuario_id}"
    cursor.execute(consulta)
    sonos = cursor.fetchall()

    # Transforma o resultado em uma lista de dicionários
    if sonos:
        keys = ["ID_SONO", "META_SONO", "DURACAO_SONO", "DATA_REGISTRO"]
        return [dict(zip(keys, sono)) for sono in sonos]

def buscar_meta(usuario_id):
    cursor = conn.cursor()
    consulta = f"SELECT ID_META, MENSSAGEM FROM META WHERE ID_USUARIO = {usuario_id}"
    cursor.execute(consulta)
    metas = cursor.fetchall()

    # Transforma o resultado em uma lista de dicionários
    if metas:
        keys = ["ID_META", "MENSSAGEM"]
        return [dict(zip(keys, meta)) for meta in metas]

def buscar_exame(usuario_id):
    cursor = conn.cursor()
    consulta = f"SELECT ID_EXAME, NOME_EXAME, DATA_EXAME, HORARIO_EXAME FROM EXAME WHERE ID_USUARIO = {usuario_id}"
    cursor.execute(consulta)
    exames = cursor.fetchall()

    # Transforma o resultado em uma lista de dicionários
    if exames:
        keys = ["ID_EXAME", "NOME_EXAME", "DATA_EXAME", "HORARIO_EXAME"]
        return [dict(zip(keys, exame)) for exame in exames]

# Relatorios
def relatorio_usuario(usuario_id):
    return buscar_usuario(usuario_id)

def relatorio_atividade(usuario_id):
    return buscar_atividade(usuario_id)

def relatorio_alimentacao(usuario_id):
    return buscar_alimentacao(usuario_id)

def relatorio_sono(usuario_id):
    return buscar_sono(usuario_id)

def relatorio_meta(usuario_id):
    return buscar_meta(usuario_id)

def relatorio_exame(usuario_id):
    return buscar_exame(usuario_id)

def converter_para_json(dado):
    if isinstance(dado, datetime.datetime):
        return dado.__str__()
    
# Exportar relatório
def exportar_dados_relatorio(usuario_id):
    info_usuario = relatorio_usuario(usuario_id)
    info_atividades = relatorio_atividade(usuario_id)
    info_alimentacao = relatorio_alimentacao(usuario_id)
    info_sono = relatorio_sono(usuario_id)
    info_meta = relatorio_meta(usuario_id)
    info_exame = relatorio_exame(usuario_id)

    relatorio = {}

    if info_usuario:
        relatorio["usuario"] = info_usuario
    else:
        relatorio["mensagem_usuario"] = "Nenhum usuário encontrado."

    if info_atividades:
        relatorio["atividades"] = info_atividades
    else:
        relatorio["mensagem_atividade"] = "Nenhuma atividade encontrada."

    if info_alimentacao:
        relatorio["alimentacoes"] = info_alimentacao
    else:
        relatorio["mensagem_alimentacao"] = "Nenhuma alimentacao encontrada."
    
    if info_sono:
        relatorio["sonos"] = info_sono
    else:
        relatorio["mensagem_sono"] = "Nenhum sono encontrado."
    
    if info_meta:
        relatorio["metas"] = info_meta
    else:
        relatorio["mensagem_meta"] = "Nenhuma meta encontrada."
    
    if info_exame:
        relatorio["exames"] = info_exame
    else:
        relatorio["mensagem_exame"] = "Nenhum exame encontrado."

    with open("relatorio.json", "w") as arquivo:
        json.dump(relatorio, arquivo, indent=2, default=converter_para_json)
    print('\33[1;33mDados do Relatorio exportados com sucesso!\33[m')


# EXPLORAR
def explorar_menu():
    while True:
        print("""
             1. 🍏 Nutrição
             2. 💤 Sono
             3. 🏋️‍♀️ Atividade Física
             4. 🎯 Metas pessoais
             5. 🩺 Exames
             0. Voltar
        """)
        escolha_str = input("\33[1;37mEscolha uma opção: \33[m").strip()

        if escolha_str == '':
            print("\33[1;31mOpção inválida. Tente novamente.\33[m")
            continue

        try:
            escolha = int(escolha_str)
        except ValueError:
            print("\33[1;31mOpção inválida. Tente novamente.\33[m")
            continue

        if escolha == 1:
            registrar_aliementacao_menu(usuario_id)
        elif escolha == 2:
            registrar_sono(usuario_id)
        elif escolha == 3:
            registrar_atividade(usuario_id)
        elif escolha == 4:
            metas_pessoais(usuario_id)
        elif escolha == 5:
            registrar_exames(usuario_id)
        elif escolha == 0:
            print("Voltando...")
            break
        else:
            print("\33[1;31mOpção inválida. Tente novamente.\33[m")


#Sono
#Registrar sono e meta
def registrar_sono(usuario_id):
    while True:
        print("""
            1 - Registrar meta de sono
            2 - Registrar sono
            0 - Voltar
        """)
        escolha = input("\33[1;37mEscolha uma opção: \33[m")

        if escolha == "1":
            # Verificar se já existe uma meta de sono para o usuário
            inst_verificar_meta = conn.cursor()
            inst_verificar_meta.execute(f"SELECT META_SONO FROM (SELECT META_SONO, DATA_REGISTRO FROM SONO WHERE ID_USUARIO = {usuario_id} AND META_SONO IS NOT NULL ORDER BY DATA_REGISTRO DESC) WHERE ROWNUM <= 1")
            meta_existente = inst_verificar_meta.fetchone()

            if meta_existente is None:
                while True:
                    meta_sono = input("Digite a quantidade de horas desejada para dormir: ")
                    if meta_sono.strip() and meta_sono.isdigit():
                        try:
                            # Obtém a data e hora atual
                            data_registro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            # Insere os dados da meta de sono no banco de dados
                            registrar_meta_sono(usuario_id, meta_sono, data_registro)

                            print("\n\33[1;33mMeta de sono registrada!\33[m")
                            break
                        except Exception as e:
                            print(f"\33[1;31mErro ao registrar meta de sono: {e}\33[m")
                    else:
                        print("\33[1;31mPor favor, insira um valor válido para a meta de sono.\33[m")
            else:
                while True:
                    atualizar_meta = input(f"\33[1;33mVocê já possui uma meta de sono de {meta_existente[0]} horas.\33[m Deseja atualizar para uma nova meta? (S/N): ").upper()
                    if atualizar_meta == "S":
                        while True:
                            meta_sono = input("Digite a nova quantidade de horas desejada para dormir: ")
                            if meta_sono.strip() and meta_sono.isdigit():
                                try:
                                    # Obtém a data e hora atual
                                    data_registro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                    # Atualiza a meta de sono no banco de dados
                                    registrar_meta_sono(usuario_id, meta_sono, data_registro)

                                    print("\n\33[1;33mMeta de sono atualizada!\33[m")
                                    break
                                except Exception as e:
                                    print(f"\33[1;31mErro ao atualizar meta de sono: {e}\33[m")
                            else:
                                print("\33[1;31mPor favor, insira um valor válido para a meta de sono.\33[m")
                        break
                    elif atualizar_meta == "N":
                        print("\33[1;33mMeta de sono mantida.\33[m")
                        break
                    else:
                        print("\33[1;31mOpção inválida!\33[m")

        elif escolha == "2":
            while True:
                duracao_sono = input("Digite a duração do sono em minutos: ")
                if duracao_sono.strip() and duracao_sono.isdigit():
                    try:
                        # Obtém a data e hora atual
                        data_registro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Insere os dados do sono no banco de dados
                        registrar_registro_sono(usuario_id, duracao_sono, data_registro)

                        print("\n\33[1;33mSono registrado!\33[m")
                        break
                    except Exception as e:
                        print(f"\33[1;31mErro ao registrar sono: {e}\33[m")
                else:
                    print("\33[1;31mPor favor, insira um valor válido para a duração do sono.\33[m")

        elif escolha == "0":
            break
        else:
            print("\33[1;31mOpção inválida. Tente novamente.\33[m")

def registrar_meta_sono(usuario_id, meta_sono, data_registro):
    try:
        inst_registro_meta_sono = conn.cursor()
        inst_registro_meta_sono.execute(
            f"INSERT INTO SONO (ID_USUARIO, META_SONO, DATA_REGISTRO) VALUES ({usuario_id}, {meta_sono}, TO_DATE('{data_registro}', 'YYYY-MM-DD HH24:MI:SS'))"
        )
        conn.commit()
    except Exception as e:
        print(f"\33[1;31mErro ao inserir meta de sono no banco de dados: {e}\33[m")


def registrar_registro_sono(usuario_id, duracao, data_registro):
    try:
        inst_registro_sono = conn.cursor()
        inst_registro_sono.execute(
            f"INSERT INTO SONO (ID_USUARIO, DURACAO_SONO, DATA_REGISTRO) VALUES ({usuario_id}, {duracao}, TO_DATE('{data_registro}', 'YYYY-MM-DD HH24:MI:SS'))"
        )
        conn.commit()
    except Exception as e:
        print(f"\33[1;31mErro ao inserir sono no banco de dados: {e}\33[m")


# Nutrição
# Registrar alimentação e meta (dieta)
def registrar_nutricao():
    while True:
        print("""
            1 - Registrar alimentação
            2 - Dietas personalizadas
            0 - Voltar
        """)
        opcao = input("\33[1;37mEscolha uma das opções:\33[m")
        if opcao == "1":
            registrar_alimentacao(usuario_id)
        elif opcao == "2":
            exibir_sugestoes_dietas()
        elif opcao == "0":
            break
        else:
            print("\33[1;31mOpção inválida!\33[m")

#Alimentação
# Usuario registra alimentação e alimentos consumidos
# Visualizar
# Excluir
def registrar_aliementacao_menu(usuario_id):
    while True:
        print("""
            1 - Registrar alimentação
            2 - Visualizar alimentação
            3 - Excluir alimentacão
            4 - Dietas personalizadas
            0 - Voltar
        """)
        opcao_alimentacao = input("\33[1;37mEscolha uma opção:\33[m")

        if opcao_alimentacao == '1':
            registrar_alimentacao(usuario_id)
        elif opcao_alimentacao== '2':
           visualizar_alimentacao(usuario_id)
        elif opcao_alimentacao== '3':
            excluir_alimentacao(usuario_id)
        elif opcao_alimentacao == '4':
            exibir_sugestoes_dietas()
        elif opcao_alimentacao == '0':
            break
        else:
            print("\33[1;31mOpção inválida.\33[m")

def registrar_alimentacao(usuario_id):
    print("\33[1;33mVamos registrar sua refeição :)\33[m")
    print("""
    1 - Café da manhã
    2 - Lancha da manhã
    3 - Almoço
    4 - Lanche da tarde
    5 - Jantar
    6 - Lanche da noite
    """)
    while True:
        tipo_refeicao = input("\33[1;37mDigite o número da refeição:  \33[m")
        if tipo_refeicao not in {"1", "2", "3", "4", "5", "6"}:
            print("\33[1;31mOpção inválida.\33[m")
        else:
            break

    while True:
        alimentos_consumidos = input("\33[1;37mDigite os alimentos consumidos:\33[m ")
        if not alimentos_consumidos:
            print("\33[1;31mAlimentos não encontrados. Registre seus alimentos!\33[m")
        else:
            break

    try:
        # Obtém a data e hora atual
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Insere os dados da alimentação no banco de dados
        inserir_alimentacao(usuario_id, tipo_refeicao, alimentos_consumidos, data_atual)

        print("\n\33[1;33mAlimentação registrada com sucesso!\33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao registrar a alimentação: {e}\33[m")

def inserir_alimentacao(usuario_id, tipo_refeicao, alimentos_consumidos, data_alimentacao):
    try:
        inst_inserir_alimentacao = conn.cursor()
        inst_inserir_alimentacao.execute(
            f"INSERT INTO ALIMENTACAO (ID_USUARIO, TIPO_REFEICAO, ALIMENTOS_CONSUMIDOS, DATA_ALIMENTACAO) VALUES ({usuario_id}, '{tipo_refeicao}', '{alimentos_consumidos}', TO_DATE('{data_alimentacao}', 'YYYY-MM-DD HH24:MI:SS'))"
        )
        conn.commit()
    except Exception as e:
        print(f"\33[1;31mErro ao inserir a alimentação no banco de dados: {e}\33[m")

def visualizar_alimentacao(usuario_id):
    try:
        inst_recuperar_alimentacao = conn.cursor()
        inst_recuperar_alimentacao.execute(
            f"SELECT TIPO_REFEICAO, ALIMENTOS_CONSUMIDOS, DATA_ALIMENTACAO FROM ALIMENTACAO WHERE ID_USUARIO = {usuario_id}"
        )
        alimentacoes = inst_recuperar_alimentacao.fetchall()

        if alimentacoes:
            print("\nAlimentações registradas:")
            for alimentacao in alimentacoes:
                tipo_refeicao, alimentos_consumidos, data_alimentacao = alimentacao
                print(f"- Refeição: {tipo_refeicao}, Alimentos Consumidos: {alimentos_consumidos}, Data: {data_alimentacao}")
        else:
            print("\nNenhuma alimentação encontrada.\33[1;33mRegistre suas alimentações\33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao recuperar alimentações: {e}\33[m")

def excluir_alimentacao(usuario_id):
    try:
        # Exibir as alimentacoes do usuário
        inst_exibir_alimentacoes = conn.cursor()
        inst_exibir_alimentacoes.execute(
            f"SELECT ID_ALIMENTACAO, TIPO_REFEICAO, ALIMENTOS_CONSUMIDOS, DATA_ALIMENTACAO FROM ALIMENTACAO WHERE ID_USUARIO = {usuario_id}"
        )
        alimentacoes = inst_exibir_alimentacoes.fetchall()

        if not alimentacoes:
            print("\nNenhuma alimentação encontrada.\33[1;33mRegistre suas alimentações\33[m")
            return

        print("Alimentações disponíveis para exclusão:")
        for alimentacao in alimentacoes:
            id_alimentacao, tipo_refeicao, alimentos_consumidos, data_alimentacao = alimentacao
            print(f" ID: {id_alimentacao} - Refeição: {tipo_refeicao}, Alimentos Consumidos: {alimentos_consumidos}, Data: {data_alimentacao}")

        alimentacao_a_excluir_id = input("\nDigite o ID da alimentação que deseja excluir (ou '0' para cancelar): ")

        if alimentacao_a_excluir_id == '0':
            print("\33[1;33mOperação de exclusão cancelada.\33[m")
            return

        # Verificar se o ID da alimentacao pertence ao usuário
        alimentacao_encontrada = False
        for alimentacao in alimentacoes:
            id_alimentacao, _, _, _ = alimentacao
            if str(id_alimentacao) == alimentacao_a_excluir_id:
                alimentacao_encontrada = True
                break

        if not alimentacao_encontrada:
            print("\33[1;31mID de alimentação inválido.\33[m")
            return

        # Excluir a alimentacao do banco de dados
        inst_excluir_alimentacao = conn.cursor()
        inst_excluir_alimentacao.execute(
            f"DELETE FROM ALIMENTACAO WHERE ID_USUARIO = {usuario_id} AND ID_ALIMENTACAO = {alimentacao_a_excluir_id}"
        )
        conn.commit()

        print("\33[1;33mAlimentação excluída com sucesso!\33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao excluir a alimentação: {e}\33[m")


#Dieta
def exibir_sugestoes_dietas():
    print("""
        \33[1;33mEscolha o seu objetivo :)\33[m
        1 - Definição Muscular
        2 - Ganho de Massa Magra
        3 - Emagrecimento
        4 - Dieta Low-Carb
        5 - Dieta Vegetariana/Vegana
        6 - Dieta Cetogênica
        7 - Controle da Diabetes
    """)

    while True:
        objetivo = input("\33[1;37mDigite o número correspondente ao seu objetivo:\33[m")

        if objetivo not in ["1", "2", "3", "4", "5", "6", "7"]:
            print("\33[1;31mOpção inválida!\33[m")
        else:
            exibir_sugestao_dieta(objetivo)
            break

def exibir_sugestao_dieta(objetivo):

    if objetivo == "1":
        print("\n\33[1;33mSugestões para Definição Muscular:\33[m")
        print("""
    Macronutrientes: Consuma uma quantidade adequada de proteínas para manter a massa muscular, moderada quantidade de carboidratos e uma quantidade mínima de gorduras.
    Exemplo de Alimentos: Peito de frango, peixe, ovos, vegetais, arroz integral.
        """)
    elif objetivo == "2":
        print("\n\33[1;33mSugestões para Ganho de Massa Magra:\33[m")
        print("""
    Macronutrientes: Aumente a ingestão de proteínas e carboidratos para fornecer energia para os treinos e suportar o crescimento muscular.
    Exemplo de Alimentos: Carne magra, batata-doce, quinoa, legumes.
        """)
    elif objetivo == "3":
        print("\n\33[1;33mSugestões para Emagrecimento:\33[m")
        print("""
    Macronutrientes: Mantenha um déficit calórico com uma ênfase em proteínas para preservar a massa muscular.
    Exemplo de Alimentos: Peito de frango, peixe, vegetais folhosos, aveia.
        """)
    elif objetivo == "4":
        print("\n\33[1;33mSugestões para Dieta Low-Carb:\33[m")
        print("""
    Macronutrientes: Reduza a ingestão de carboidratos, aumentando a ingestão de gorduras saudáveis e mantendo uma quantidade adequada de proteínas.
    Exemplo de Alimentos: Abacate, azeite de oliva, carne magra, vegetais com baixo teor de carboidratos.
        """)
    elif objetivo == "5":
        print("\n\33[1;33mSugestões para Dieta Vegetariana/Vegana:\33[m")
        print("""
    Macronutrientes: Certifique-se de obter proteínas suficientes de fontes vegetais, incluindo leguminosas, tofu, quinoa, e diversifique a ingestão de vegetais para garantir nutrientes adequados.
    Exemplo de Alimentos: Feijão, lentilhas, tofu, vegetais variados
       """)
    elif objetivo == "6":
        print("\n\33[1;33mSugestões para Dieta Cetogênica:\33[m")
        print("""
    Macronutrientes: Alta ingestão de gorduras, moderada em proteínas, e muito baixa em carboidratos.
    Exemplo de Alimentos: Carne, peixe, ovos, abacate, azeite de oliva.
        """)
    elif objetivo == "7":
        print("\n\33[1;33mSugestões para Controle da Diabetes:\33[m")
        print("""
    Macronutrientes: Controle rigoroso de carboidratos, ênfase em fibras, escolha de carboidratos complexos.
    Exemplo de Alimentos: Grãos integrais, vegetais, proteínas magras.
        """)

# Atividade física
# Registrar atividade e a duração
#Visualizar
#Excluir
def registrar_atividade(usuario_id):
    while True:
        print("""
            1 - Registrar atividade
            2 - Visualizar atividade
            3 - Excluir atividades
            0 - Voltar
        """)
        opcao_atividade = input("\33[1;37mEscolha uma opção:\33[m")

        if opcao_atividade == '1':
            registrar_atividade_fisica(usuario_id)
        elif opcao_atividade== '2':
           visualizar_atividade(usuario_id)
        elif opcao_atividade== '3':
            excluir_atividade(usuario_id)
        elif opcao_atividade == '0':
            break
        else:
            print("\33[1;31mOpção inválida.\33[m")


def registrar_atividade_fisica(usuario_id):
    print("\33[1;33mEba! Vamos registrar uma atividade física :)\33[m")
    print("""
    \n*Esportes praticados a pé*
    1 - Corrida
    2 - Caminhada
    3 - Trilha
    \n*Esportes de ciclismo*
    4 - Pedalada
    5 - Bicileta Elétrica
    \n*Esportes aquáticos*
    6 - Canoa 
    7 - Caiaque
    8 - Remo
    9 - Surfe
    10 - Natação
    \n*Caso não tenha o esporte*
    0 - Outros
    """)
    while True:
        tipo_atividade = input("\33[1;37mDigite o número da atividade realizada:\33[m")
        if tipo_atividade == "0":
            outro = input("\33[1;37mQual o nome da atividade realizada: \33[m")
            break
        elif tipo_atividade not in {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}:
            print("\33[1;31mOpção inválida.\33[m")
        else:
            break

    while True:
        duracao = input("\33[1;37mDigite a duração da atividade (em minutos, ex: 120 = 2 horas): \33[m")
        if not duracao.isdigit():
            print("\33[1;31mDuração inválida\33[m")
        else:
            break
    try:
        # Obtém a data e hora atual
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insere os dados da atividade física no banco de dados
        inserir_atividade_fisica(usuario_id, tipo_atividade, duracao, data_atual)

    except Exception as e:
        print(f"\33[1;31mErro ao registrar a atividade física: {e}\33[m")

    print("\n\33[1;33mAtividade física registrada com sucesso!\33[m")

def inserir_atividade_fisica(usuario_id, tipo_atividade, duracao, data_atividade):
    try:
        inst_inserir_atividade = conn.cursor()
        inst_inserir_atividade.execute(
            f"INSERT INTO ATIVIDADE_FISICA (ID_USUARIO, TIPO_ATIVIDADE, DURACAO, DATA_ATIVIDADE) VALUES ({usuario_id}, '{tipo_atividade}', {duracao}, TO_DATE('{data_atividade}', 'YYYY-MM-DD HH24:MI:SS'))"
        )
        conn.commit()
    except Exception as e:
        print(f"\33[1;31mErro ao inserir a atividade física no banco de dados: {e}\33[m")

def visualizar_atividade(usuario_id):
    try:
        inst_recuperar_atividades = conn.cursor()
        inst_recuperar_atividades.execute(
            f"SELECT TIPO_ATIVIDADE, DURACAO, DATA_ATIVIDADE FROM ATIVIDADE_FISICA WHERE ID_USUARIO = {usuario_id}"
        )
        atividades = inst_recuperar_atividades.fetchall()

        if atividades:
            print("\nAtividades:")
            for atividade in atividades:
                tipo_atividade, duracao, data_atividade = atividade
                print(f"- Tipo: {tipo_atividade}, Duração: {duracao} minutos, Data: {data_atividade}")
        else:
            print("\nNenhuma atividade encontrada.\33[1;33mRegistre suas atividades :)\33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao recuperar atividades: {e}\33[m")

def excluir_atividade(usuario_id):
    try:
        # Exibir as atividades do usuário
        inst_exibir_atividades = conn.cursor()
        inst_exibir_atividades.execute(
            f"SELECT ID_ATIVIDADE, TIPO_ATIVIDADE, DURACAO, DATA_ATIVIDADE FROM ATIVIDADE_FISICA WHERE ID_USUARIO = {usuario_id}"
        )
        atividades = inst_exibir_atividades.fetchall()

        if not atividades:
            print("\nNenhuma atividade encontrada.\33[1;33mRegistre suas atividades :)\33[m")
            return

        print("Atividades disponíveis para exclusão:")
        for atividade in atividades:
            id_atividade, tipo_atividade, duracao, data_atividade = atividade
            print(f" ID: {id_atividade} - Tipo: {tipo_atividade}, Duração: {duracao} minutos, Data: {data_atividade}")

        atividade_a_excluir_id = input("\nDigite o ID da atividade que deseja excluir (ou '0' para cancelar): ")

        if atividade_a_excluir_id == '0':
            print("\33[1;33mOperação de exclusão cancelada.\33[m")
            return

        # Verificar se o ID da atividade pertence ao usuário
        atividade_encontrada = False
        for atividade in atividades:
            id_atividade, _, _, _ = atividade
            if str(id_atividade) == atividade_a_excluir_id:
                atividade_encontrada = True
                break

        if not atividade_encontrada:
            print("\33[1;31mID de atividade inválido.\33[m")
            return

        # Excluir a atividade do banco de dados
        inst_excluir_atividade = conn.cursor()
        inst_excluir_atividade.execute(
            f"DELETE FROM ATIVIDADE_FISICA WHERE ID_USUARIO = {usuario_id} AND ID_ATIVIDADE = {atividade_a_excluir_id}"
        )
        conn.commit()

        print("\33[1;33mAtividade excluída com sucesso!\33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao excluir a atividade: {e}\33[m")


#Metas pessoais
#Adiconar, visualizar e excluir
def metas_pessoais(usuario_id):
    while True:
        print("""
            1 - Adicionar meta
            2 - Visualizar metas
            3 - Excluir meta
            0 - Voltar
        """)
        opcao_meta = input("\33[1;37mEscolha uma opção:\33[m")

        if opcao_meta == '1':
            mensagem = input("Digite sua meta: ")
            while not mensagem.strip():
                print("\33[1;31mPor favor, forneça uma mensagem de meta.\33[m")
                mensagem = input("Digite sua meta: ")
            adicionar_meta(usuario_id, mensagem)
        elif opcao_meta == '2':
            visualizar_metas(usuario_id)
        elif opcao_meta == '3':
            excluir_meta(usuario_id)
        elif opcao_meta == '0':
            break
        else:
            print("\33[1;31mOpção inválida.\33[m")

def adicionar_meta(usuario_id, menssagem):
    try:
        inst_inserir_alimentacao = conn.cursor()
        inst_inserir_alimentacao.execute(
            f"INSERT INTO META (ID_USUARIO, MENSSAGEM) VALUES ({usuario_id}, '{menssagem}')"
        )
        conn.commit()
    except Exception as e:
        print(f"\33[1;31mErro ao inserir a alimentação no banco de dados: {e}\33[m")


    print("\33[1;33mMeta adicionada com sucesso!\33[m")

def visualizar_metas(usuario_id):
    try:
        inst_recuperar_metas = conn.cursor()
        inst_recuperar_metas.execute(
            f"SELECT MENSSAGEM FROM META WHERE ID_USUARIO = {usuario_id}"
        )
        metas = inst_recuperar_metas.fetchall()

        if metas:
            print("\nMetas:")
            for meta in metas:
                print(f"- {meta[0]}")
        else:
            print("\nNenhuma meta encontrada.\33[1;33mRegistre suas metas :)\33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao recuperar metas: {e}\33[m")

def excluir_meta(usuario_id):
    try:
        # Exibir as metas do usuário
        inst_exibir_metas = conn.cursor()
        inst_exibir_metas.execute(
            f"SELECT ID_META, MENSSAGEM FROM META WHERE ID_USUARIO = {usuario_id}"
        )
        metas = inst_exibir_metas.fetchall()

        if not metas:
            print("\nNenhuma meta encontrada.\33[1;33mRegistre suas metas :)\33[m")
            return

        print("Metas disponíveis para exclusão:")
        for meta in metas:
            id_meta, mensagem = meta
            print(f" ID: {id_meta} - {mensagem}")

        meta_a_excluir_id = input("Digite o ID da meta que deseja excluir (ou '0' para cancelar): ")

        if meta_a_excluir_id == '0':
            print("\33[1;33mOperação de exclusão cancelada.\33[m")
            return

        # Verificar se o ID da meta pertence ao usuário
        meta_encontrada = False
        for meta in metas:
            id_meta, mensagem = meta
            if str(id_meta) == meta_a_excluir_id:
                meta_encontrada = True
                break

        if not meta_encontrada:
            print("\33[1;31mID de meta inválido.\33[m")
            return

        # Excluir a meta do banco de dados
        inst_excluir_meta = conn.cursor()
        inst_excluir_meta.execute(
            f"DELETE FROM META WHERE ID_USUARIO = {usuario_id} AND ID_META = {meta_a_excluir_id}"
        )
        conn.commit()

        print("\33[1;33mMeta excluída com sucesso!\33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao excluir a meta: {e}\33[m")

#Exames
# Adicionar compromisso relacuinado a saude:  nome do compromisso, data e horario
# Verificar compromissos
# Exluir compromissos
def registrar_exames(usuario_id):
    while True:
        print("""
            1 - Adicionar exame
            2 - Visualizar exames
            3 - Excluir exame
            0 - Voltar
        """)
        opcao_exame = input("\33[1;37mEscolha uma opção:\33[m")

        if opcao_exame == '1':
            nome_exame = input("Nome do exame: ")

            while not nome_exame.strip():
                print("\33[1;31mPor favor, forneça um nome de exame.\33[m")
                nome_exame = input("Nome do exame: ")

            while True:
                data = input("Data (ex - 08/04/2023): ")
                if validar_formato_data(data):
                    break
                else:
                    print("\33[1;31mFormato de data inválido. Tente novamente.\33[m")

            while True:
                horario = input("Horário (ex - 18:00): ")

                if validar_formato_horario(horario):
                    break  
                else:
                    print("\33[1;31mFormato de horário inválido. Tente novamente.\33[m")
            adicionar_exame(usuario_id, nome_exame,data, horario)
        elif opcao_exame == '2':
            visualizar_exames(usuario_id)
        elif opcao_exame == '3':
            excluir_exame(usuario_id)
        elif opcao_exame == '0':
            break
        else:
            print("\33[1;31mOpção inválida.\33[m")

def adicionar_exame(usuario_id, nome_exame, data, horario):
    try:
        inst_inserir_exame = conn.cursor()
        inst_inserir_exame.execute(
            f"INSERT INTO EXAME (ID_USUARIO, NOME_EXAME, DATA_EXAME, HORARIO_EXAME) VALUES ({usuario_id}, '{nome_exame}', TO_DATE('{data}', 'DD/MM/YYYY'), '{horario}')"
        )
        conn.commit()
        print("\33[1;33mExame adicionado com sucesso!\33[m")
    except Exception as e:
        print(f"\33[1;31mErro ao inserir exame no banco de dados: {e}\33[m")

def visualizar_exames(usuario_id):
    try:
        inst_visualizar_exames = conn.cursor()
        inst_visualizar_exames.execute(
            f"SELECT NOME_EXAME, DATA_EXAME, HORARIO_EXAME FROM EXAME WHERE ID_USUARIO = {usuario_id}"
        )
        exames = inst_visualizar_exames.fetchall()

        if exames:
            print("\nExames:")
            for exame in exames:
                nome_exame, data_exame, horario_exame = exame
                print(f"- Nome: {nome_exame}, Data: {data_exame}, Horário: {horario_exame}")

        else:
            print("\nNenhum exame encontrado.\33[1;33mRegistre seus exames:)\33[m")


    except Exception as e:
        print(f"\33[1;31mErro ao visualizar os exames: {e}\33[m")

def excluir_exame(usuario_id):
    try:
        # Exibir as metas do usuário
        inst_exibir_exames = conn.cursor()
        inst_exibir_exames.execute(
            f"SELECT ID_EXAME, NOME_EXAME FROM EXAME WHERE ID_USUARIO = {usuario_id}"
        )
        exames = inst_exibir_exames.fetchall()

        if not exames:
            print("\nNenhum exame encontrado.\33[1;33mRegistre seus exames :)\33[m")
            return

        print("Exames disponíveis para exclusão:")
        for exame in exames:
            id_exame, nome_exame = exame
            print(f" ID: {id_exame} - {nome_exame}")

        exame_a_excluir_id = input("Digite o ID do exame que deseja excluir (ou '0' para cancelar): ")

        if exame_a_excluir_id == '0':
            print("\33[1;33mOperação de exclusão cancelada.\33[m")
            return

        # Verificar se o ID de exame pertence ao usuário
        exame_encontrada = False
        for exame in exames:
            id_exame, nome_exame = exame
            if str(id_exame) == exame_a_excluir_id:
                exame_encontrada = True
                break

        if not exame_encontrada:
            print("\33[1;31mID de exame inválido.\33[m")
            return

        # Excluir a meta do banco de dados
        inst_excluir_exame= conn.cursor()
        inst_excluir_exame.execute(
            f"DELETE FROM EXAME WHERE ID_USUARIO = {usuario_id} AND ID_EXAME= {exame_a_excluir_id}"
        )
        conn.commit()

        print("\33[1;31mExame excluído com sucesso!\33[m")

    except Exception as e:
        print(f"\33[1;31mErro ao excluir o exame: {e}\33[m")


while True:
    try:
        dsnStr = oracledb.makedsn("????????", "??????", "????????")
        conn = oracledb.connect(user='?????', password='??????', dsn=dsnStr)
        inst_login = conn.cursor()
        inst_cadastro = conn.cursor()
        inst_visualizar_perfil = conn.cursor()
        

    except Exception as e:
        print("Erro:", e)
        conexao = False
    else:
        conexao = True
        print("\n\33[1;32m* Saúde 360° *\33[m")
        print(""" 
              1. Cadastrar-se
              2. Entrar
              0. Sair
        """)

        escolha = input("\33[1;37mEscolha uma opção:\33[m ")
        if escolha == "0":
            print("\33[1;32mSaindo de Saúde 360°. Até logo, espero ver você em breve!\33[m")
            dados = carregar_dados_json()
            break
        elif escolha == "1":
            cadastrar_usuario()
        elif escolha == "2":
            usuario_id = fazer_login()
            if usuario_id is not None:
                print(f"\n\33[1;33mVocê voltou :)\33[m")
                sair = exibir_menu()
                if sair:
                    print("Voltando..")
        else:
            print("\33[1;31mOpção inválida. Tente novamente.\33[m")






