from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'spi-website-secret-key-2026'

# ============ MySQL Config (នៅលើ db-app) ============
DB_CONFIG = {
    'host': '192.168.50.67',
    'user': 'spi_user',
    'password': 'Spi@2026!',
    'database': 'spi_database',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': False
}

# ============ Admin Credentials ============
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '1'


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def get_db():
    return pymysql.connect(**DB_CONFIG)


# ============ Public Routes ============
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admission')
def admission():
    return render_template('admission.html')


@app.route('/programs')
def programs():
    return render_template('programs.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        gender = request.form['gender']
        dob = request.form['dob']
        phone = request.form['phone'].strip()
        email = request.form['email'].strip()
        address = request.form['address'].strip()
        province = request.form['province']
        program = request.form['program']
        high_school = request.form['high_school'].strip()
        grade = request.form['grade']
        scholarship = request.form.get('scholarship', 'no')
        notes = request.form.get('notes', '').strip()

        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO applications 
                    (full_name, gender, dob, phone, email, address, province, program, high_school, grade, scholarship, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (full_name, gender, dob, phone, email, address, province, program, high_school, grade, scholarship, notes))
                conn.commit()
        except Exception as e:
            print(f"Register Error: {e}")
            flash('មានបញ្ហាក្នុងការចុះឈ្មោះ', 'danger')
            return redirect(url_for('register'))
        finally:
            conn.close()

        return redirect(url_for('register_success'))

    return render_template('register.html')


@app.route('/success')
def register_success():
    return render_template('success.html')


# ============ Admin Auth ============
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html', error='Username ឬ Password មិនត្រឹមត្រូវ')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


# ============ Admin Routes ============
@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) AS total FROM applications')
        total = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS pending FROM applications WHERE status = 'pending'")
        pending = cursor.fetchone()['pending']

        cursor.execute("SELECT COUNT(*) AS approved FROM applications WHERE status = 'approved'")
        approved = cursor.fetchone()['approved']

        cursor.execute("SELECT COUNT(*) AS rejected FROM applications WHERE status = 'rejected'")
        rejected = cursor.fetchone()['rejected']

        cursor.execute('SELECT * FROM applications ORDER BY id DESC LIMIT 10')
        recent = cursor.fetchall()
    conn.close()

    return render_template('admin/dashboard.html',
                           total=total, pending=pending,
                           approved=approved, rejected=rejected,
                           recent=recent)


@app.route('/admin/applications')
@admin_required
def admin_applications():
    conn = get_db()
    status_filter = request.args.get('status', 'all')

    with conn.cursor() as cursor:
        if status_filter == 'all':
            cursor.execute('SELECT * FROM applications ORDER BY id DESC')
        else:
            cursor.execute('SELECT * FROM applications WHERE status = %s ORDER BY id DESC',
                           (status_filter,))
        applications = cursor.fetchall()
    conn.close()

    return render_template('admin/applications.html',
                           applications=applications,
                           status_filter=status_filter)


@app.route('/admin/applications/view/<int:id>')
@admin_required
def admin_application_view(id):
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM applications WHERE id = %s', (id,))
        app_data = cursor.fetchone()
    conn.close()

    if not app_data:
        return "Application not found", 404

    return render_template('admin/application_view.html', app=app_data)


@app.route('/admin/applications/status/<int:id>/<status>')
@admin_required
def admin_application_status(id, status):
    if status not in ['pending', 'approved', 'rejected']:
        return "Invalid status", 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE applications SET status = %s WHERE id = %s', (status, id))
            conn.commit()
    finally:
        conn.close()

    return redirect(url_for('admin_applications'))


@app.route('/admin/applications/delete/<int:id>')
@admin_required
def admin_application_delete(id):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM applications WHERE id = %s', (id,))
            conn.commit()
    finally:
        conn.close()

    return redirect(url_for('admin_applications'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345, debug=True)
