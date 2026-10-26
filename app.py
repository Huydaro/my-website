from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'spi_database_from_ubuntu.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# ============ PUBLIC ROUTES ============
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

        db = get_db()
        db.execute('''
            INSERT INTO applications 
            (full_name, gender, dob, phone, email, address, province, program, high_school, grade, scholarship, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (full_name, gender, dob, phone, email, address, province, program, high_school, grade, scholarship, notes))
        db.commit()

        return redirect(url_for('register_success'))

    return render_template('register.html')


@app.route('/success')
def register_success():
    return render_template('success.html')


# ============ ADMIN ROUTES ============
@app.route('/admin')
def admin_dashboard():
    db = get_db()
    total = db.execute('SELECT COUNT(*) FROM applications').fetchone()[0]
    pending = db.execute("SELECT COUNT(*) FROM applications WHERE status = 'pending'").fetchone()[0]
    approved = db.execute("SELECT COUNT(*) FROM applications WHERE status = 'approved'").fetchone()[0]
    rejected = db.execute("SELECT COUNT(*) FROM applications WHERE status = 'rejected'").fetchone()[0]
    recent = db.execute('SELECT * FROM applications ORDER BY id DESC LIMIT 10').fetchall()

    return render_template('admin/dashboard.html',
                           total=total, pending=pending,
                           approved=approved, rejected=rejected,
                           recent=recent)


@app.route('/admin/applications')
def admin_applications():
    db = get_db()
    status_filter = request.args.get('status', 'all')

    if status_filter == 'all':
        applications = db.execute('SELECT * FROM applications ORDER BY id DESC').fetchall()
    else:
        applications = db.execute('SELECT * FROM applications WHERE status = ? ORDER BY id DESC',
                                  (status_filter,)).fetchall()

    return render_template('admin/applications.html',
                           applications=applications,
                           status_filter=status_filter)


@app.route('/admin/applications/view/<int:id>')
def admin_application_view(id):
    db = get_db()
    app_data = db.execute('SELECT * FROM applications WHERE id = ?', (id,)).fetchone()
    if not app_data:
        return "Application not found", 404
    return render_template('admin/application_view.html', app=app_data)


@app.route('/admin/applications/status/<int:id>/<status>')
def admin_application_status(id, status):
    if status not in ['pending', 'approved', 'rejected']:
        return "Invalid status", 400
    db = get_db()
    db.execute('UPDATE applications SET status = ? WHERE id = ?', (status, id))
    db.commit()
    return redirect(url_for('admin_applications'))


@app.route('/admin/applications/delete/<int:id>')
def admin_application_delete(id):
    db = get_db()
    db.execute('DELETE FROM applications WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('admin_applications'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)