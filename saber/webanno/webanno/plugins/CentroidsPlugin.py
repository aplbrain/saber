import json
from .plugin import Plugin

HTML_PAGE = """
<html>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css">
    <script src="https://cdn.jsdelivr.net/npm/p5@0.10.2/lib/p5.js"></script>
    <script>

    let maxCount = [[MAX_COUNT]];

    let img;
    let ready = false;
    let clicks = [];
    function setup() {
        canvas = createCanvas(600, 600);
        canvas.parent('canvas-container');
        background(123, 234, 123);
        img = createImg('[[IMAGE_URL]]', '', () => ready = true);
        img.hide();
    }

    function draw() {
        if (ready) {
            image(img, 0, 0);
        }
        noStroke();
        for (let i = 0; i < clicks.length; i++) {
            fill(255);
            circle(clicks[i][0], clicks[i][1], 20, 20)
            fill(0);
            circle(clicks[i][0], clicks[i][1], 10, 10)
        }
    }

    function mouseClicked() {
        if (maxCount && clicks.length < maxCount) {
            clicks.push([mouseX, mouseY]);
        }
    }


    function handleClick() {
        fetch("[[SUBMIT_URL]]", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                clicks,
            })
        }).then(() => {
            alert("Thank you! You may close this page.")
        })
    }
    </script>
    <body>
        <h1>[[PROMPT]]</h1>
        <div id="canvas-container"></div>
        <button class="button" onclick="handleClick()">SUBMIT</button>
    </body>
</html>
"""


class CentroidsPlugin(Plugin):
    def __init__(self, config: dict):
        self.json_file_output = config.get("json_file_output", "results.json")
        self.config = config
        self.text_prompt = config.get("prompt", "")
        self.max_count = config.get("max_count", "undefined")
        self.image_url = config["image_url"]

    def prompt(self) -> str:
        return (
            HTML_PAGE.replace("[[PROMPT]]", self.text_prompt)
            .replace("[[IMAGE_URL]]", self.image_url)
            .replace("[[MAX_COUNT]]", str(self.max_count))
        )

    def collect(self, data: dict, response):
        # Response is a Flask response
        with open(self.json_file_output, "w") as fh:
            json.dump(data, fh)
        return True


_Plugin = CentroidsPlugin
