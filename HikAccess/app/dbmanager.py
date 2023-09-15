from flask import g
import sqlite3, datetime

DB_PATH = '/data/hikaccess.db'

def init_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db

def close_db():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def add_entry(entry):
    db = get_db()
    db.execute('INSERT INTO t_codes (code, valid_from, valid_upto, description) values (?, ?, ?, ?)',
               [entry.code, entry.valid_from.strftime('%Y-%m-%dT%H:%M'), entry.valid_upto.strftime('%Y-%m-%dT%H:%M'), entry.description])
    db.commit()

def get_entry(id):
    db = get_db()
    cursor = db.execute('SELECT id, code, valid_from, valid_upto, description FROM t_codes WHERE id = ?', [id])
    row = cursor.fetchone()
    return CodeEntry(row[0], row[1], row[2], row[3], row[4])

def delete_entry(id):
    db = get_db()
    db.execute('DELETE FROM t_codes WHERE id = ?', [id])
    db.commit()

def edit_entry(id, entry):
    db = get_db()
    db.execute('UPDATE t_codes SET code = ?, valid_from = ?, valid_upto = ?, description = ? WHERE id = ?',
               [entry.code, entry.valid_from.strftime('%Y-%m-%dT%H:%M'), entry.valid_upto.strftime('%Y-%m-%dT%H:%M'), entry.description, id])
    db.commit()

def purge_old_entries():
    db = get_db()
    db.execute('DELETE FROM t_codes WHERE valid_upto < ?', [datetime.datetime.now() - datetime.timedelta(days=7)])
    db.commit()

def all_entries():
    db = get_db()
    cursor = db.execute('SELECT id, code, valid_from, valid_upto, description FROM t_codes ORDER BY id DESC')
    return [CodeEntry(row[0], row[1], row[2], row[3], row[4]) for row in cursor.fetchall()]

def get_active_entries():
    entries = all_entries()
    active_entries = []
    for entry in entries:
        if entry.active:
            active_entries.append(entry)
    return active_entries

class CodeEntry:
    def __init__(self, id, code, valid_from, valid_upto, description) -> None:
        self.id = id
        self.code = code
        self.valid_from = datetime.datetime.strptime(valid_from, '%Y-%m-%dT%H:%M')
        self.valid_upto = datetime.datetime.strptime(valid_upto, '%Y-%m-%dT%H:%M')
        self.description = description

    @property
    def active(self):
        activation_threshold = datetime.datetime.now() + datetime.timedelta(minutes=15)
        deactivation_threshold = datetime.datetime.now() - datetime.timedelta(minutes=15)
        if self.valid_from < activation_threshold and self.valid_upto > deactivation_threshold:
            return True
        return False