from flask import Flask, request, render_template, redirect, g
from .dbmanager import init_db, purge_old_entries, close_db, add_entry, get_entry, edit_entry, all_entries, delete_entry, CodeEntry
from .intercom import intercom_thread, request_intercom_codes, parse_codes, delete_code, upload_code, Code
from threading import Thread

app = Flask(__name__)

@app.before_request
def init_server():
    init_db(app)
    purge_old_entries()
    g.intercom_thread = Thread(target=intercom_thread)

@app.route('/', methods = ['POST', 'GET'])
def entries():
    ingress_root = request.headers.get("X-Ingress-Path", "")
    purge_old_entries()
    return render_template('entries.html',
                           ingress_root=ingress_root,
                           entries=all_entries())

@app.route('/delete/<int:id>')
def delete(id):
    ingress_root = request.headers.get("X-Ingress-Path", "")
    delete_entry(id)
    return redirect(ingress_root + '/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    ingress_root = request.headers.get("X-Ingress-Path", "")
    if request.method == 'POST':
        entry = CodeEntry(id,
                          request.form['code'],
                          request.form['valid_from'],
                          request.form['valid_upto'],
                          request.form['description'])
        edit_entry(id, entry)
        return redirect(ingress_root + '/')
    return render_template('edit.html',ingress_root=ingress_root, entry=get_entry(id))

@app.route('/add', methods=['GET', 'POST'])
def add():
    ingress_root = request.headers.get("X-Ingress-Path", "")
    if request.method == 'POST':
        entry = CodeEntry(None,
                          request.form['code'],
                          request.form['valid_from'],
                          request.form['valid_upto'],
                          request.form['description'])
        add_entry(entry)
        return redirect(ingress_root + '/')
    return render_template('add.html', ingress_root=ingress_root)

@app.route('/intercom')
def intercom_info():
    ingress_root = request.headers.get("X-Ingress-Path", "")
    codes = []
    msg = ""
    try:
        codes = parse_codes(request_intercom_codes())
    except Exception as e:
        msg = e
    return render_template('intercom.html', ingress_root=ingress_root, codes=codes, msg=msg)

@app.route('/delete_code/<int:slot_number>')
def delete_intercom(slot_number):
    ingress_root = request.headers.get("X-Ingress-Path", "")
    try:
        delete_code(slot_number)
    except Exception as e:
        print(e)
    return redirect(ingress_root + '/intercom')

@app.route('/edit_code/<int:slot_number>', methods=['GET', 'POST'])
def edit_intercom(slot_number):
    ingress_root = request.headers.get("X-Ingress-Path", "")
    if request.method == 'POST':
        upload_code(request.form['code'],request.form['description'], slot_number)
        return redirect(ingress_root + '/intercom')
    return render_template('edit.html',ingress_root=ingress_root, slot_number=slot_number)

@app.teardown_appcontext
def close_connection(exception):
    close_db()