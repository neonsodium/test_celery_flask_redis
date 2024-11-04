from flask import Flask, jsonify, request
from celery import Celery
import time

# Create Flask application
app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Define a Celery task
@celery.task
def long_running_task(n):
    time.sleep(n)  # Simulate a long task
    return f'Task completed after {n} seconds.'

# Define a route to start the task
@app.route('/start-task', methods=['POST'])
def start_task():
    data = request.json
    seconds = data.get('seconds', 5)
    task = long_running_task.delay(seconds)  # Start the task
    return jsonify({"task_id": task.id}), 202  # Return task ID

# Define a route to check the task status
@app.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = long_running_task.AsyncResult(task_id)  # Get task result
    return jsonify({"task_id": task_id, "status": task.status, "result": task.result})

if __name__ == '__main__':
    app.run(debug=True)
