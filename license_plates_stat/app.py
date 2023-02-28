from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    session,
    flash,
    get_flashed_messages,
)
import sqlite3
import datetime
import json
import atexit
import os

from license_plates_stat.scheduler import init_scheduler


app = Flask(__name__)
init_scheduler()

app.config['SECRET_KEY'] = 'weghudvhb9238232'
scheduler_file = 'scheduler.lock'


@atexit.register
def delete_scheduler_file():
    if os.path.exists(scheduler_file):
        os.remove(scheduler_file)


@app.route('/')
def index():
    return render_template(
        '/index.html',
    )


@app.route('/license-plates', methods=['GET', 'POST'])
def show_license_plates():
    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()
    messages = None
    if request.method == 'POST':
        letter_to_add = request.form['letter_to_add']
        cur.execute('INSERT INTO letters (letter) VALUES (?)', (letter_to_add,))
        connection.commit()
        flash('Code has been adeed', 'success')
        messages = get_flashed_messages(with_categories=True)
    letters_data = cur.execute('SELECT letter FROM letters ORDER BY letter').fetchall()
    connection.close()
    letters = list([element[0] for element in letters_data])
    return render_template(
        '/letters.html',
        data=letters,
        messages=messages
    )


@app.route('/code', methods=['GET'])
def go_to_code():
    code = request.args.get('code')
    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()
    code_from_db = cur.execute('SELECT letter FROM letters WHERE letter=?', (code,)).fetchone()
    if not code_from_db:
        flash('Code does not exist', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            '/index.html',
            messages=messages,
            bad_code=code
        ), 422
    session['code'] = code
    return redirect(url_for('show_code', name=code))


@app.route('/code/<name>', methods=['GET'])
def show_code(name):
    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()
    view_data = []
    data_limit = 30
    messages = None

    if request.args.get('ask_date'):
        start_date = request.args['start_date']
        end_date = request.args['end_date']
        page = 1
        letter_id = request.args['letter_id']

        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        except Exception:
            flash('Incorrect date format', 'danger')
            messages = get_flashed_messages(with_categories=True)
            return redirect(url_for('show_code', name=name, messages=messages)), 400

        letter_data = cur.execute('SELECT value, created_at FROM letter_values WHERE letter_id = ? AND created_at >= ? AND created_at <= ?', (letter_id, start_date, end_date)).fetchall()
        data_volume = len(letter_data)
        if data_volume != 0:
            pages = (int(data_volume / data_limit) + 1) if data_volume % data_limit != 0 else data_volume / data_limit
        else:
            pages = 1
        offset = 0
        letter_data = cur.execute('SELECT value, created_at FROM letter_values WHERE letter_id = ? AND created_at >= ? AND created_at <= ? LIMIT ? OFFSET ?', (letter_id, start_date, end_date, data_limit, offset)).fetchall()

    elif request.args.get('change_page'):
        letter_id = request.args['letter_id']
        page = int(request.args['page'])
        pages = int(request.args['end_page'])
        offset = (page - 1) * data_limit
        start_date = request.args['start_date']
        end_date = request.args['end_date']
        letter_data = cur.execute('SELECT value, created_at FROM letter_values WHERE letter_id = ? AND created_at >= ? AND created_at <= ? LIMIT ? OFFSET ?', (letter_id, start_date, end_date, data_limit, offset)).fetchall()

    else:
        page = 1
        (letter_id,) = cur.execute('SELECT id FROM letters WHERE letter = ?', (name,)).fetchone()
        start_date = datetime.datetime.today().date() - datetime.timedelta(days=30)
        end_date = datetime.datetime.today().date()
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        letter_data = cur.execute('SELECT value, created_at FROM letter_values WHERE letter_id = ? AND created_at >= ? AND created_at <= ?', (letter_id, start_date, end_date)).fetchall()
        pages = 1

    for i, elem in enumerate(letter_data):
        value, date = elem
        if i == 0:
            previous_date = datetime.datetime.strptime(letter_data[i][1], '%Y-%m-%d').date() - datetime.timedelta(days=1)
            previous_date_data = cur.execute('SELECT value FROM letter_values WHERE letter_id = ? AND created_at = ?', (letter_id, previous_date)).fetchone()
            if previous_date_data:
                (previous_value,) = previous_date_data
                difference = value - previous_value 
            else:
                difference = 0
        if i > 0:
            difference = value - letter_data[i-1][0]
        view_data.append([value, date, difference])

    graph_dates = list([element[1] for element in view_data])
    graph_values = list([element[0] for element in view_data])

    return render_template(
        '/code.html',
        code=name,
        table_data=view_data,
        letter_id=letter_id,
        page=page,
        messages=messages,
        graph_dates = json.dumps(graph_dates),
        graph_values = json.dumps(graph_values),
        end_page=pages,
        start_date=start_date,
        end_date=end_date,
    )


@app.route('/totaldata', methods=['GET'])
def total_data():
    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()
    view_data = []
    data_limit = 30
    messages = None

    if request.args.get('ask_date'):
        start_date = request.args['start_date']
        end_date = request.args['end_date']
        page = 1

        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        except Exception:
            flash('Incorrect date format', 'danger')
            messages = get_flashed_messages(with_categories=True)
            return redirect(url_for('total_data', messages=messages)), 400

        letter_data = cur.execute('SELECT SUM(value) as total_value, created_at FROM letter_values WHERE created_at >= ? AND created_at <= ? GROUP BY created_at', (start_date, end_date)).fetchall()
        data_volume = len(letter_data)
        if data_volume != 0:
            pages = (int(data_volume / data_limit) + 1) if data_volume % data_limit != 0 else data_volume / data_limit
        else:
            pages = 1
        offset = 0
        letter_data = cur.execute('SELECT SUM(value) as total_value, created_at FROM letter_values WHERE created_at >= ? AND created_at <= ? GROUP BY created_at LIMIT ? OFFSET ?', (start_date, end_date, data_limit, offset)).fetchall()

    elif request.args.get('change_page'):
        page = int(request.args['page'])
        pages = int(request.args['end_page'])
        offset = (page - 1) * data_limit
        start_date = request.args['start_date']
        end_date = request.args['end_date']
        letter_data = cur.execute('SELECT SUM(value) as total_value, created_at FROM letter_values WHERE created_at >= ? AND created_at <= ? GROUP BY created_at LIMIT ? OFFSET ?', (start_date, end_date, data_limit, offset)).fetchall()

    else:
        page = 1
        start_date = datetime.datetime.today().date()
        end_date = datetime.datetime.today().date()
        start_date = start_date.strftime("%Y-%m-%d") - datetime.timedelta(days=30)
        end_date = end_date.strftime("%Y-%m-%d")
        letter_data = cur.execute('SELECT SUM(value) as total_value, created_at FROM letter_values WHERE created_at >= ? AND created_at <= ? GROUP BY created_at', (start_date, end_date)).fetchall()
        pages = 1

    for i, elem in enumerate(letter_data):
        value, date = elem
        if i == 0:
            previous_date = datetime.datetime.strptime(letter_data[i][1], '%Y-%m-%d').date() - datetime.timedelta(days=1)
            previous_date_data = cur.execute('SELECT SUM(value) as total_value FROM letter_values WHERE created_at = ?', (previous_date,)).fetchone()
            (previous_value,) = previous_date_data
            if previous_value:
                difference = value - previous_value 
            else:
                difference = 0
        if i > 0:
            difference = value - letter_data[i-1][0]
        view_data.append([value, date, difference])

    graph_dates = list([element[1] for element in view_data])
    graph_values = list([element[0] for element in view_data])

    return render_template(
        '/total_data.html',
        table_data=view_data,
        page=page,
        messages=messages,
        graph_dates = json.dumps(graph_dates),
        graph_values = json.dumps(graph_values),
        end_page=pages,
        start_date=start_date,
        end_date=end_date,
    )


@app.route('/updateinfo', methods=['GET', 'POST'])
def update_info():
    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()

    upd_data = cur.execute("SELECT * FROM updates ORDER BY id DESC",
    ).fetchall()
    return render_template(
        '/update_info.html',
        upd_data = upd_data,
    )
