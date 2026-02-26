import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    def __init__(self, db_name="inventario_ti.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        with open('schema.sql', 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())
        conn.commit()
        
        cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
        if not cursor.fetchone():
            senha_hash = generate_password_hash('admin123')
            cursor.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)",
                            ('admin', senha_hash, 'admin'))
            conn.commit()
            print("Usuário Admin criado com sucesso!")
            
        conn.close()

    def inserir_ativo(self, tag, tipo, marca, modelo, serie):
        """Método unificado com o nome de coluna correto: num_serie"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """INSERT INTO ativos (tag_patrimonio, tipo, marca, modelo, num_serie, status) 
                    VALUES (?, ?, ?, ?, ?, 'Disponível')"""
            cursor.execute(query, (tag, tipo, marca, modelo, serie))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Erro de integridade (Tag ou Série duplicada): {e}")
            return False
        finally:
            conn.close()

    def excluir_ativo(self, tag):
        """Remove um ativo permanentemente do banco de dados."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ativos WHERE tag_patrimonio = ?", (tag,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir ativo: {e}")
            return False
        finally:
            conn.close()

    def buscar_usuario(self, username):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def buscar_usuario_por_id(self, user_id):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    def excluir_usuario(self, id_usuario):
        """Remove um utilizador do sistema pelo ID."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir utilizador: {e}")
            return False
        finally:
            conn.close()

    def inserir_usuario(self, username, password, role='tecnico'):
        """Cria um novo usuário com senha protegida por Hash."""
        try:
            # Gera o hash da senha antes de salvar
            senha_hash = generate_password_hash(password) 
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", 
                            (username, senha_hash, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def listar_usuarios(self):
        """Retorna a lista de todos os usuários que acessam o sistema."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM usuarios ORDER BY username ASC")
        usuarios = cursor.fetchall()
        conn.close()
        return usuarios

    def listar_inventario_resumo(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ativos") 
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def listar_inventario_filtrado(self, tipo="", modelo=""):
        query = "SELECT * FROM ativos WHERE 1=1"
        params = []

        if tipo:
            query += " AND tipo LIKE ?"
            params.append(f"%{tipo}%")
    
        if modelo:
            query += " AND modelo LIKE ?"
            params.append(f"%{modelo}%")

        query += " ORDER BY tag_patrimonio DESC"

        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def get_estatisticas(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM ativos GROUP BY status")
        stats = dict(cursor.fetchall())
        conn.close()
        return stats
    
    
    def buscar_ativo_por_tag(self, tag):
        """Busca os detalhes de um ativo específico pela Tag."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ativos WHERE tag_patrimonio = ?", (tag,))
        ativo = cursor.fetchone()
        conn.close()
        return ativo

    def atualizar_ativo(self, tag_original, tipo, marca, modelo, serie, status):
        """Atualiza os dados do ativo no banco."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """UPDATE ativos 
                        SET tipo = ?, marca = ?, modelo = ?, num_serie = ?, status = ?
                        WHERE tag_patrimonio = ?"""
            cursor.execute(query, (tipo, marca, modelo, serie, status, tag_original))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar: {e}")
            return False
        finally:
            conn.close()
            
    

    def inserir_equipamento(self, nome, tipo, patrimonio, responsavel_id):
        """Vincula um equipamento específico a um técnico/usuário."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """INSERT INTO equipamentos (nome_equipamento, tipo, patrimonio, responsavel_id) 
                        VALUES (?, ?, ?, ?)"""
            cursor.execute(query, (nome, tipo, patrimonio, responsavel_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def listar_equipamentos_por_responsavel(self, user_id):
        """Retorna todos os equipamentos sob responsabilidade de um usuário específico."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipamentos WHERE responsavel_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def atualizar_responsavel(self, tag, novo_responsavel):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Ao definir um responsável, o status muda automaticamente para 'Em Uso'
            query = "UPDATE ativos SET responsavel_atual = ?, status = 'Em Uso' WHERE tag_patrimonio = ?"
            cursor.execute(query, (novo_responsavel, tag))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar responsável: {e}")
            return False
        finally:
            conn.close()
            
    def listar_ativos(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ativos")
        rows = cursor.fetchall()
        conn.close()
        return rows