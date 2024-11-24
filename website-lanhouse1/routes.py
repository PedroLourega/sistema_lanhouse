from main import app
from flask import render_template

#rotas
@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/calcular_sessao")
def calcular_sessao():
    return "calcular_sessao"

@app.route("/registro")
def registro():
    return "registro"