from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    ingressRoot = request.headers.get("X-Ingress-Path", "/")
    return render_template('index.html', ingressRoot=ingressRoot)