from waitress import serve
from app.app import app

port = 8000
host = '0.0.0.0'
debug = False

def main():
    if debug:
        app.run(host=host, port=port, debug=True)
    else:
        serve(app, host=host, port=port)

if __name__ == '__main__':
    main()
