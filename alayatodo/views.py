from alayatodo import app, db
from alayatodo.models import Users, Todos
from http import HTTPStatus
from flask import (
    redirect,
    render_template,
    request,
    session,
    jsonify
    )


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')
    """
    dbuser = Users(username=username, password=password)
    db.session.add(dbuser)
    db.session.commit()
    """
    print((username, password))
    user = Users.query.filter(Users.username == username, Users.password == password).first()
    print(user)
    if user:
        session['user'] = {'id': user.id, 'username': user.username}
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = Todos.query.filter(Todos.id == id).first_or_404()
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = Todos.query.filter(Todos.id == id).first()
    if todo:
        result = {
            'id': todo.id,
            'user_id': todo.user_id,
            'description': todo.description,
            'status': todo.status
        }
        return jsonify(result), HTTPStatus.OK
    else:
        return jsonify({'message': 'No todo with id found'}), HTTPStatus.NOT_FOUND


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    user = session['user']
    todos = Todos.query.filter(Todos.user_id == user['id']).all()
    return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    description = request.form.get('description', '')
    if description and description != '':
        user = session['user']
        todo = Todos(user_id=user['id'], description=description)
        db.session.add(todo)
        db.session.commit()
        return redirect('/todo')
    else:
        return render_template('error.html', error='Description can not be empty')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = Todos.query.filter(Todos.id == id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return redirect('/todo')
    else:
        return render_template('error.html', error='Todo with provided id not found')


@app.route('/todo/<id>/done', methods=['POST'])
def todo_done(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = Todos.query.filter(Todos.id == id).first()
    if todo:
        todo.status = 'DONE'
        db.session.commit()
        return redirect('/todo')
    else:
        return render_template('error.html', error='Todo with provided id not found')
