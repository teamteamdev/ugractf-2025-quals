import multiprocessing

from gunicorn.app.base import BaseApplication

from racelights.app import app


class Application(BaseApplication):
    def __init__(self):
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            "bind": "unix:/tmp/app.sock",
            "workers": min(multiprocessing.cpu_count() * 2, 8),
            "timeout": 180,
            "worker_class": "uvicorn.workers.UvicornWorker"
        }

        for key, value in config.items():
            if key in self.cfg.settings:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
