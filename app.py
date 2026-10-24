from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'my_test_database.db')


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
    db = get_db()
    search = request.args.get('search', '').strip()

    if search:
        products = db.execute(
            'SELECT * FROM products WHERE model LIKE ? ORDER BY year DESC',
            (f'%{search}%',)
        ).fetchall()
    else:
        products = db.execute('SELECT * FROM products ORDER BY year DESC').fetchall()

    featured = db.execute('SELECT * FROM products WHERE featured = 1 ORDER BY year DESC LIMIT 3').fetchall()
    total_products = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]

    return render_template('index.html',
                           products=products,
                           featured=featured,
                           total_products=total_products,
                           search=search)


@app.route('/product/<int:id>')
def product_detail(id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if not product:
        return "Product not found", 404
    return render_template('product_detail.html', product=product)


@app.route('/order/<int:product_id>', methods=['GET', 'POST'])
def order(product_id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        return "Product not found", 404

    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        quantity = int(request.form.get('quantity', 1))
        total_price = product['price'] * quantity

        db.execute(
            '''INSERT INTO orders (product_id, customer_name, customer_email, customer_phone, address, quantity, total_price) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (product_id, name, email, phone, address, quantity, total_price)
        )
        # បន្ថយ stock
        db.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (quantity, product_id))
        db.commit()
        return redirect(url_for('order_success'))

    return render_template('order.html', product=product)


@app.route('/success')
def order_success():
    return render_template('success.html')


# ============ ADMIN ROUTES ============
@app.route('/admin')
def admin_dashboard():
    db = get_db()
    total_products = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    total_orders = db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    pending = db.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'").fetchone()[0]
    revenue = db.execute("SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status != 'cancelled'").fetchone()[0]

    recent_orders = db.execute('''
        SELECT o.*, p.model as product_name 
        FROM orders o 
        JOIN products p ON o.product_id = p.id 
        ORDER BY o.id DESC 
        LIMIT 10
    ''').fetchall()

    return render_template('admin/dashboard.html',
                           total_products=total_products,
                           total_orders=total_orders,
                           pending=pending,
                           revenue=revenue,
                           recent_orders=recent_orders)


@app.route('/admin/products')
def admin_products():
    db = get_db()
    products = db.execute('SELECT * FROM products ORDER BY year DESC').fetchall()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/add', methods=['GET', 'POST'])
def admin_product_add():
    if request.method == 'POST':
        model = request.form['model'].strip()
        storage = request.form['storage'].strip()
        color = request.form.get('color', '').strip()
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        year = int(request.form.get('year', 2026))
        description = request.form.get('description', '').strip()
        featured = 1 if request.form.get('featured') else 0

        db = get_db()
        db.execute(
            '''INSERT INTO products (model, storage, color, price, stock, year, description, featured) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (model, storage, color, price, stock, year, description, featured)
        )
        db.commit()
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', product=None)


@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
def admin_product_edit(id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if not product:
        return "Product not found", 404

    if request.method == 'POST':
        model = request.form['model'].strip()
        storage = request.form['storage'].strip()
        color = request.form.get('color', '').strip()
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        year = int(request.form.get('year', 2026))
        description = request.form.get('description', '').strip()
        featured = 1 if request.form.get('featured') else 0

        db.execute(
            '''UPDATE products SET model = ?, storage = ?, color = ?, price = ?, stock = ?, year = ?, description = ?, featured = ? 
               WHERE id = ?''',
            (model, storage, color, price, stock, year, description, featured, id)
        )
        db.commit()
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', product=product)


@app.route('/admin/products/delete/<int:id>')
def admin_product_delete(id):
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('admin_products'))


@app.route('/admin/orders')
def admin_orders():
    db = get_db()
    orders = db.execute('''
        SELECT o.*, p.model as product_name
        FROM orders o 
        JOIN products p ON o.product_id = p.id 
        ORDER BY o.id DESC
    ''').fetchall()
    return render_template('admin/orders.html', orders=orders)


@app.route('/admin/orders/status/<int:id>/<status>')
def admin_order_status(id, status):
    if status not in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        return "Invalid status", 400
    db = get_db()
    db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, id))
    db.commit()
    return redirect(url_for('admin_orders'))


@app.route('/admin/orders/delete/<int:id>')
def admin_order_delete(id):
    db = get_db()
    db.execute('DELETE FROM orders WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('admin_orders'))


# ============ SHORTCUT ROUTES ============
@app.route('/add')
def add_shortcut():
    return redirect(url_for('admin_product_add'))


@app.route('/products')
def products_shortcut():
    return redirect(url_for('admin_products'))


@app.route('/orders')
def orders_shortcut():
    return redirect(url_for('admin_orders'))


@app.route('/dashboard')
def dashboard_shortcut():
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)