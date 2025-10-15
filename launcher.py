import webbrowser
import threading
from app import app

def run_flask():
    app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    run_flask()
