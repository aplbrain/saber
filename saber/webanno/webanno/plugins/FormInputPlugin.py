import json
from .plugin import Plugin


HTML_PAGE = """
<html>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css">
    <script>
    function handleClick() {
        fetch("[[SUBMIT_URL]]", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                [[FORM_AS_JS]]
            })
        }).then(() => {
            alert("Thank you! You may close this page.")
        })
    }
    </script>
    <body>
        <div class="container">
            <div class="section">
                <div class="columns">
                    <div class="column is-8 is-offset-2">
                        <div class="card">
                            <div class="card-content">
                                <div class="section">
                                    [[FORM_HTML]]
                                </div>
                                <div class="section">
                                    <button
                                        class="button is-primary is-fullwidth"
                                        onclick="handleClick()">
                                        SUBMIT
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
</html>
"""


class FormInputPlugin(Plugin):
    def __init__(self, config: dict):
        self.json_file_output = config.get("json_file_output", "results.json")
        self.config = config

    def _fields_html(self) -> str:
        html = ""
        for field in self.config["fields"]:
            html += f"""
                <div class="field">
                    <label class="label">{field.get("label", field.get("name"))}</label>
                    <input
                        id='{field.get("name")}'
                        class='input'
                        type='{field['type']}'
                        name='{field['name']}'
                        placeholder='{field.get("label", field.get("name"))}'
                        />
                </div>
            """
        return html

    def _fields_as_js(self) -> str:
        js = ""
        for field in self.config["fields"]:
            js += f"""
            "{field['name']}": document.getElementById('{field['name']}').value,
            """
        return js

    def prompt(self) -> str:
        return HTML_PAGE.replace("[[FORM_HTML]]", self._fields_html()).replace(
            "[[FORM_AS_JS]]", self._fields_as_js()
        )

    def collect(self, data: dict, response):
        # Response is a Flask response
        with open(self.json_file_output, "w") as fh:
            json.dump(data, fh)
        return True


_Plugin = FormInputPlugin
