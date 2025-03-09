def run():
    from racelights.gunicorn import Application
    Application().run()


def debug():
    import os
    import uvicorn
    os.environ.setdefault("SECRET_KEY", "1")
    uvicorn.run("racelights.app:app", reload=True, port=8000)
