from flask import Flask, render_template, redirect, request, url_for, send_file, session, make_response
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    rg = db.Column(db.String(20), nullable=True)

def validar_rg(rg, cargo):
    if cargo != 'aluno':
        rg = ''.join(filter(str.isdigit, rg))
        if len(rg) < 7 or len(rg) > 10:
            return False
    return True

@app.route('/')
def home():
    return render_template('escolha.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['firstname']
        sobrenome = request.form['lastname']
        cargo = request.form['oqvce']
        rg = request.form['RG']

        if not validar_rg(rg, cargo):
            ultimo_usuario = session.get('ultimousuario', None)
            return render_template('index.html', ultimousuario=ultimo_usuario, erro_rg="RG inválido!")

        novo_usuario = Usuarios(nome=nome, sobrenome=sobrenome, cargo=cargo, rg=rg)
        db.session.add(novo_usuario)
        db.session.commit()

        session['ultimousuario'] = nome
        print(nome)
        return redirect(url_for('cadastro'))
            
    ultimo_usuario = session.get('ultimousuario', None)
    return render_template('index.html', ultimousuario=ultimo_usuario)

@app.route('/relatorios')
def relatorio():
    usuarios = Usuarios.query.all()
    return render_template('relatorios.html', usuarios=usuarios)


@app.route('/pesquisar', methods=['GET', 'POST'])
def pesquisar():
    usuarios = Usuarios.query.all()
    return render_template('pesquisar_usuario.html', usuarios=usuarios)

@app.route('/gerar_pdf')
def gerar_pdf():
    usuarios = Usuarios.query.all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Relatório de Usuários", ln=True, align='C')
    
    for usuario in usuarios:
        pdf.cell(200, 10, txt=f"{usuario.nome} {usuario.sobrenome} - {usuario.cargo} - {usuario.horario_chegada} - {usuario.rg}", ln=True)
    
    # Gerar o PDF em memória
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio_usuarios.pdf'
    return response
    
# So pra testar
@app.route('/popular_db')
def popular_db():
    import random
    nomes = ["Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Julia",
             "Kleber", "Larissa", "Marcos", "Natália", "Otávio", "Paula", "Quésia", "Rafael", "Sabrina", "Thiago",
             "Ursula", "Vinicius", "Wesley", "Xuxa", "Yasmin", "Zeca"]
    sobrenomes = ["Silva", "Souza", "Oliveira", "Santos", "Pereira", "Costa", "Rodrigues", "Almeida", "Nascimento", "Lima"]
    cargos = ["aluno", "professor", "visitante", "responsavel", "paimae"]

    for i in range(50):
        nome = random.choice(nomes)
        sobrenome = random.choice(sobrenomes)
        cargo = random.choice(cargos)
        rg = str(random.randint(1000000, 999999999))
        usuario = Usuarios(nome=nome, sobrenome=sobrenome, cargo=cargo, rg=rg)
        db.session.add(usuario)
    db.session.commit()
    return "Banco populado com 50 usuários!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=False)

    # To com uma vontade absurda de aplicar CC nesse código, mas não vejo necessidade
    # disso agora.