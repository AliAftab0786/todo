from flask import Flask, request, jsonify , render_template , redirect , url_for 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__ , template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/todo'
db = SQLAlchemy(app)

class tasks(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

@app.route('/')
def index():
    return render_template('index.html' , tasks = tasks.query.all())

@app.route('/add', methods=['POST'])
def add():
    task_name = request.form['name']
    description = request.form['description']
    due_date = request.form['due_date']
    new_task = tasks(task_name=task_name, description=description , due_date=due_date)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))
@app.route('/delete', methods=['POST'])
def delete_task():
    if request.form['_method'] == 'DELETE':
        task_id = request.form['task_id']
        task = tasks.query.filter_by(task_id=task_id).first()
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))
@app.route('/edit/<int:task_id>', methods=['GET'])
def edit_task(task_id):
    task = tasks.query.filter_by(task_id=task_id).first()
    if task:
        return render_template('edit.html', task=task)
    else:
        return redirect(url_for('index'))
@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task = tasks.query.filter_by(task_id=task_id).first()
    if task:
        task.task_name = request.form['task_name']
        task.description = request.form['description']
        task.due_date = request.form['due_date']
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False , host='0.0.0.0')