import json
from .plugin import Plugin


class ButtonPressPlugin(Plugin):
    def __init__(self, config: dict):
        self.json_file_output = config.get("json_file_output", "results.json")

    def prompt(self) -> str:
        return """
        <html>
            <script>
            function handleClick() {
                fetch("[[SUBMIT_URL]]", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        "submitted": new Date()
                    })
                }).then(() => {
                    alert("Thank you! You may close this page.")
                })
            }
            </script>
            <body>
                <button onclick="handleClick()" type="button">Submit</button>
            </body>
        </html>
        """

    def collect(self, data: dict):
        with open(self.json_file_output, "w") as fh:
            json.dump(data, fh)
        return True


_Plugin = ButtonPressPlugin
