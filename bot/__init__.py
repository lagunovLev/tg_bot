import threading
from tg.run import run_bot
from app import app
import main


if __name__ == '__main__':
    th = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080))
    th.start()
    run_bot()
    th.join()
