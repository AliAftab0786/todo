from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import os

app = Flask(__name__, template_folder='templates')

# Use an absolute path for the SQLite database
db_path = os.path.join(os.getcwd(), "todo.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class tasks(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)

@app.before_request
def setup():
    try:
        if not os.path.exists(db_path):
            db.create_all()
            logger.debug("Database created at: %s", db_path)
        else:
            logger.debug("Database already exists at: %s", db_path)
    except Exception as e:
        logger.error(f"Error during database setup: {e}")

@app.route('/')
def index():
    try:
        # Dummy data for testing
        task_id = 1
        task_name = "Sample Task"
        description = "This is a sample description."
        due_date_str = "2024-10-27"  # Correct date format: YYYY-MM-DD
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        
        # Check if the task already exists to prevent duplicate entries
        if not tasks.query.filter_by(task_id=task_id).first():
            new_task = tasks(task_id=task_id, task_name=task_name, description=description, due_date=due_date)
            db.session.add(new_task)
            db.session.commit()
        
        # Fetch all tasks
        all_tasks = tasks.query.all()
        return render_template('index.html', tasks=all_tasks)
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        return "Internal Server Error", 500

@app.route('/add', methods=['POST'])
def add():
    try:
        task_name = request.form['name']
        description = request.form['description']
        due_date_str = request.form['due_date']
        
        # Debugging prints (remove in production)
        print(f"task_name: {task_name}")
        print(f"description: {description}")
        print(f"due_date_str: {due_date_str}")

        # Parse due_date
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        
        # Create new task
        new_task = tasks(task_name=task_name, description=description, due_date=due_date)
        
        # Add and commit to database
        db.session.add(new_task)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        # Debugging prints (remove in production)
        print(f"Exception: {e}")
        return "Internal Server Error", 500

@app.route('/delete', methods=['POST'])
def delete_task():
    try:
        if request.form['_method'] == 'DELETE':
            task_id = request.form['task_id']
            task = tasks.query.filter_by(task_id=task_id).first()
            db.session.delete(task)
            db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return "Internal Server Error", 500

@app.route('/edit/<int:task_id>', methods=['GET'])
def edit_task(task_id):
    try:
        task = tasks.query.filter_by(task_id=task_id).first()
        if task:
            return render_template('edit.html', task=task)
        else:
            return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error editing task: {e}")
        return "Internal Server Error", 500

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    try:
        task = tasks.query.filter_by(task_id=task_id).first()
        if task:
            task.task_name = request.form['task_name']
            task.description = request.form['description']
            due_date_str = request.form['due_date']
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
