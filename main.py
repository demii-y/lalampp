from threading import Thread
import webview
from app import create_app


def start_server():
    app = create_app()
    # Change host/port if needed
    app.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    t = Thread(target=start_server)
    t.daemon = True
    t.start()
    webview.create_window('Lalampp', 'http://127.0.0.1:5000')
    webview.start()
