from waitress import serve
from app.app import app
import sys

port = 8000
host = '0.0.0.0'
debug = True

def main():
    if debug:
        app.run(host=host, port=port, debug=True)
    else:
        serve(app, host=host, port=port)

if __name__ == '__main__':
    main()
