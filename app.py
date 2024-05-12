from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify, make_response
from flask_login import UserMixin, login_user, logout_user, current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func,and_
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import secrets
import os
from flask_talisman import Talisman
from dotenv import load_dotenv



import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

app=Flask(__name__,template_folder='templates',static_url_path='/static')
# config = cloudinary.config(secure=True)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
cloudinary.config( 
  cloud_name = "doxj9pjvr", 
  api_key = "629727456658243", 
  api_secret = "xWUK83YdSiZQsmR8GgPxWN8v_2w" 
)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=14)
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
secret_key = secrets.token_hex(16)
app.secret_key = secret_key

login_manager = LoginManager()
login_manager.init_app(app)
# config2 = pdfkit.configuration(wkhtmltopdf='C:\\Users\\raksh\\OneDrive\\Desktop\\web\\walkwise\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
csp = {
    'default-src': '\'self\'',
    'connect-src': ['\'self\'', 'https://api.example.com'],  # Add your API endpoint here
    'style-src': [
        '\'self\'',
        'https://fonts.googleapis.com',
        'https://cdn.jsdelivr.net',
        'https://kit-free.fontawesome.com',
        'https://stackpath.bootstrapcdn.com',
        'https://cdn-uicons.flaticon.com',
        'https://fonts.gstatic.com',
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',  # Include Bootstrap if not already allowed
    ],
    'font-src': [
        '\'self\'',
        'https://maxcdn.bootstrapcdn.com',
        'https://stackpath.bootstrapcdn.com',
        'https://fonts.gstatic.com',
        'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.15.4/webfonts/',  # Include FontAwesome if not already allowed
        'https://cdn-uicons.flaticon.com',
    ],
    'script-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',
        'https://stackpath.bootstrapcdn.com',
        'https://kit.fontawesome.com',
        'https://cdnjs.cloudflare.com',
      '{{ url_for("static", filename="script.js") }}'
    ],
    'img-src': [
        '\'self\'',
        'blob:',
        'data:',
        'file:',
        '*',
        'https://res.cloudinary.com/dh6qnpost/',
        'https://images.unsplash.com/',
        
    ],
    'media-src': ['\'self\'', 'https://res.cloudinary.com/dh6qnpost/'],
    'object-src': '\'none\'',
    'child-src': ['blob:'],
}

talisman = Talisman(app, content_security_policy=csp)



# Association Table
cart_items = db.Table(
    'cart_items',
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'), primary_key=True),
    db.Column('cover_id', db.Integer, db.ForeignKey('covers.id'), primary_key=True),
    db.Column('cover_quantity', db.Integer, nullable=False, default=1)
)
order_items = db.Table(
    'order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('cover_id', db.Integer, db.ForeignKey('covers.id'), primary_key=True),
    db.Column('cover_quantity', db.Integer, nullable=False, default=1)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    comments = db.relationship('Comment', backref='user')
    orders = db.relationship('Order', backref='user')
    cart = db.relationship('Cart', backref='user', uselist=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # covers_ordered = db.relationship('Covers', secondary='order_items', backref='orders')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    address1 = db.Column(db.String(250), nullable=False)
    address2 = db.Column(db.String(250), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    town_city = db.Column(db.String(250), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(250), nullable=False)
    country = db.Column(db.String(250), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    cover_title = db.Column(db.String(250), nullable=False)  # New field
    cover_quantity = db.Column(db.Integer, nullable=False)  # New field
    phone_model = db.Column(db.String(250), nullable=False)

class Covers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    model = db.Column(db.String(250), nullable=False)
    price = db.Column(db.String(250), nullable=False)
    image = db.Column(db.String(250), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    carts = db.relationship('Cart', secondary=cart_items, backref='covers', overlaps="carts,covers")
    orders = db.relationship('Order', secondary='order_items', backref='covers')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship('Covers', secondary=cart_items, backref='cart', overlaps="carts,covers")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function
def get_total_quantity():
    if current_user.is_authenticated:
        # Join necessary tables to get cart items for the current user
        query = db.session.query(func.coalesce(func.sum(cart_items.columns.cover_quantity), 0)). \
            join(Cart, Cart.id == cart_items.columns.cart_id). \
            join(User, User.id == Cart.user_id). \
            filter(User.id == current_user.id)

        quantity = query.scalar()
    else:
        quantity = 0
    return quantity

@app.route("/", methods=['POST', 'GET'])
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    covers = Covers.query.paginate(page=page, per_page=per_page, error_out=False)
    results = db.session.execute(db.select(User).order_by(User.name))
    users = results.scalars().all()
    quantity = get_total_quantity()
    return render_template("home.html",quantity=quantity, covers=covers, users=users)
@app.route("/home", methods=['POST', 'GET'])
def landing():
    return render_template("head.html")

@app.route("/reviews",methods=['POST', 'GET'])
def reviews():
    if request.method == "POST":
        new_comment = Comment(
            user_id=current_user.id,
            text=request.form.get('userComment')
        )
        db.session.add(new_comment)
        db.session.commit()
    results = db.session.execute(db.select(User).order_by(User.name))
    users = results.scalars().all()
    quantity = get_total_quantity()
    return render_template("comments.html",quantity=quantity,users=users)

@app.route('/add_cover', methods=['POST', 'GET'])
@admin_only
def add_cover():
    if request.method == "POST":
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            upload_result = cloudinary.uploader.upload(
                file,
                folder="covers"
            )
            image_url = upload_result.get('url')
        user_id = current_user.id
        new_cover = Covers(
            model=request.form.get('phoneName'),
            price=request.form.get('price'),
            image=image_url,
            quantity=request.form.get('quantity'),
            title=request.form.get('title'),
            user_id=user_id
        )

        db.session.add(new_cover)
        db.session.commit()
        return (redirect(url_for('home')))
    return render_template("covers_add_form.html")


# @app.route('/cover_details/<cover_id>/update', methods=['GET', 'POST'])
# @admin_only
# def update_cover(cover_id):
#     cover = Covers.query.get_or_404(cover_id)
#     # Check if the current user is the owner of the cover
#     if cover.user_id != current_user.id:
#         flash('You do not have permission to update this cover.', 'danger')
#         return redirect(url_for('home'))
#
#     if request.method == 'POST':
#         if 'image' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['image']
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#
#         if file:
#             upload_result = cloudinary.uploader.upload(
#                 file,
#                 folder="covers"
#             )
#             image_url = upload_result.get('url')
#         cover.model = request.form.get('phoneName')
#         cover.price = request.form.get('price')
#         cover.image = image_url
#         cover.quantity = request.form.get('quantity')
#         cover.title = request.form.get('title')
#         db.session.commit()
#         flash('Cover updated successfully!', 'success')
#         return redirect(url_for('home'))
#     else:
#         return render_template('update_cover_form.html', cover=cover)


@app.route('/cover_details/<cover_id>', methods=['POST', 'GET'])
def cover_detais(cover_id):
    if request.method == "POST":
        new_comment = Comment(
            user_id=current_user.id,
            text=request.form.get('userComment')
        )
        db.session.add(new_comment)
        db.session.commit()
    results = db.session.execute(db.select(User).order_by(User.name))
    users = results.scalars().all()
    cover = db.get_or_404(Covers, cover_id)
    cancelled_price=int(cover.price)*10
    return render_template("cover_details.html", cover=cover, users=users, cancelled_price=cancelled_price)


# Assuming you have a route to delete covers

@app.route('/cover_details/<cover_id>/delete', methods=['DELETE'])
def delete_cover_perm(cover_id):
    cover = Covers.query.get_or_404(cover_id)

    # Check if the cover is associated with any carts or orders
    carts_with_cover = Cart.query.filter(Cart.items.contains(cover)).all()
    orders_with_cover = Order.query.filter(Order.covers.contains(cover)).all()

    try:
        # Delete the cover and commit changes
        db.session.delete(cover)
        db.session.commit()

        # Remove the cover from carts and orders
        for cart in carts_with_cover:
            cart.items.remove(cover)
        for order in orders_with_cover:
            order.covers.remove(cover)

        # Commit the changes after removing associations
        db.session.commit()
        return redirect(url_for('view_covers'))  # Redirect to covers page after successful deletion
    except Exception as e:
        db.session.rollback()  # Rollback changes if an error occurs
        print(e)  # Handle or log the error appropriately
        return redirect(url_for('view_covers'))




@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        results = db.session.execute(db.select(User).where(User.email == request.form.get('email')))
        user = results.scalar()
        if user:
            password = request.form.get('password')
            if (check_password_hash(user.password, password)):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Incorrect password!")
        else:
            flash('No  account found with that email address. Please register or check your entry.')
    return render_template("login-form.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        results = db.session.execute(db.select(User).where(User.email == request.form.get('email')))
        user = results.scalar()
        if not user:
            if request.form.get('role')== 'customer':
                seller=False
            else:
                seller=True
            new_user = User(
                name=request.form.get('username'),
                email=request.form.get('email'),
                password=generate_password_hash(request.form.get('password')),
                is_admin=seller
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
        else:
            flash(f"An account is already registered to this email.")
    return render_template('signup-form.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/add-to-cart/<int:cover_id>")
def add_to_cart(cover_id):
    if not current_user.is_authenticated:
        return render_template('not_log_in.html', message="You need to be logged in to add items to your cart")

    user = current_user
    cover = db.get_or_404(Covers, cover_id)

    if user.cart is None:
        user.cart = Cart()
        db.session.commit()

    user_cart = user.cart
    cart_item = db.session.query(cart_items).filter_by(cart_id=user_cart.id, cover_id=cover.id).first()

    if cart_item is None:
        # Create a new entry in the association table
        db.session.execute(cart_items.insert().values(cart_id=user_cart.id, cover_id=cover.id, cover_quantity=1))
    else:
        # Update the cover_quantity column in the cart_items table
        db.session.execute(
            cart_items.update().where(cart_items.c.cart_id == user_cart.id, cart_items.c.cover_id == cover.id).values(
                cover_quantity=cart_item.cover_quantity + 1))

    # Check if the cover is not already in user_cart.items
    if cover not in user_cart.items:
        # Directly append the cover to user_cart.items
        user_cart.items.append(cover)

    db.session.commit()

    return redirect(url_for('home'))


@app.route("/view_cart")
def view_cart():
    if not current_user.is_authenticated:
        return render_template('not_log_in.html', message="You need to be logged in to access your cart")

    user = current_user
    user_cart = user.cart

    if user_cart is None:
        user_cart = Cart(user_id=user.id)
        db.session.add(user_cart)
        db.session.commit()

    user_cart_items = user_cart.items
    total = 0
    items = []

    for item in user_cart_items:
        # Use db.session.query(cart_items) to get the cover_quantity
        cart_item = db.session.query(cart_items).filter_by(cart_id=user_cart.id, cover_id=item.id).first()
        cover_item = {
            'cover': item,
            'cover_quantity': cart_item.cover_quantity if cart_item else 0,  # Default to 0 if cart_item is None
            'image': item.image,
            'price': item.price,
            'title': item.title,
            'model': item.model,
            'id': item.id
        }
        items.append(cover_item)
        total += int(item.price.split('.')[0]) * cover_item['cover_quantity']

    return render_template("cart.html", items=items, total=total)

# @app.route("/get_pdf", methods=['POST'])
# def get_pdf():
#     if not current_user.is_authenticated:
#         return render_template('not_log_in.html', message="You need to be logged in to access your cart")
#
#     user = current_user
#     user_cart = user.cart
#     if request.method=="POST":
#         if user_cart is None:
#             user_cart = Cart(user_id=user.id)
#             db.session.add(user_cart)
#             db.session.commit()
#
#         user_cart_items = user_cart.items
#         total = 0
#         items = []
#
#         for item in user_cart_items:
#         # Use db.session.query(cart_items) to get the cover_quantity
#             cart_item = db.session.query(cart_items).filter_by(cart_id=user_cart.id, cover_id=item.id).first()
#             cover_item = {
#                 'cover': item,
#                 'cover_quantity': cart_item.cover_quantity if cart_item else 0,  # Default to 0 if cart_item is None
#                 'image': item.image,
#                 'price': item.price,
#                 'title': item.title,
#                 'model': item.model,
#                 'id': item.id
#             }
#             items.append(cover_item)
#             total += int(item.price.split('.')[0]) * cover_item['cover_quantity']
#         invoice = "invoice"
#         rendered = render_template("pdf.html", items=items, total=total)
#         pdf = pdfkit.from_string(rendered, False, configuration=config2)
#         response = make_response(pdf)
#         response.headers['Content-Type'] = 'application/pdf'
#         response.headers['Content-Disposition'] = f'inline; filename={invoice}.pdf'
#
#     return response

@app.route("/delete_item/<int:cover_id>")
def delete_cover(cover_id):
    user = current_user
    user_cart = user.cart
    cover_to_remove = db.get_or_404(Covers, cover_id)
    cart_item = db.session.query(cart_items).filter_by(cart_id=user_cart.id, cover_id=cover_to_remove.id).first()
    if cart_item:
        db.session.execute(cart_items.delete().where(cart_items.c.cart_id == user_cart.id,
                                                     cart_items.c.cover_id == cover_to_remove.id))
        db.session.commit()

    return redirect(url_for('view_cart'))


@app.route('/search_covers/')
def search_covers():
    s = request.args.get('query', '')
    results = Covers.query.filter(Covers.title.ilike(f"%{s}%")).all()
    return render_template('results.html', results=results, query=s)


@app.route('/about-me')
def about_me():
    return render_template("about.html")


@app.route('/account')
def account():
    if current_user.is_authenticated:
        orders = Order.query.filter_by(user_id=current_user.id).all()
        return render_template("account.html", user=current_user, items=orders)
    else:
        return render_template("not_log_in.html", message="You need to be logged in to check your account")


@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if request.method == 'POST':
        # num_covers = int(request.form.get('num_covers'))
        # covers_info = []
        # for i in range(0, num_covers + 1):
        #     cover_title = request.form.get(f'title_{i}')
        #     cover_quantity = request.form.get(f'quantity_{i}')
        #     phone_model = request.form.get(f'model_{i}')
        #     covers_info.append({'title': cover_title, 'quantity': cover_quantity, 'model': phone_model})
        user = current_user
        covers_info = []
        for item in user.cart.items:
            cart_it = db.session.query(cart_items).filter_by(cart_id=user.cart.id, cover_id=item.id).first()
            cover_info={
                'cover': item,
                'quantity': cart_it.cover_quantity,
                'price': item.price,
                'title': item.title,
                'model': item.model,
            }
            covers_info.append(cover_info)

        for cover in covers_info:
            new_order = Order(
                user_id=current_user.id,
                date=str(datetime.today().date()),
                name=request.form.get('name'),
                email=request.form.get('email'),
                address1=request.form.get('address1'),
                address2=request.form.get('address2'),
                pincode=request.form.get('pincode'),
                town_city=request.form.get('Town/City'),
                phone_number=request.form.get('phone'),
                state=request.form.get('state'),
                country=request.form.get('countries'),
                payment_type=request.form.get('payment_type'),
                cover_title=cover['title'],
                cover_quantity=cover['quantity'],
                phone_model=cover['model']
            )
        db.session.add(new_order)

        for item in user.cart.items:
            cart_it = db.session.query(cart_items).filter_by(cart_id=user.cart.id, cover_id=item.id).first()
            if cart_it:
                item.order_id = new_order.id
                cover = db.session.get(Covers, item.id)
                cover.quantity -= cart_it.cover_quantity
                db.session.query(cart_items).filter_by(cart_id=user.cart.id, cover_id=item.id).delete()
                db.session.commit()

        user.cart.items = []
        db.session.commit()
        return render_template("order_sucess.html")

    user = current_user
    if not current_user.is_authenticated or user.cart is None:
        return render_template("not_log_in.html", message='Session Expired! Please Log In Again')

    user_cart = user.cart
    user_cart_items = user_cart.items
    total = 0
    items = []

    for item in user_cart_items:
        cart_item = db.session.query(cart_items).filter_by(cart_id=user_cart.id, cover_id=item.id).first()
        cover_item = {
            'cover': item,
            'cover_quantity': cart_item.cover_quantity,
            'image': item.image,
            'price': item.price,
            'title': item.title,
            'model': item.model,
            'id': item.id
        }
        items.append(cover_item)
        total += int(item.price.split('.')[0]) * cover_item['cover_quantity']
    return render_template("checkout.html", items=items, total=total)


@app.route('/admin/orders')
@admin_only
def admin_orders():
    # Query orders related to covers posted by the current admin
    admin_user_id = current_user.id

    print(admin_user_id)
    admin_orders = Order.query \
        .all()
    return render_template('admin_orders.html', orders=admin_orders)


# hashed_password = generate_password_hash("S@hil276")
#
# with app.app_context():
#     # your code here, e.g., database operations
#     new_admin = User(
#     name = 'Raksha',
#     email = 'rakshabv@example.com',
#     password = hashed_password,  # make sure to hash passwords
#     is_admin = True
#     )
#     db.session.add(new_admin)
#     db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
