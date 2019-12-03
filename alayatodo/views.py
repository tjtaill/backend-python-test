from alayatodo import app, db
from alayatodo.models import Users, Todos
from http import HTTPStatus
from flask import (
    redirect,
    render_template,
    request,
    session,
    jsonify,
    flash
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
    user = Users.query.filter(Users.username == username, Users.password == password).first()
    if user:
        session['user'] = {'id': user.id, 'username': user.username}
        session['logged_in'] = True
        return redirect('/todos')
    flash('Invalid Credentials')
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
    todo = Todos.query.filter(Todos.id == id).first()
    if not todo:
        return render_template('error.html', error='Todo with provided id not found')

    user_id = session['user']['id']
    if todo.user_id != user_id:
        return render_template('error.html', error='Can not view todo which does not belong to you')
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = Todos.query.filter(Todos.id == id).first()

    if not todo:
        return jsonify({'message': 'No todo with id found'}), HTTPStatus.NOT_FOUND

    user_id = session['user']['id']
    if todo.user_id != user_id:
        return jsonify({'message': 'Can not view todo which does not belong to you'}), HTTPStatus.FORBIDDEN

    result = {
        'id': todo.id,
        'user_id': todo.user_id,
        'description': todo.description,
        'status': todo.status
    }
    return jsonify(result), HTTPStatus.OK


"""
@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    user = session['user']
    todos = Todos.query.filter(Todos.user_id == user['id']).all()
    return render_template('todos.html', todos=todos)
"""


@app.route('/todos', methods=['GET'])
@app.route('/todos/<int:page>', methods=['GET'])
def todos(page=1):
    if not session.get('logged_in'):
        return redirect('/login')
    user = session['user']
    todos = Todos.query.filter(Todos.user_id == user['id']).paginate(page, per_page=2)
    return render_template('todos.html', todos=todos)

    """
    try:
        users_list = User.query.order_by(
            User.id.desc()
        ).paginate(page, per_page=USERS_PER_PAGE)
    except OperationalError:
        flash("No users in the database.")
        users_list = None

    return render_template(
        'users.html',
        users_list=users_list,
        form=form
    )
"""


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
    if not todo:
        return render_template('error.html', error='Todo with provided id not found')
    user_id = session['user']['id']
    if todo.user_id != user_id:
        return render_template('error.html', error='Can delete a todo that does not belong to you')

    db.session.delete(todo)
    db.session.commit()
    return redirect('/todo')


@app.route('/todo/<id>/done', methods=['POST'])
def todo_done(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = Todos.query.filter(Todos.id == id).first()
    if not todo:
        return render_template('error.html', error='Todo with provided id not found')

    todo.status = 'DONE'
    db.session.commit()
    return redirect('/todo')
