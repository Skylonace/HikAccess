from app.app import app

PORT = 8000
HOST = '0.0.0.0'
DEBUG = True

app.run(host=HOST, port=PORT, debug=DEBUG)