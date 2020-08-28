from typing import Tuple
import json
import io
import os.path

import numpy as np
from flask import send_file
from PIL import Image
from intern.remote.boss import BossRemote
from .plugin import Plugin


def _get_boss_remote_and_channel(
    uri: str, token: str = "public"
) -> Tuple[BossRemote, "Channel"]:
    _, protocol, url = uri.split("://")
    host, col, exp, chan = url.split("/")
    boss = BossRemote({"protocol": protocol, "host": host, "token": token})
    return (boss, boss.get_channel(chan, col, exp))


my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "templates/BossVolumePlugin.html")
with open(path) as f:
    HTML_PAGE = f.read()


class CentroidsPlugin(Plugin):
    def __init__(self, config: dict):
        self.json_file_output = config.get("json_file_output", "results.json")
        self.config = config
        self.text_prompt = config.get("prompt", "")
        self.max_count = config.get("max_count", "undefined")
        self.dot_color = config.get("dot_color", [255, 255, 255])
        self.boss_uri = config["boss_uri"]
        self.boss, self.channel = _get_boss_remote_and_channel(self.boss_uri)
        self.start = config["start"]
        self.stop = config["stop"]
        self.xs = [self.start[0], self.stop[0]]
        self.ys = [self.start[1], self.stop[1]]
        self.zs = [self.start[2], self.stop[2]]
        self.resolution = config.get("resolution", 0)

    def prompt(self) -> str:
        return (
            HTML_PAGE.replace("[[PROMPT]]", self.text_prompt)
            .replace("[[IMAGE_URL]]", self.boss_uri)
            .replace("[[MAX_COUNT]]", str(self.max_count))
            .replace("[[DOT_COLOR]]", "[{}, {}, {}]".format(*self.dot_color))
            .replace(
                "[[IMG_SIZE]]",
                f"[{self.xs[1] - self.xs[0]}, {self.ys[1] - self.ys[0]}, {self.zs[1] - self.zs[0]}]",
            )
        )

    def collect(self, data: dict, response):
        # Response is a Flask response
        with open(self.json_file_output, "w") as fh:
            json.dump(data, fh)
        return True

    def routes(self):
        return {"/volume": self._route_get_volume_as_filmstrip}

    def _route_get_volume_as_filmstrip(self):
        data = self.boss.get_cutout(
            self.channel, self.resolution, self.xs, self.ys, self.zs
        )
        img = Image.fromarray(np.concatenate([z for z in data], axis=0))
        imgio = io.BytesIO()
        img.save(imgio, format="jpeg")
        imgio.seek(0)
        return send_file(imgio, mimetype="image/jpeg")


_Plugin = CentroidsPlugin
