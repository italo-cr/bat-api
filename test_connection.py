import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, OperationFailure


def testar_conexao_mongodb():
    """Testa a variável de ambiente MONGODB_URI e a conexão com o MongoDB Atlas."""
    print("Iniciando teste de conexão ao MongoDB...")

    # 1. Testar a variável de ambiente
    uri = os.getenv("MONGODB_URI")

    if not uri:
        print("FALHA: A variável de ambiente MONGODB_URI NÃO está definida.")
        print("Por favor, verifique se você a configurou corretamente na seção 'Segredos' do Codex.")
        print("Certifique-se de que a CHAVE é 'MONGODB_URI' e o VALOR é a sua string de conexão completa.")
        return False
    else:
        print(f"SUCESSO: MONGODB_URI encontrada. Primeiros 30 caracteres do URI: {uri[:30]}...")

    client = None

    try:
        # 2. Tentar conectar ao MongoDB
        print("Tentando conectar ao MongoDB Atlas...")
        client = MongoClient(uri, server_api=ServerApi('1'))

        # 3. Enviar um comando ping para verificar a conexão
        print("Enviando comando ping para verificar a conexão...")
        client.admin.command('ping')
        print("SUCESSO: Pinged seu deployment. Você se conectou com sucesso ao MongoDB!")

        # 4. Opcional: Tentar listar bancos de dados para confirmar operação
        print("Tentando listar bancos de dados para confirmar a operação...")
        try:
            db_names = client.list_database_names()
            print(f"SUCESSO: Conexão ativa. Bancos de dados acessíveis: {', '.join(db_names)}")
        except OperationFailure as e:
            print(f"AVISO: Não foi possível listar bancos de dados (pode ser permissão): {e}")
            print("A conexão básica via ping foi bem-sucedida, o que é um bom sinal.")

        return True

    except ConnectionFailure as e:
        print(f"FALHA NA CONEXÃO: Não foi possível conectar ao MongoDB. Erro: {e}")
        print("Verifique os seguintes pontos:")
        print("  - Sua string de conexão (`MONGODB_URI`) está 100% correta (usuário, senha, cluster)?")
        print("  - Seu IP foi adicionado à lista de acesso de IP no MongoDB Atlas?")
        print("  - Há alguma restrição de firewall no seu ambiente Codex ou na rede do MongoDB Atlas?")
        return False
    except Exception as e:
        print(f"OCORREU UM ERRO INESPERADO: {e}")
        print("Pode ser um problema com a string de conexão mal formatada ou outra questão.")
        return False
    finally:
        if client:
            print("Fechando conexão com o MongoDB.")
            client.close()


if __name__ == "__main__":
    if testar_conexao_mongodb():
        print("\nTeste de conexão concluído com SUCESSO!")
    else:
        print("\nTeste de conexão concluído com FALHA.")
