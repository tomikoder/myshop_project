from celery import Celery

app = Celery('tasks', broker='memory://localhost:8000')

@app.task
def add(x, y):
    return x + y