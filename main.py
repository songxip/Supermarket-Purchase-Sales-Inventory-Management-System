from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from datetime import datetime
from db import get_conn

app = Flask(__name__)
app.secret_key = 'My164427'

@app.route('/')
def index():
    return render_template('index.html')

# 管理员登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT admin_password FROM admin_login WHERE admin_username = %s", (username,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            db_password = result[0]
            if isinstance(db_password, bytes):
                db_password = db_password.decode('utf-8').strip()

            if password == db_password:
                session['user_id'] = username
                session['role'] = 'admin'  # 管理员身份
                return jsonify({'success': True, 'username': username})
            else:
                return jsonify({'success': False, 'message': '密码错误'})
        else:
            return jsonify({'success': False, 'message': '用户名不存在'})
        
    return render_template('login.html')

# 销售员工登录
@app.route('/sale_login', methods=['POST'])
def sale_login():
    data = request.get_json()
    sale_employee_id = data.get('sale_employee_id')
    password = data.get('password')

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT sale_employee_password FROM sale_employee_login WHERE sale_employee_id = %s", (sale_employee_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        db_password = result[0] # 数据库里的密码
        # 如果是 bytes，先 decode
        if isinstance(db_password, bytes):
            db_password = db_password.decode('utf-8').strip()

        if password == db_password:  # 初始密码
            session['user_id'] = sale_employee_id
            session['role'] = 'sale'  # 销售员身份
            return jsonify({'success': True, 'sale_employee_id': sale_employee_id})
        else:
            return jsonify({'success': False, 'message': '密码错误'})
    else:
        return jsonify({'success': False, 'message': '员工编号不存在'})

# 采购员工登录
@app.route('/purchase_login', methods=['POST'])
def purchase_login():
    data = request.get_json()
    purchase_employee_id = data.get('purchase_employee_id')
    password = data.get('password')

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT purchase_employee_password FROM purchase_employee_login WHERE purchase_employee_id = %s", (purchase_employee_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        db_password = result[0] # 数据库里的密码
        # 如果是 bytes，先 decode
        if isinstance(db_password, bytes):
            db_password = db_password.decode('utf-8').strip()

        if password == db_password:  # 初始密码
            session['user_id'] = purchase_employee_id
            session['role'] = 'purchase'
            return jsonify({'success': True, 'purchase_employee_id': purchase_employee_id})
        else:
            return jsonify({'success': False, 'message': '密码错误'})
    else:
        return jsonify({'success': False, 'message': '员工编号不存在'})

# 个人中心
@app.route('/profile')
def profile():
    return render_template('profile.html')

# 管理员管理
@app.route('/admin_manage')
def admin_manage():
    return render_template('admin_manage.html')

@app.route('/product_manage')
def product_manage():
    return render_template('product_manage.html')

@app.route('/sale_employee_manage')
def sale_employee_manage():
    return render_template('sale_employee_manage.html')

@app.route('/sale_manage')
def sale_manage():
    return render_template('sale_manage.html')

@app.route('/purchase_employee_manage')
def purchase_employee_manage():
    return render_template('purchase_employee_manage.html')

@app.route('/purchase_manage')
def purchase_manage():
    return render_template('purchase_manage.html')

@app.route('/inventory_view')
def inventory_view():
    return render_template('inventory_view.html')

@app.route('/sale_report')
def sale_report():
    return render_template('sale_report.html')

@app.route('/purchase_report')
def purchase_report():
    return render_template('purchase_report.html')

# 查询销售员工列表
@app.route('/api/sale_employees', methods=['GET'])
def get_sale_employees():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sale_employee")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    result = []
    for row in rows:
        row_dict = {}
        for col, val in zip(columns, row):
            # 将 bytes 类型解码成字符串
            if isinstance(val, bytes):
                val = val.decode("utf-8", errors="ignore")
            row_dict[col] = val
        result.append(row_dict)

    cur.close()
    conn.close()
    return jsonify(result)

# 添加销售员工
@app.route('/api/sale_employees', methods=['POST'])
def add_sale_employee():
    data = request.json
    conn = get_conn()
    cur = conn.cursor()

    try:
        # 插入 sale_employee 表
        cur.execute("""
            INSERT INTO sale_employee 
            (sale_employee_id, sale_employee_name, sale_employee_gender, sale_employee_age, 
             sale_employee_phone, sale_employee_hire_date, sale_employee_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['sale_employee_id'], data['sale_employee_name'], data['sale_employee_gender'],
            data['sale_employee_age'], data['sale_employee_phone'], data['sale_employee_hire_date'],
            data['sale_employee_status']
        ))
        
        # 同时插入 sale_employee_login 表，默认密码123456
        cur.execute("""
            INSERT INTO sale_employee_login (sale_employee_id, sale_employee_password, sale_employee_register_date)
            VALUES (%s, %s, NOW())
        """, (
            data['sale_employee_id'], '123456'
        ))

        conn.commit()
        return jsonify({"message": "销售员工添加成功"})
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"销售员工添加失败: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()

# 更新销售员工
@app.route('/api/sale_employees/<string:emp_id>', methods=['PUT'])
def update_sale_employee(emp_id):
    data = request.json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE sale_employee SET 
            sale_employee_name = %s,
            sale_employee_gender = %s,
            sale_employee_age = %s,
            sale_employee_phone = %s,
            sale_employee_hire_date = %s,
            sale_employee_status = %s
        WHERE sale_employee_id = %s
    """, (
        data['sale_employee_name'], data['sale_employee_gender'], data['sale_employee_age'],
        data['sale_employee_phone'], data['sale_employee_hire_date'], data['sale_employee_status'],
        emp_id
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "销售员工更新成功"})

# 删除销售员工
@app.route('/api/sale_employees/<string:emp_id>', methods=['DELETE'])
def delete_sale_employee(emp_id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # 删除 sale_employee 表
        cur.execute("DELETE FROM sale_employee WHERE sale_employee_id = %s", (emp_id,))
        
        # 删除 sale_employee_login_k 表
        cur.execute("DELETE FROM sale_employee_login WHERE sale_employee_id = %s", (emp_id,))
        
        conn.commit()
        return jsonify({"message": "销售员工删除成功"})
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"销售员工删除失败: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()

# 查询采购员工列表
@app.route('/api/purchase_employees', methods=['GET'])
def get_purchase_employees():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM purchase_employee")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    result = []
    for row in rows:
        row_dict = {}
        for col, val in zip(columns, row):
            # 将 bytes 类型解码成字符串
            if isinstance(val, bytes):
                val = val.decode("utf-8", errors="ignore")
            row_dict[col] = val
        result.append(row_dict)

    cur.close()
    conn.close()
    return jsonify(result)

# 添加采购员工
@app.route('/api/purchase_employees', methods=['POST'])
def add_purchase_employee():
    data = request.json
    conn = get_conn()
    cur = conn.cursor()
    try:
        # 插入 purchase_employee 表
        cur.execute("""
            INSERT INTO purchase_employee 
            (purchase_employee_id, purchase_employee_name, purchase_employee_gender, purchase_employee_age, 
             purchase_employee_phone, purchase_employee_hire_date, purchase_employee_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['purchase_employee_id'], data['purchase_employee_name'], data['purchase_employee_gender'],
            data['purchase_employee_age'], data['purchase_employee_phone'], data['purchase_employee_hire_date'],
            data['purchase_employee_status']
        ))
        
        # 同时插入 purchase_employee_login 表，默认密码123456
        cur.execute("""
            INSERT INTO purchase_employee_login (purchase_employee_id, purchase_employee_password, purchase_employee_register_date)
            VALUES (%s, %s, NOW())
        """, (
            data['purchase_employee_id'], '123456'
        ))

        conn.commit()
        return jsonify({"message": "采购员工添加成功"})
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"采购员工添加失败: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()

# 更新采购员工
@app.route('/api/purchase_employees/<string:emp_id>', methods=['PUT'])
def update_purchase_employee(emp_id):
    data = request.json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE purchase_employee SET 
            purchase_employee_name = %s,
            purchase_employee_gender = %s,
            purchase_employee_age = %s,
            purchase_employee_phone = %s,
            purchase_employee_hire_date = %s,
            purchase_employee_status = %s
        WHERE purchase_employee_id = %s
    """, (
        data['purchase_employee_name'], data['purchase_employee_gender'], data['purchase_employee_age'],
        data['purchase_employee_phone'], data['purchase_employee_hire_date'], data['purchase_employee_status'],
        emp_id
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "采购员工更新成功"})

# 删除采购员工
@app.route('/api/purchase_employees/<string:emp_id>', methods=['DELETE'])
def delete_purchase_employee(emp_id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # 删除 purchase_employee 表
        cur.execute("DELETE FROM purchase_employee WHERE purchase_employee_id = %s", (emp_id,))
        
        # 删除 purchase_employee_login_k 表
        cur.execute("DELETE FROM purchase_employee_login WHERE purchase_employee_id = %s", (emp_id,))
        
        conn.commit()
        return jsonify({"message": "采购员工删除成功"})
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"采购员工删除失败: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()

# 员工密码修改
@app.route('/api/change_password', methods=['POST'])
def change_password():
    # 先验证是否登录
    if 'user_id' not in session or 'role' not in session:
        return jsonify({'success': False, 'message': '未登录或会话超时，请重新登录'}), 401

    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'success': False, 'message': '参数不完整'}), 400

    user_id = session['user_id']
    role = session['role']  # 'sale' 或 'purchase' 或 'admin'
    
    # 选择表名和字段
    if role == 'sale':
        table_name = 'sale_employee_login'
        id_field = 'sale_employee_id'
        password_field = 'sale_employee_password'
    elif role == 'purchase':
        table_name = 'purchase_employee_login'
        id_field = 'purchase_employee_id'
        password_field = 'purchase_employee_password'
    elif role == 'admin':
        table_name = 'admin_login'
        id_field = 'admin_username'
        password_field = 'admin_password'
    else:
        return jsonify({'success': False, 'message': '未知身份'}), 400

    conn = get_conn()
    cur = conn.cursor()

    # 查询数据库中的原密码
    cur.execute(f"SELECT {password_field} FROM {table_name} WHERE {id_field} = %s", (user_id,))
    result = cur.fetchone()

    if not result:
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    db_password = result[0]
    if isinstance(db_password, bytes):
        db_password = db_password.decode('utf-8').strip()

    if db_password != old_password:
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': '原密码错误'}), 400

    # 更新密码
    cur.execute(f"UPDATE {table_name} SET {password_field} = %s WHERE {id_field} = %s", (new_password, user_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'success': True, 'message': '密码修改成功'})

# === 查询所有商品 ===
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM product ORDER BY product_id")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    products = []
    for row in rows:
        row_dict = {}
        for col, val in zip(columns, row):
            if isinstance(val, bytes):
                val = val.decode("utf-8", errors="ignore")
            row_dict[col] = val
        products.append(row_dict)

    cur.close()
    conn.close()
    return jsonify(products)

# === 新增商品 ===
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO product (product_id, product_name, product_category, sale_unit_price, product_stock_quantity, product_status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['product_id'],
        data['product_name'],
        data['product_category'],
        float(data['sale_unit_price']),
        int(data['product_stock_quantity']),
        data['product_status'] == 'true'  # 字符串转 bool
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "添加成功"}), 201

# === 修改商品 ===
@app.route('/api/products/<string:pid>', methods=['PUT'])
def update_product(pid):
    data = request.json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE product
        SET product_name=%s,
            product_category=%s,
            sale_unit_price=%s,
            product_stock_quantity=%s,
            product_status=%s
        WHERE product_id=%s
    """, (
        data['product_name'],
        data['product_category'],
        float(data['sale_unit_price']),
        int(data['product_stock_quantity']),
        data['product_status'] == 'true',
        pid
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "修改成功"})

# === 删除商品 ===
@app.route('/api/products/<string:pid>', methods=['DELETE'])
def delete_product(pid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM product WHERE product_id=%s", (pid,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "删除成功"})

# === 查询商品 ===
@app.route('/api/products', methods=['GET'])
def get_all_products():  # 改名，避免与已有的 get_products 冲突
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            product_id, 
            product_name, 
            product_category, 
            sale_unit_price, 
            product_stock_quantity, 
            product_status
        FROM product
    """)
    
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    products = [dict(zip(columns, row)) for row in rows]

    cur.close()
    conn.close()

    return jsonify(products)

# 获取所有销售记录
@app.route('/api/sales', methods=['GET'])
def get_sales():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sale ORDER BY sale_date DESC")
    rows = cur.fetchall()
    sales = []
    for row in rows:
        sales.append({
            'sale_id': row[0].decode('utf-8') if isinstance(row[0], bytes) else row[0],
            'product_id': row[1].decode('utf-8') if isinstance(row[1], bytes) else row[1],
            'sale_quantity': row[2],
            'sale_unit_price': float(row[3]),
            'sale_total_price': float(row[4]),
            'customer_id': row[5].decode('utf-8') if isinstance(row[5], bytes) else row[5],
            'sale_employee_id': row[6].decode('utf-8') if isinstance(row[5], bytes) else row[6],
            'sale_date': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None
        })
    cur.close()
    conn.close()
    return jsonify(sales)

# 添加销售记录
@app.route('/api/sales', methods=['POST'])
def add_sale():
    data = request.get_json()
    conn = get_conn()
    cur = conn.cursor()

    try:
        sale_id = f"S{int(datetime.now().timestamp())}"
        product_id = data['product_id']
        sale_quantity = int(data['sale_quantity'])
        sale_unit_price = float(data['sale_unit_price'])
        sale_total_price = round(sale_quantity * sale_unit_price, 2)
        customer_id = data['customer_id']
        sale_employee_id = data['sale_employee_id']
        sale_date = data['sale_date']

        # 验证 product_id 是否存在，并检查商品是否上架
        cur.execute("SELECT product_status, product_stock_quantity FROM product WHERE product_id = %s", (product_id,))
        product_info = cur.fetchone()
        if not product_info:
            return jsonify({'error': '商品ID不存在'}), 400

        product_status, stock_quantity = product_info
        if not product_status:
            return jsonify({'error': '商品已下架！'}), 400

        # 验证 sale_employee_id 是否存在
        cur.execute("SELECT 1 FROM sale_employee WHERE sale_employee_id = %s", (sale_employee_id,))
        if not cur.fetchone():
            return jsonify({'error': '销售员工ID不存在'}), 400

        # 获取当前库存并判断是否足够
        cur.execute("SELECT product_stock_quantity FROM product WHERE product_id = %s", (product_id,))
        stock = cur.fetchone()
        if not stock or stock[0] < sale_quantity:
            return jsonify({'error': '库存不足，无法完成销售'}), 400

        # 插入销售记录
        cur.execute("""
            INSERT INTO sale (sale_id, product_id, sale_quantity, sale_unit_price, sale_total_price, customer_id, sale_employee_id, sale_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (sale_id, product_id, sale_quantity, sale_unit_price, sale_total_price, customer_id, sale_employee_id, sale_date))

        # 更新库存
        cur.execute("""
            UPDATE product SET product_stock_quantity = product_stock_quantity - %s WHERE product_id = %s
        """, (sale_quantity, product_id))

        conn.commit()
        return jsonify({'message': '销售记录添加成功'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cur.close()
        conn.close()

# 删除销售记录
@app.route('/api/sales/<sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    conn = get_conn()
    cur = conn.cursor()

    # 查找记录以恢复库存
    cur.execute("SELECT product_id, sale_quantity FROM sale WHERE sale_id = %s", (sale_id,))
    row = cur.fetchone()
    if row:
        product_id, quantity = row
        # 如果 product_id 是 bytes 类型，先解码
        if isinstance(product_id, bytes):
            product_id = product_id.decode('utf-8')

        cur.execute("UPDATE product SET product_stock_quantity = product_stock_quantity + %s WHERE product_id = %s", (quantity, product_id))

    cur.execute("DELETE FROM sale WHERE sale_id = %s", (sale_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': '销售记录删除成功'})

# 获取所有采购记录
@app.route('/api/purchases', methods=['GET'])
def get_purchases():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM purchase ORDER BY purchase_date DESC")
    rows = cur.fetchall()
    purchases = []
    for row in rows:
        purchases.append({
            'purchase_id': row[0].decode('utf-8') if isinstance(row[0], bytes) else row[0],
            'product_id': row[1].decode('utf-8') if isinstance(row[1], bytes) else row[1],
            'purchase_quantity': row[2],
            'purchase_unit_price': float(row[3]),
            'purchase_total_price': float(row[4]),
            'supplier_id': row[5].decode('utf-8') if isinstance(row[5], bytes) else row[5],
            'purchase_employee_id': row[6].decode('utf-8') if isinstance(row[6], bytes) else row[6],
            'purchase_date': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None
        })
    cur.close()
    conn.close()
    return jsonify(purchases)

# 添加采购记录
@app.route('/api/purchases', methods=['POST'])
def add_purchase():
    data = request.get_json()
    conn = get_conn()
    cur = conn.cursor()

    try:
        purchase_id = f"P{int(datetime.now().timestamp())}"
        product_id = data['product_id']
        purchase_quantity = int(data['purchase_quantity'])
        purchase_unit_price = float(data['purchase_unit_price'])
        purchase_total_price = round(purchase_quantity * purchase_unit_price, 2)
        supplier_id = data.get('supplier_id')  # 供应商ID从请求中获取
        purchase_employee_id = data['purchase_employee_id']
        purchase_date = data['purchase_date']

        # 验证商品是否存在
        cur.execute("SELECT 1 FROM product WHERE product_id = %s", (product_id,))
        if not cur.fetchone():
            return jsonify({'error': '商品ID不存在'}), 400

        # 验证采购员工是否存在
        cur.execute("SELECT 1 FROM purchase_employee WHERE purchase_employee_id = %s", (purchase_employee_id,))
        if not cur.fetchone():
            return jsonify({'error': '采购员工ID不存在'}), 400

        # 插入采购记录，字段顺序和表顺序一致
        cur.execute("""
            INSERT INTO purchase (
                purchase_id,
                product_id,
                purchase_quantity,
                purchase_unit_price,
                purchase_total_price,
                supplier_id,
                purchase_employee_id,
                purchase_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            purchase_id,
            product_id,
            purchase_quantity,
            purchase_unit_price,
            purchase_total_price,
            supplier_id,
            purchase_employee_id,
            purchase_date
        ))

        # 更新库存
        cur.execute("""
            UPDATE product SET product_stock_quantity = product_stock_quantity + %s WHERE product_id = %s
        """, (purchase_quantity, product_id))

        conn.commit()
        return jsonify({'message': '采购记录添加成功'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cur.close()
        conn.close()

# 删除采购记录
@app.route('/api/purchases/<purchase_id>', methods=['DELETE'])
def delete_purchase(purchase_id):
    conn = get_conn()
    cur = conn.cursor()

    # 查找记录以回退库存
    cur.execute("SELECT product_id, purchase_quantity FROM purchase WHERE purchase_id = %s", (purchase_id,))
    row = cur.fetchone()
    if row:
        product_id, quantity = row
        if isinstance(product_id, bytes):
            product_id = product_id.decode('utf-8')

        cur.execute("UPDATE product SET product_stock_quantity = product_stock_quantity - %s WHERE product_id = %s", (quantity, product_id))

    cur.execute("DELETE FROM purchase WHERE purchase_id = %s", (purchase_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': '采购记录删除成功'})

if __name__ == '__main__':
    app.run(debug=True)
