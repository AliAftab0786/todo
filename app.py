from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

class tasks(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

@app.route('/')
def index():
    try:
        all_tasks = tasks.query.all()
        return render_template('index.html', tasks=all_tasks)
    except Exception as e:
        logging.error(f"Error fetching tasks: {e}")
        return "Internal Server Error", 500

@app.route('/add', methods=['POST'])
def add():
    try:
        task_name = request.form['name']
        description = request.form['description']
        due_date_str = request.form['due_date']
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        new_task = tasks(task_name=task_name, description=description, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error adding task: {e}")
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
        logging.error(f"Error deleting task: {e}")
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
        logging.error(f"Error editing task: {e}")
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
        logging.error(f"Error updating task: {e}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
