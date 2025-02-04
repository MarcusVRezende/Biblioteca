from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from urllib.parse import unquote
import os

# Configuração do Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_padrao_insegura")
socketio = SocketIO(app)

# Classes de Usuário (Herança - Para atender ao requisito do trabalho)
class UsuarioBase:
    def __init__(self, nome):
        self.nome = nome

class Admin(UsuarioBase):
    def __init__(self, nome):
        super().__init__(nome)
        self.permissao_total = True

class UsuarioComum(UsuarioBase):
    def __init__(self, nome):
        super().__init__(nome)
        self.livros_emprestados = []

# 📌 Dicionário da Biblioteca (Corrigido e organizado em ordem alfabética)
biblioteca = {
    "livros": [
        {"titulo": "A Divina Comédia", "autor": "Dante Alighieri", "disponivel": True},
        {"titulo": "A Revolução dos Bichos", "autor": "George Orwell", "disponivel": True},
        {"titulo": "As Crônicas de Nárnia", "autor": "C. S. Lewis", "disponivel": True},
        {"titulo": "Capitães da Areia", "autor": "Jorge Amado", "disponivel": True},
        {"titulo": "Cem Anos de Solidão", "autor": "Gabriel García Márquez", "disponivel": True},
        {"titulo": "Crime e Castigo", "autor": "Fiódor Dostoiévski", "disponivel": True},
        {"titulo": "Dom Casmurro", "autor": "Machado de Assis", "disponivel": True},
        {"titulo": "Dom Quixote", "autor": "Miguel de Cervantes", "disponivel": True},
        {"titulo": "Drácula", "autor": "Bram Stoker", "disponivel": True},
        {"titulo": "Frankestein", "autor": "Mary Shelley", "disponivel": True},
        {"titulo": "Grande Sertão: Veredas", "autor": "Guimarães Rosa", "disponivel": True},
        {"titulo": "Harry Potter e a Pedra Filosofal", "autor": "J. K. Rowling", "disponivel": True},
        {"titulo": "Iracema", "autor": "José de Alencar", "disponivel": True},
        {"titulo": "Memórias Póstumas de Brás Cubas", "autor": "Machado de Assis", "disponivel": True},
        {"titulo": "O Alquimista", "autor": "Paulo Coelho", "disponivel": True},
        {"titulo": "O Cortiço", "autor": "Aluísio Azevedo", "disponivel": True},
        {"titulo": "O Hobbit", "autor": "J. R. R. Tolkien", "disponivel": True},
        {"titulo": "O Pequeno Príncipe", "autor": "Antoine de Saint-Exupéry", "disponivel": True},
        {"titulo": "O Senhor dos Anéis", "autor": "J. R. R. Tolkien", "disponivel": True},
        {"titulo": "Orgulho e Preconceito", "autor": "Jane Austen", "disponivel": True},
        {"titulo": "Os Miseráveis", "autor": "Victor Hugo", "disponivel": True},
        {"titulo": "Percy Jackson e o Ladrão de Raios", "autor": "Rick Riordan", "disponivel": True},
        {"titulo": "Romeu e Julieta", "autor": "William Shakespeare", "disponivel": True},
        {"titulo": "Vidas Secas", "autor": "Graciliano Ramos", "disponivel": True}
    ],
    "usuarios": {"admin": "admin123"}  # ✅ ERRO CORRIGIDO: vírgula antes de "usuarios"
}

# 📌 Rotas do Flask
@app.route('/')
def home():
    return render_template('index.html', livros=biblioteca["livros"])

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario in biblioteca['usuarios'] and senha == "admin123":
            session['usuario'] = usuario
            return redirect(url_for('dashboard'))
        else:
            erro = "Usuário ou senha incorretos!"
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('home'))  

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', livros=biblioteca["livros"])

@app.route('/livros')
def listar_livros():
    return jsonify(livros=biblioteca["livros"]) 

@app.route('/adicionar_livro', methods=['POST'])
def adicionar_livro():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    titulo = request.form.get('titulo')
    autor = request.form.get('autor')
    if titulo and autor:
        biblioteca['livros'].append({"titulo": titulo, "autor": autor, "disponivel": True})
        socketio.emit('livros_atualizados', biblioteca['livros'], namespace='/')  
    return redirect(url_for('dashboard'))

@app.route('/remover_livro/<titulo>', methods=['POST'])
def remover_livro(titulo):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    biblioteca['livros'] = [livro for livro in biblioteca['livros'] if livro['titulo'] != titulo]
    socketio.emit('livros_atualizados', biblioteca['livros'], namespace='/')  
    return redirect(url_for('dashboard'))

@app.route('/emprestar/<titulo>')
def emprestar(titulo):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    titulo_decodificado = unquote(titulo)

    for livro in biblioteca["livros"]:
        if livro["titulo"] == titulo_decodificado and livro["disponivel"]:
            livro["disponivel"] = False
            socketio.emit('livros_atualizados', biblioteca["livros"], namespace='/')
            return jsonify(livros=biblioteca["livros"])  

    return jsonify(livros=biblioteca["livros"])

@app.route('/devolver/<titulo>')
def devolver(titulo):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    titulo_decodificado = unquote(titulo)

    for livro in biblioteca["livros"]:
        if livro["titulo"] == titulo_decodificado and not livro["disponivel"]:
            livro["disponivel"] = True
            socketio.emit('livros_atualizados', biblioteca["livros"], namespace='/')  
            return jsonify(livros=biblioteca["livros"])  

    return jsonify(livros=biblioteca["livros"])

@socketio.on('atualizar_livros')
def atualizar_livros():
    emit('livros_atualizados', biblioteca["livros"], namespace='/')

# 🔥 Correção: Apenas um bloco de execução do Flask
if __name__ == '__main__':
    socketio.run(app, debug=True)
