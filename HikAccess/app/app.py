from flask import Flask, request, render_template, g, redirect
from .dbmanager import init_db, close_db, add_entry, get_entry, edit_entry, all_entries, delete_entry, CodeEntry

app = Flask(__name__)

@app.before_request
def init_server():
    init_db(app)

@app.route('/', methods = ['POST', 'GET'])
def index():
    ingressRoot = request.headers.get("X-Ingress-Path", "")
    return render_template('index.html',
                           ingressRoot=ingressRoot,
                           entries=all_entries())

@app.route('/delete/<int:id>')
def delete(id):
    ingressRoot = request.headers.get("X-Ingress-Path", "")
    delete_entry(id)
    return redirect(ingressRoot + '/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    ingressRoot = request.headers.get("X-Ingress-Path", "")
    if request.method == 'POST':
        entry = CodeEntry(id,
                          request.form['code'],
                          request.form['validFrom'],
                          request.form['validUpTo'],
                          request.form['description'])
        edit_entry(id, entry)
        return redirect(ingressRoot + '/')
    return render_template('edit.html',ingressRoot=ingressRoot, entry=get_entry(id))

@app.route('/add', methods=['GET', 'POST'])
def add():
    ingressRoot = request.headers.get("X-Ingress-Path", "")
    if request.method == 'POST':
        entry = CodeEntry(None,
                          request.form['code'],
                          request.form['validFrom'],
                          request.form['validUpTo'],
                          request.form['description'])
        add_entry(entry)
        return redirect(ingressRoot + '/')
    return render_template('add.html', ingressRoot=ingressRoot)

@app.teardown_appcontext
def close_connection(exception):
    close_db()