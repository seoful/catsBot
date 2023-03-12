from multiprocessing import Process
from time import sleep
from flask import Flask


app = Flask(__name__)


@app.route("/")
def check_app():
    return "OK"


def run():
    server = Process(target=lambda: app.run(host="0.0.0.0", port=8080))
    server.start()
    sleep(10)
    server.terminate()
    server.join()
