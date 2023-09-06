from flask import g
import sqlite3

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
               [entry.code, entry.validFrom, entry.validUpTo, entry.description])
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
               [entry.code, entry.validFrom, entry.validUpTo, entry.description, id])
    db.commit()

def all_entries():
    db = get_db()
    cursor = db.execute('SELECT id, code, valid_from, valid_upto, description FROM t_codes ORDER BY id DESC')
    return [CodeEntry(row[0], row[1], row[2], row[3], row[4]) for row in cursor.fetchall()]

class CodeEntry:
    def __init__(self, id, code, validFrom, validUpTo, description) -> None:
        self.id = id
        self.code = code
        self.validFrom = validFrom
        self.validUpTo = validUpTo
        self.description = description
