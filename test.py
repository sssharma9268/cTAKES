from flask import Flask

import os
app = Flask(__name__)


@app.route("/")

def hello():
    html = "<h3>Test:{test}</h3>"
    test = os.environ['JAVA_HOME']

    return html.format(test = test)


if __name__ == '__main__':
    app.run()
