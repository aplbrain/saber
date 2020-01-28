import sys
import importlib
import json
from flask import Flask, request, render_template
from flask_cors import CORS


from webanno.plugins import Plugin


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


def attach_plugin(plugin: Plugin, app: Flask):
    CORS(app)

    def _prompt():
        return plugin.prompt().replace("[[SUBMIT_URL]]", "http://localhost:5000/submit")

    def _submit():
        plugin.collect(request.json, request)
        shutdown_server()
        return "ok"

    for path, route_fn in plugin.routes().items():
        app.add_url_rule("/plugin/" + path.lstrip("/"), path, route_fn)

    app.add_url_rule("/", "prompt", _prompt)
    app.add_url_rule("/submit", "submit", _submit, methods=["POST"])


def run():
    APP = Flask(__name__)
    config = json.load(open(sys.argv[1], "r"))
    plugin = importlib.import_module(config["plugin"])
    attach_plugin(plugin._Plugin(config["config"]), APP)
    APP.run(debug=True)
