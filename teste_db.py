from database import Database
import os

def rodar_testes():
    # 1. Setup: Criar um banco de teste separado para não sujar o original
    test_db_name = "test_inventario.db"
    if os.path.exists(test_db_name):
        os.remove(test_db_name)
    
    db = Database(test_db_name)
    print(" Iniciando Testes Automatizados...")

    # TESTE 1: Inserção de Ativo
    print("\n[Teste 1] Inserindo ativo novo...")
    sucesso = db.inserir_ativo("TEST-01", "Notebook", "Dell", "G15", "SN123")
    if sucesso:
        print(" Sucesso: Ativo inserido.")
    else:
        print(" Falha: Erro ao inserir ativo válido.")

    # TESTE 2: Duplicidade (O sistema deve barrar)
    print("\n[Teste 2] Testando bloqueio de TAG duplicada...")
    duplicado = db.inserir_ativo("TEST-01", "Monitor", "LG", "29WK", "SN456")
    if not duplicado:
        print(" Sucesso: O sistema barrou a TAG duplicada corretamente.")
    else:
        print(" Falha: O sistema permitiu cadastrar a mesma TAG duas vezes!")

    # TESTE 3: Atualização de Responsável e Status
    print("\n[Teste 3] Testando atribuição de responsável...")
    db.atualizar_responsavel("TEST-01", "Carlos Pluma")
    
    # Verificar se mudou no banco
    ativos = db.listar_ativos()
    ativo_test = next(a for a in ativos if a['tag_patrimonio'] == "TEST-01")
    
    if ativo_test['responsavel_atual'] == "Carlos Pluma" and ativo_test['status'] == "Em Uso":
        print(" Sucesso: Responsável vinculado e Status alterado para 'Em Uso'.")
    else:
        print(" Falha: Dados de atribuição não conferem.")

    # 4. Limpeza
    print("\n Limpando ambiente de teste...")
    os.remove(test_db_name)
    print("\n Todos os testes concluídos!")

if __name__ == "__main__":
    rodar_testes()