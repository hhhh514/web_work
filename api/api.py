from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select
from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import pymysql
import json
import pymysql.cursors
from flask_cors import CORS
import secrets
from datetime import datetime, timezone, timedelta
import logging
from flask import g
from collections import OrderedDict
from sqlalchemy.orm import joinedload
MAX_TRACKED_IPS = 100  
FAILURE_TTL = timedelta(minutes=30)

def utcnow():
    return datetime.now(timezone.utc)
def utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)
app = Flask(__name__)
CORS(app, supports_credentials=True)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
info_handler = logging.FileHandler(
    "login_failures.log",
    encoding="utf-8"
)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)
warning_handler = logging.FileHandler(
    "auth_failures.log",
    encoding="utf-8"
)
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(formatter)
error_handler = logging.FileHandler(
    "system_errors.log",
    encoding="utf-8"
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
logger.addHandler(info_handler)
logger.addHandler(warning_handler)
logger.addHandler(error_handler)
logging.getLogger("werkzeug").setLevel(logging.ERROR)
login_failures = OrderedDict()
def cleanup_login_failures(now):
    expired_ips = []
    for ip, info in login_failures.items():
        lock_until = info.get('lock_until')
        if lock_until and now > lock_until + FAILURE_TTL:
            expired_ips.append(ip)

    for ip in expired_ips:
        login_failures.pop(ip, None)

    # 超過上限就從最舊的刪
    while len(login_failures) > MAX_TRACKED_IPS:
        login_failures.popitem(last=False)
TOKEN_EXPIRE_HOURS = 2
def generate_token(user_id, role):
    token = secrets.token_urlsafe(32)
    expires_at = (utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)).replace(tzinfo=None)

    auth_token = AuthToken(
        token=token,
        user_id=user_id,
        role=role,
        expires_at=expires_at
    )
    db.session.add(auth_token)
    db.session.commit()
    return token


def verify_token(token: str):
    auth = AuthToken.query.filter_by(token=token).first()
    if not auth:
        return None

    expires_at = auth.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        return None

    return auth
@app.before_request
def check_token():
    if request.path in ['/login', '/register']:
        return None

    if request.method == 'OPTIONS':
        return None

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        ip = request.remote_addr
        logging.warning(f"IP {ip} 嘗試訪問 {request.path} 時缺少或無效 token")
        return jsonify({'error': 'Missing or invalid token'}), 401

    token = auth_header.split(' ')[1]
    try:
        auth = verify_token(token)
    except Exception as e:
        logging.error(f"DB error while verifying token: {e}")
        return jsonify({'error': 'Service temporarily unavailable'}), 503
    if not auth:
        ip = request.remote_addr
        logging.warning(f"IP {ip} 嘗試使用無效或過期 token: {token} 訪問 {request.path}")
        return jsonify({'error': 'Invalid or expired token'}), 401

    # 驗證成功
    g.user_id = auth.user_id
    g.role = auth.role

with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

db_cfg = config['db']
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{db_cfg['username']}:{db_cfg['password']}"
    f"@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['database']}?charset={db_cfg['charset']}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['sqlalchemy']['track_modifications']
db = SQLAlchemy(app)
# 資料庫模型
class AuthToken(db.Model):
    __tablename__ = 'auth_token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)

    user_id = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(20), nullable=False) 

    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow_naive)
class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(50))
    product_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.seller_id'))
    discount = db.Column(db.DECIMAL(5,2))
    seller = db.relationship('Seller', backref='products')
    cart_items = db.relationship('CartItem', backref='product')
    order_items = db.relationship('OrderItem', back_populates='product')
    wishlist_items = db.relationship('WishlistItem', backref='product')
    reviews = db.relationship('Review', backref='product')
    sales_summaries = db.relationship('SalesSummary', backref='product')

class Seller(db.Model):
    __tablename__ = 'seller'
    seller_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, default=0)
    account = db.Column(db.String(50))
    password = db.Column(db.String(255))
    orders = db.relationship('OrderItem', backref='seller')
    sales_summaries = db.relationship('SalesSummary', backref='seller')

class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    account = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    carts = db.relationship('Cart', backref='customer')
    orders = db.relationship('OrderTable', backref='customer')
    reviews = db.relationship('Review', backref='customer')
    wishlists = db.relationship('Wishlist', backref='customer')

class OrderTable(db.Model):
    __tablename__ = 'order_table'
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_table.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.seller_id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    product = db.relationship('Product', back_populates='order_items')
    
class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer, primary_key=True)
    budget = db.Column(db.DECIMAL(10, 2))
    name = db.Column(db.String(255))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    created_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
    is_category = db.Column(db.Boolean, default=False)
    cart_items = db.relationship(
        'CartItem',
        backref='cart'
    )

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.cart_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)
    

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    wishlist_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    created_date = db.Column(db.DateTime, default=utcnow_naive)
    wishlist_items = db.relationship('WishlistItem', backref='wishlist')

class WishlistItem(db.Model):
    __tablename__ = 'wishlist_item'
    wishlist_item_id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.wishlist_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    add_date = db.Column(db.DateTime, default=utcnow_naive)

class SalesSummary(db.Model):
    __tablename__ = 'sales_summary'
    summary_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.seller_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    total_quantity_sold = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0)
    last_updated = db.Column(db.DateTime, default=utcnow_naive, onupdate=utcnow_naive)

class Review(db.Model):
    __tablename__ = 'review'
    review_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    rating = db.Column(db.Float)
    comment = db.Column(db.Text)
    review_date = db.Column(db.DateTime, default=utcnow_naive)

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True)

class MajorCategories(db.Model):
    __tablename__ = 'majorcategories'
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('product_category.category_id'), primary_key=True)

"""def execute_sql_file(filename):
    connection = pymysql.connect(
        host=db_cfg['host'],
        port=db_cfg['port'],
        user=db_cfg['username'],
        password=db_cfg['password'],
        database=db_cfg['database'],
        charset=db_cfg['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            with open(filename, 'r', encoding='utf-8') as f:
                sql = f.read()
                for statement in sql.split(';'):
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
        connection.commit()
    finally:
        connection.close()"""


def batch_query_results(query, start, end, order_by_column=None):
    total = query.count()
    if start < 0 or end < start:
        return [], total
    if order_by_column:
        query = query.order_by(order_by_column)
    results = query.slice(start, end).all()
    return results, total

@app.route('/products', methods=['GET'])
def get_products():
    start = request.args.get('start', 0, type=int)
    end = request.args.get('end', 20, type=int)
    query = Product.query
    products, total = batch_query_results(query, start, end, Product.product_id)
    return jsonify({
        'products': [{
            'id': p.product_id,
            'name': p.product_name,
            'image_url': f"https://picsum.photos/200/300/?{p.product_name}",
            'price': p.price,
            'stock': p.stock
        } for p in products],
        'total': total
    })
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    reviews = (
        db.session.query(Review, Customer)
        .outerjoin(Customer, Review.customer_id == Customer.customer_id)
        .filter(Review.product_id == id)
        .all()
    )

    return jsonify({
        'product_id': product.product_id,
        'name': product.product_name,
        'description': product.description,
        'image_url': f"https://picsum.photos/200/300/?{product.product_name}",
        'price': product.price,
        'stock': product.stock,
        'discount': float(product.discount) if product.discount else None,
        'reviews': [{
            'review_id': r.review_id,
            'customer_name': c.name if c else 'Unknown',
            'rating': r.rating,
            'comment': r.comment,
            'review_date': r.review_date.isoformat()
        } for r, c in reviews]
    })

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    product = Product(
        product_type=data.get('product_type'),
        product_name=data.get('product_name'),
        description=data.get('description'),
        price=data.get('price'),
        stock=data.get('stock', 0),
        seller_id=data.get('seller_id'),
        discount=data.get('discount')
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created', 'product_id': product.product_id}), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    product.product_type = data.get('product_type', product.product_type)
    product.product_name = data.get('product_name', product.product_name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    product.seller_id = data.get('seller_id', product.seller_id)
    product.discount = data.get('discount', product.discount)
    db.session.commit()
    return jsonify({'message': 'Product updated'})

@app.route('/products/<int:id>/stock', methods=['PATCH'])
def update_product_stock(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    product.stock = data.get('stock', product.stock)
    db.session.commit()
    return jsonify({'message': 'Product stock updated'})

@app.route('/products/<int:id>/discount', methods=['PATCH'])
def update_product_discount(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    product.discount = data.get('discount', product.discount)
    db.session.commit()
    return jsonify({'message': 'Product discount updated'})

@app.route('/products/search', methods=['GET'])
def search_products():
    keyword = request.args.get('keyword')
    start = request.args.get('start', 0, type=int)
    end = request.args.get('end', 20, type=int)
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400
    query = Product.query.filter(Product.product_name.ilike(f'%{keyword}%'))
    products, total = batch_query_results(query, start, end)
    return jsonify({
        'products': [{
            'id': p.product_id,
            'name': p.product_name,
            'image_url': f"https://example.com/images/product{p.product_name}.jpg",
            'price': p.price,
            'stock': p.stock
        } for p in products],
        'total': total
    })
@app.route('/products/by-category', methods=['GET'])
def get_products_by_category():
    category = request.args.get('category')
    start = request.args.get('start', 0, type=int)
    end = request.args.get('end', 20, type=int)
    if not category:
        return jsonify({'error': 'Category is required'}), 400
    
    category = ProductCategory.query.filter_by(category_name=category).first_or_404()
    sub_categories = db.session.query(MajorCategories.product_id).filter(MajorCategories.type_id == category.category_id).all()
    category_names = [str(item[0]) for item in sub_categories]

    total = len(category_names)
    paginated_names = category_names[start:end]

    return jsonify({
        'categories': paginated_names,  
        'total': total
    })
@app.route('/products/seller', methods=['GET'])
def get_products_by_seller():
    products = Product.query.filter_by(seller_id=g.user_id).all()
    result = []
    for product in products:
        result.append({
            'product_id': product.product_id,
            'product_name': product.product_name,
            'product_type': product.product_type,
            'description': product.description,
            'price': float(product.price),
            'stock': product.stock,
            'discount': float(product.discount) if product.discount else 0.0
        })
    return jsonify(result)
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': '找不到商品'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': '商品已刪除'})
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    role = data.get('role')
    account = data.get('account')
    password = data.get('password')

    if role not in ['customer', 'seller']:
        return jsonify({'error': 'Invalid role'}), 400

    if role == 'customer':
        if Customer.query.filter_by(account=account).first():
            return jsonify({'error': 'Account already exists'}), 400
        customer = Customer(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            account=account,
            password=generate_password_hash(password)
        )
        db.session.add(customer)
    else:
        if Seller.query.filter_by(account=account).first():
            return jsonify({'error': 'Account already exists'}), 400
        seller = Seller(
            name=data.get('name'),
            email=data.get('email'),
            account=account,
            password=generate_password_hash(password)
        )
        db.session.add(seller)

    db.session.commit()
    return jsonify({'message': f'{role.capitalize()} registered successfully'})
MAX_LOGIN_ATTEMPTS = 3          
LOCK_TIME_MINUTES = 10 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    role = data.get('role')
    account = data.get('account')
    password = data.get('password')

    ip = request.remote_addr
    now = utcnow() 
    cleanup_login_failures(now)
    info = login_failures.get(ip)
    if info:
        lock_until = info.get('lock_until')

        if lock_until:
        
            if lock_until.tzinfo is None:
                lock_until = lock_until.replace(tzinfo=timezone.utc)

            if now < lock_until:
                remaining = int((lock_until - now).total_seconds())
                logging.warning(
                    f"IP {ip} 被鎖定 {LOCK_TIME_MINUTES} 分鐘，剩餘 {remaining} 秒"
                )
                return jsonify({
                    'error': 'Too many failed attempts',
                    'lock_seconds': remaining
                }), 429
            else:

                login_failures.pop(ip, None)
    if role == 'customer':
        user = Customer.query.filter_by(account=account).first()
        user_id = user.customer_id if user else None
    elif role == 'seller':
        user = Seller.query.filter_by(account=account).first()
        user_id = user.seller_id if user else None
    else:
        return jsonify({'error': 'Invalid role'}), 400

    if not user or not check_password_hash(user.password, password):
        info = login_failures.setdefault(ip, {'count': 0, 'lock_until': None})
        info['count'] += 1

        if info['count'] >= MAX_LOGIN_ATTEMPTS:
            info['lock_until'] = now + timedelta(minutes=LOCK_TIME_MINUTES)
            logging.warning(
                f"IP {ip} 連續 {MAX_LOGIN_ATTEMPTS} 次登入失敗，被鎖定 {LOCK_TIME_MINUTES} 分鐘"
            )

        return jsonify({'error': 'Invalid credentials'}), 401

    login_failures.pop(ip, None)

    token = generate_token(user_id, role)

    return jsonify({
        'message': 'Login successful',
        'role': role,
        'user_id': user_id,
        'token': token,
        'expires_in': TOKEN_EXPIRE_HOURS * 3600
    })
@app.route('/sellers', methods=['GET'])
def get_seller():
    seller = Seller.query.get_or_404(g.user_id)
    return jsonify({
        'seller_id': seller.seller_id,
        'name': seller.name,
        'email': seller.email,
        'rating': seller.rating
    })

@app.route('/sellers', methods=['POST'])
def create_seller():
    data = request.get_json()
    seller = Seller(
        name=data.get('name'),
        email=data.get('email'),
        rating=data.get('rating', 0),
        account=data.get('account'),
        password=data.get('password')
    )
    db.session.add(seller)
    db.session.commit()
    return jsonify({'message': 'Seller created', 'seller_id': seller.seller_id}), 201

@app.route('/sellers/rating', methods=['PATCH'])
def update_seller_rating():
    seller = Seller.query.get_or_404(g.user_id)
    data = request.get_json()
    seller.rating = data.get('rating', seller.rating)
    db.session.commit()
    return jsonify({'message': 'Seller rating updated'})

# 顧客相關 API
@app.route('/customers', methods=['GET'])
def get_customer():
    customer = Customer.query.get_or_404(g.user_id)
    return jsonify({
        'customer_id': customer.customer_id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'address': customer.address
    })
@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    customer = Customer(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Customer created', 'customer_id': customer.customer_id}), 201

@app.route('/customers', methods=['PUT'])
def update_customer():
    customer = Customer.query.get_or_404(Customer, g.user_id)
    data = request.get_json()
    customer.name = data.get('name', customer.name)
    customer.email = data.get('email', customer.email)
    customer.phone = data.get('phone', customer.phone)
    customer.address = data.get('address', customer.address)
    db.session.commit()
    return jsonify({'message': 'Customer updated'})

# 訂單相關 API
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    customer_id = g.user_id
    items = data['items'] 
    total = 0
    order_items = []

    for item in items:
        product = Product.query.get(item['product_id'])
        if not product or product.stock < item['quantity']:
            return jsonify({'error': f"商品 ID {item['product_id']} 庫存不足或不存在"}), 400
        subtotal = product.price * item['quantity']
        total += subtotal
        order_items.append(OrderItem(
            product_id=item['product_id'],
            quantity=item['quantity'],
            subtotal=subtotal,
            seller_id=product.seller_id,
            status='pending'
        ))

    order = OrderTable(
        customer_id=customer_id,
        order_date=datetime.now(),
        total_amount=total,
        items=order_items
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({'message': '訂單建立成功', 'order_id': order.order_id}), 201

@app.route('/orders/customer', methods=['GET'])
def get_customer_orders():
    orders = OrderTable.query.filter_by(customer_id=g.user_id).all()
    result = []
    for order in orders:
        order_data = {
            'order_id': order.order_id,
            'order_date': order.order_date,
            'total_amount': order.total_amount,
            'items': []
        }
        for item in order.items:
            product = Product.query.get(item.product_id)
            order_data['items'].append({
                'order_item_id':item.order_item_id,
                'product_id': item.product_id,
                'product_name': product.product_name if product else "未知商品",
                'quantity': item.quantity,
                'subtotal': item.subtotal,
                'status': item.status
            })
        result.append(order_data)
    return jsonify(result)
@app.route('/orders/seller', methods=['GET'])
def get_seller_orders():
    items = OrderItem.query.filter_by(seller_id=g.user_id).all()
    result = []
    for item in items:
        result.append({
            'order_item_id': item.order_item_id,
            'order_id': item.order_id,
            'product_id': item.product_id,
            'quantity': item.quantity,
            'subtotal': item.subtotal,
            'status': item.status
        })
    return jsonify(result)
@app.route('/orders/item/<int:order_item_id>/status', methods=['PUT'])
def update_status(order_item_id):
    data = request.json
    new_status = data.get('status')
    valid_statuses = ['pending', 'shipped', 'delivered', 'completed']

    if new_status not in valid_statuses:
        return jsonify({'error': '狀態無效'}), 400

    item = OrderItem.query.get(order_item_id)
    if not item:
        return jsonify({'error': '訂單項目不存在'}), 404
    if item.status == 'pending' and new_status == 'shipped':
        product = Product.query.get(item.product_id)
        if product.stock < item.quantity:
            return jsonify({'error': '庫存不足'}), 400
    if item.status != 'completed' and new_status == 'completed':
        product = Product.query.get(item.product_id)
        product.stock -= item.quantity
        summary = SalesSummary.query.filter_by(
            seller_id=item.seller_id,
            product_id=item.product_id
        ).first()
        if not summary:
            summary = SalesSummary(
                seller_id=item.seller_id,
                product_id=item.product_id,
                total_quantity_sold=item.quantity,
                total_revenue=item.subtotal,
                last_updated=datetime.utcnow()
            )
            db.session.add(summary)
        else:
            summary.total_quantity_sold += item.quantity
            summary.total_revenue += item.subtotal
            summary.last_updated = datetime.utcnow()
    item.status = new_status
    db.session.commit()

    return jsonify({'message': '狀態更新成功'})
# 購物車相關 API
@app.route('/carts', methods=['POST'])
def create_cart():
    data = request.get_json()
    customer_id = g.user_id
    if not customer_id:
        return jsonify({'error': 'Customer ID is required'}), 400
    budget = data.get('budget')
    name = data.get('name')
    is_category = 1 if name and name.strip() != "" else 0 
    if is_category == 0:
        name = "default_cart"
        existing_general_cart = Cart.query.filter_by(customer_id=customer_id, is_category=0).first()
        if existing_general_cart:
            return jsonify({'error': 'Customer already has a general cart'}), 400
    elif not name or name.strip() == "":
        return jsonify({'error': 'Name is required for category cart'}), 400

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({'error': 'Customer does not exist'}), 400


    existing_cart = Cart.query.filter_by(customer_id=customer_id, is_category=is_category, name=name).first()
    if existing_cart:
        return jsonify({'message': 'Cart already exists', 'cart_id': existing_cart.cart_id}), 200


    cart = Cart(
        customer_id=customer_id,
        budget=budget,
        name=name,
        created_date=datetime.now(),
        last_updated=datetime.now(),
        is_category=is_category
    )
    db.session.add(cart)
    db.session.commit()
    return jsonify({'message': 'Cart created', 'cart_id': cart.cart_id}), 201

@app.route('/carts/add', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        if not all([g.user_id, product_id, quantity]):
            print( 'Missing fields:', data)
            return jsonify({'error': 'Missing required fields'}), 400
        default_cart = Cart.query.filter_by(
            customer_id=g.user_id,
            is_category=False
        ).first()
        if not default_cart:
            default_cart = Cart(
                budget=0.00,
                name='Default Cart',
                customer_id=g.user_id,
                created_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                is_category=False
            )
            db.session.add(default_cart)
            db.session.commit()
        cart_item = CartItem.query.filter_by(
            cart_id=default_cart.cart_id,
            product_id=product_id
        ).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                cart_id=default_cart.cart_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        db.session.commit()
        return jsonify({
            'message': 'Product added to cart successfully',
            'cart_id': default_cart.cart_id,
            'id': cart_item.id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': "error"}), 500
@app.route('/carts/<int:cart_id>/items', methods=['POST'])
def add_cart_item(cart_id):
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    cart = db.session.get(Cart, cart_id)
    if not cart:
        customer_id = request.args.get('customer_id')
        if not customer_id:
            return jsonify({'error': 'Customer ID is required'}), 400
        customer = db.session.get(Customer, int(customer_id))
        if not customer:
            return jsonify({'error': 'Customer does not exist'}), 400
        cart = Cart(
            customer_id=customer_id,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            name="Default Cart"
        )
        db.session.add(cart)
        db.session.commit()
        if cart.cart_id != cart_id:
            return jsonify({'error': 'Invalid cart ID'}), 400

    cart_item = CartItem(
        cart_id=cart.cart_id,
        product_id=product_id,
        quantity=quantity
    )
    db.session.add(cart_item)
    cart.last_updated = datetime.now()
    db.session.commit()
    return jsonify({'message': 'Item added to cart'}), 201

@app.route('/carts/', methods=['GET'])
def get_cart():
    customer = db.session.get(Customer, g.user_id)
    if not customer:
        return jsonify({'error': 'Customer does not exist'}), 400
    general_cart = Cart.query.filter_by(customer_id=g.user_id, is_category=0).first()
    general_cart_data = None
    if general_cart:
        items = CartItem.query.filter_by(cart_id=general_cart.cart_id).all()
        general_cart_data = {
            'cart_id': general_cart.cart_id,
            'items': [{
                'id': item.id,
                'product_id': item.product_id,
                'product_name': db.session.get(Product, item.product_id).product_name,
                'quantity': item.quantity,
                'price': db.session.get(Product, item.product_id).price
            } for item in items]
        }

    categorized_carts = Cart.query.filter_by(customer_id=g.user_id, is_category=1).all()
    categorized_cart_data = []
    for cart in categorized_carts:
        items = CartItem.query.filter_by(cart_id=cart.cart_id).all()
        categorized_cart_data.append({
            'category_id': cart.cart_id, 
            'name': cart.name,
            'budget': float(cart.budget) if cart.budget else None,
            'items': [{
                'id': item.id,
                'product_id': item.product_id,
                'product_name': db.session.get(Product, item.product_id).product_name,
                'quantity': item.quantity,
                'price': db.session.get(Product, item.product_id).price
            } for item in items]
        })


    response = {}
    if general_cart_data:
        response['cart'] = general_cart_data
    if categorized_cart_data:
        response['cart_category'] = categorized_cart_data

    return jsonify(response)

@app.route('/carts/<int:cart_id>/items/<int:product_id>', methods=['DELETE'])
def remove_cart_item(cart_id, product_id):
    cart_item = CartItem.query.filter_by(cart_id=cart_id, product_id=product_id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'})
@app.route('/carts/<int:cart_id>', methods=['DELETE'])
def delete_cart(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({'error': '購物車不存在'}), 404

    try:
        CartItem.query.filter_by(cart_id=cart_id).delete()
        db.session.delete(cart)
        db.session.commit()
        return jsonify({'message': f'成功刪除購物車與其項目 (ID: {cart_id})'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '刪除過程出錯', 'detail': str(e)}), 500
@app.route('/carts/<int:cart_id>', methods=['PUT'])
def update_cart(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    data = request.get_json()
    if 'name' in data:
        cart.name = data['name']
    if 'budget' in data:
        cart.budget = data['budget']
    db.session.commit()
    return jsonify({'message': 'Cart updated successfully'})

@app.route('/carts/<int:cart_id>/items/<int:item_id>/quantity', methods=['PATCH'])
def update_cart_item_quantity(cart_id, item_id):
    item = CartItem.query.filter_by(cart_id=cart_id, id=item_id).first_or_404()
    data = request.get_json()
    item.quantity = data.get('quantity', item.quantity)
    db.session.commit()
    return jsonify({'message': 'Cart item quantity updated'})

# 願望清單相關 API
@app.route('/wishlists', methods=['GET'])
def get_wishlist():
    wishlist = Wishlist.query.filter_by(customer_id=g.user_id).first_or_404()
    return jsonify({
        'wishlist_id': wishlist.wishlist_id,
        'customer_id': wishlist.customer_id,
        'created_date': wishlist.created_date.isoformat()
    })
@app.route('/wishlists/<int:wishlist_id>/items', methods=['POST'])
@app.route('/wishlists/customer/items', methods=['POST'])
def add_item_by_customer_id():
    data = request.get_json()
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'Missing product_id'}), 400
    wishlist = Wishlist.query.filter_by(customer_id=g.user_id).first()
    if not wishlist:
        wishlist = Wishlist(customer_id=g.user_id)
        db.session.add(wishlist)
        db.session.commit() 
    existing_item = WishlistItem.query.filter_by(
        wishlist_id=wishlist.wishlist_id,
        product_id=product_id
    ).first()

    if existing_item:
        return jsonify({'message': 'Item already in wishlist'}), 409
    wishlist_item = WishlistItem(
        wishlist_id=wishlist.wishlist_id,
        product_id=product_id
    )
    db.session.add(wishlist_item)
    db.session.commit()
    return jsonify({
        'message': 'Item added to wishlist',
        'wishlist_item_id': wishlist_item.wishlist_item_id,
        'wishlist_id': wishlist.wishlist_id
    }), 201

@app.route('/wishlists/<int:wishlist_id>/items/<int:product_id>', methods=['DELETE'])
def remove_wishlist_item(wishlist_id, product_id):
    wishlist_item = WishlistItem.query.filter_by(wishlist_id=wishlist_id, product_id=product_id).first_or_404()
    db.session.delete(wishlist_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from wishlist'})
@app.route('/wishlists/<int:wishlist_id>/items', methods=['GET'])
def get_wishlist_items(wishlist_id):
    items = WishlistItem.query.filter_by(wishlist_id=wishlist_id).all()
    if not items:
        return jsonify([]), 200
    result = []
    for item in items:
        product = item.product
        result.append({
            'wishlist_item_id': item.wishlist_item_id,
            'product_id': product.product_id,
            'product_name': product.product_name,
            'price': float(product.price),
            'add_date': item.add_date.isoformat()
        })
    return jsonify(result), 200
# 銷售總結相關 API
@app.route('/sales-summary/seller', methods=['GET'])
def get_seller_sales_summary():
    summaries = SalesSummary.query.filter_by(seller_id=g.user_id).all()
    return jsonify([{
        'summary_id': s.summary_id,
        'product_id': s.product_id,
        'total_quantity_sold': s.total_quantity_sold,
        'total_revenue': s.total_revenue,
        'last_updated': s.last_updated.isoformat()
    } for s in summaries])

@app.route('/sales-summary/product/<int:product_id>', methods=['GET'])
def get_product_sales_summary(product_id):
    summary = SalesSummary.query.filter_by(product_id=product_id).first_or_404()
    return jsonify({
        'summary_id': summary.summary_id,
        'seller_id': summary.seller_id,
        'product_id': summary.product_id,
        'total_quantity_sold': summary.total_quantity_sold,
        'total_revenue': summary.total_revenue,
        'last_updated': summary.last_updated.isoformat()
    })
# 評論相關 API

@app.route('/reviews', methods=['POST'])
def create_or_update_review():
    data = request.get_json()
    customer_id = g.user_id
    product_id = data.get('product_id')
    rating = float(data.get('rating'))
    comment = data.get('comment')

    if not all([customer_id, product_id, rating, comment]):
        return jsonify({'message': 'Missing required fields'}), 400

    review = Review.query.filter_by(customer_id=customer_id, product_id=product_id).first()
    product = Product.query.get(product_id)
    seller = Seller.query.get(product.seller_id) if product else None

    if not seller:
        return jsonify({'message': 'Seller not found'}), 404

    seller_products = Product.query.with_entities(Product.product_id)\
        .filter_by(seller_id=seller.seller_id).subquery()
    
    review_count = db.session.query(func.count(Review.review_id))\
        .filter(Review.product_id.in_(seller_products))\
        .scalar()

    if review:
      
        all_reviews = db.session.query(Review.rating)\
            .filter(Review.product_id.in_(seller_products))\
            .all()
        total_rating = sum(r[0] if isinstance(r, tuple) else r for r in all_reviews)
        seller.rating = round(total_rating / review_count, 2) if review_count else 0

        review.rating = rating
        review.comment = comment

    else:

        old_avg = seller.rating or 0
        N = review_count
        new_avg = (old_avg * N + rating) / (N + 1)
        seller.rating = round(new_avg, 2)

        review = Review(
            customer_id=customer_id,
            product_id=product_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)

    db.session.commit()

    return jsonify({
        'message': 'Review updated' if review else 'Review created',
        'review_id': review.review_id,
        'seller_rating': seller.rating
    }), 201

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    customer_id = request.args.get('customer_id')
    review = Review.query.filter_by(review_id=review_id, customer_id=customer_id).first_or_404()
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # execute_sql_file('test.sql')
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
