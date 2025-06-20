from celery import Celery

# Configure the Celery app
# The first argument is the name of the current module.
# The `broker` argument specifies the URL of the message broker (Redis).
# The `backend` argument specifies the URL of the result backend (also Redis).
celery_app = Celery(
  "worker",
  broker="redis://localhost:6379/0",
  backend="redis://localhost:6379/0",
)

# Optional configuration
celery_app.conf.update(
    task_track_started=True,
)

# It's good practice to have the task definitions in a separate file (tasks.py)
# This line tells Celery to look for tasks in the 'worker.tasks' module.
celery_app.autodiscover_tasks(['worker.tasks'])