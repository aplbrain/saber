import abc


class Plugin(abc.ABC):
    def prompt(self) -> str:
        ...

    def collect(self, data: dict, response):
        # response is a flask response
        ...

    def routes(self):
        return {}
