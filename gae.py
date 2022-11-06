from datetime import datetime

import flask, os
from flask import render_template, request, send_from_directory

app = flask.Flask(__name__)


@app.get("/")
def hello():
    if request.path == "/":
        return render_template('home.html')
    else:
        return send_from_directory('.', request.path)


if __name__ == "__main__":
    # Used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="localhost", port=8080, debug=True)
