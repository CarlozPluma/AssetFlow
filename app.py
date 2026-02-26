import io
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from database import Database
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = '20@09@2003@dvpl'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Define para onde vai quem não está logado

db = Database()

# Classe de Usuário necessária para o Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    user_db = db.buscar_usuario_por_id(user_id)
    if user_db:
        return User(id=user_db['id'], username=user_db['username'], role=user_db['role'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_db = db.buscar_usuario(username)
        
        #Compara a senha digitada com o Hash do banco
        if user_db and check_password_hash(user_db['password'], password):
            user_obj = User(id=user_db['id'], username=user_db['username'], role=user_db['role'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required 
def index():
    # Captura os filtros que vêm da URL (se existirem)
    filtro_tipo = request.args.get('tipo', '')
    filtro_modelo = request.args.get('modelo', '')

    # Busca os ativos filtrados (ou todos, se os campos estiverem vazios)
    ativos = db.listar_inventario_filtrado(filtro_tipo, filtro_modelo)
    
    stats = db.get_estatisticas()
    meus_equipamentos = db.listar_equipamentos_por_responsavel(current_user.id)
    
    return render_template('index.html', 
                            ativos=ativos, 
                            stats=stats, 
                            meus_equipamentos=meus_equipamentos,
                            filtro_tipo=filtro_tipo,
                            filtro_modelo=filtro_modelo)

@app.route('/editar/<tag>', methods=['GET', 'POST'])
def editar(tag):
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        serie = request.form.get('serie')
        status = request.form.get('status')
        
        if db.atualizar_ativo(tag, tipo, marca, modelo, serie, status):
            flash('Ativo atualizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erro ao atualizar o ativo.', 'danger')

    ativo = db.buscar_ativo_por_tag(tag)
    return render_template('editar.html', ativo=ativo)

@app.route('/colaboradores')
@login_required
def colaboradores():
    lista_usuarios = db.listar_usuarios()
    return render_template('colaboradores.html', usuarios=lista_usuarios)

@app.route('/atualizar_responsavel', methods=['POST'])
@login_required
def atualizar_responsavel():
    tag = request.form.get('tag')
    responsavel = request.form.get('responsavel')
    
    if db.atualizar_responsavel(tag, responsavel):
        flash(f'Responsável do ativo {tag} atualizado com sucesso!', 'success')
    else:
        flash('Erro ao atualizar responsável.', 'danger')
        
    return redirect(url_for('index'))

@app.route('/relatorio/pdf')
@login_required
def gerar_relatorio_pdf():
    # 1. Captura os filtros da URL (os mesmos usados na index)
    filtro_tipo = request.args.get('tipo', '')
    filtro_modelo = request.args.get('modelo', '')

    # 2. Busca os dados usando a nova função filtrada que criamos no database.py
    # Se os filtros estiverem vazios, ela trará tudo automaticamente
    ativos = db.listar_inventario_filtrado(filtro_tipo, filtro_modelo)
    
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "AssetFlow - Relatório de Inventário de TI", 
            new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 10, f"Gerado por: {current_user.username}", 
            new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # Linha extra para mostrar quais filtros foram aplicados no PDF
    texto_filtro = f"Filtros: Tipo [{filtro_tipo or 'Todos'}] | Modelo [{filtro_modelo or 'Todos'}]"
    pdf.set_font("helvetica", "I", 8)
    pdf.cell(0, 10, texto_filtro, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.ln(5)
    
    # Tabela Cabeçalho
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(30, 10, "Patrimônio", border=1, fill=True)
    pdf.cell(35, 10, "Tipo", border=1, fill=True)
    pdf.cell(50, 10, "Modelo", border=1, fill=True)
    pdf.cell(30, 10, "Status", border=1, fill=True)
    pdf.cell(45, 10, "Responsável", border=1, fill=True, 
            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Tabela Dados
    pdf.set_font("helvetica", "", 9)
    for ativo in ativos:
        # Garante que o texto não seja None para não dar erro no PDF
        resp = ativo['responsavel_atual'] if ativo['responsavel_atual'] else "N/A"
        
        pdf.cell(30, 10, str(ativo['tag_patrimonio']), border=1)
        pdf.cell(35, 10, str(ativo['tipo']), border=1)
        pdf.cell(50, 10, str(ativo['modelo']), border=1)
        pdf.cell(30, 10, str(ativo['status']), border=1)
        pdf.cell(45, 10, str(resp), border=1, 
                new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Geramos o PDF como bytes e colocamos num buffer de memória
    pdf_output = pdf.output()
    buffer = io.BytesIO(pdf_output)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=False,
        download_name='relatorio_ativos.pdf',
        mimetype='application/pdf'
    )

@app.route('/excluir_ativo/<tag>')
@login_required
def deletar_ativo(tag):
    if db.excluir_ativo(tag):
        flash(f'Ativo {tag} removido com sucesso!', 'success')
    else:
        flash('Erro ao tentar remover o ativo.', 'danger')
    return redirect(url_for('index'))

@app.route('/colaboradores/excluir/<int:id_usuario>')
@login_required
def eliminar_colaborador(id_usuario):
    # SEGURANÇA: Apenas admin pode excluir
    if current_user.username != 'admin':
        flash('Acesso negado!', 'danger')
        return redirect(url_for('index'))

    # SEGURANÇA: Impedir que o admin se exclua a si próprio
    if id_usuario == current_user.id:
        flash('Erro: Não podes eliminar a tua própria conta de administrador!', 'warning')
        return redirect(url_for('colaboradores'))

    if db.excluir_usuario(id_usuario):
        flash('Utilizador removido com sucesso!', 'success')
    else:
        flash('Erro ao tentar remover utilizador.', 'danger')
        
    return redirect(url_for('colaboradores'))

@app.route('/colaboradores/novo', methods=['GET', 'POST'])
@login_required
def novo_colaborador():
    # trava de segurança para apenas o admin fazer alteraçoes nos usuarios
    if current_user.role != 'admin':
        flash('Acesso negado: apenas o administrador pode criar usuários.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        novo_user = request.form.get('username')
        nova_senha = request.form.get('password')
        cargo_atribuido = request.form.get('role')
        
        if db.inserir_usuario(novo_user, nova_senha, cargo_atribuido):
            flash(f'Usuário {novo_user} ({cargo_atribuido}) criado com sucesso!', 'success')
            return redirect(url_for('colaboradores'))
        else:
            flash('Erro: Este nome de usuário já existe.', 'danger')
            
    return render_template('novo_colaborador.html')

@app.route('/add_equipamento', methods=['POST'])
@login_required
def add_equipamento():
    nome = request.form.get('nome_equipamento')
    tipo = request.form.get('tipo')
    patrimonio = request.form.get('patrimonio')
    user_id = current_user.id # Pega automaticamente o ID do técnico logado
    
    if db.inserir_equipamento(nome, tipo, patrimonio, user_id):
        flash('Equipamento vinculado com sucesso!', 'success')
    else:
        flash('Erro: Património já registado em outro sistema.', 'danger')
        
    return redirect(url_for('index'))

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        tag = request.form.get('tag')
        tipo = request.form.get('tipo')
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        serie = request.form.get('serie')
        
        # O método inserir_ativo retorna True ou False devido ao IntegrityError
        sucesso = db.inserir_ativo(tag, tipo, marca, modelo, serie)
        
        if sucesso:
            flash('Ativo cadastrado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erro: Tag de Patrimônio ou Série já cadastrada.', 'danger')
    
    return render_template('cadastrar.html')

if __name__ == '__main__':
    app.run(debug=True)