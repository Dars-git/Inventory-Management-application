from orders import db, app, login_manager
import datetime
from flask_login import UserMixin
from flask_migrate import Migrate
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.now())
    roles = db.Column(db.String(120))
    order = db.relationship('Orders', cascade="all,delete", backref='user_order', lazy=True)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.String(80), nullable=False)
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.now())
    orders = db.relationship('Orders_items', cascade="all,delete", backref='Orders_items', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Orders_items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    product_type = db.Column(db.String(80), nullable=False)
    price = db.Column(db.String(80), nullable=False)
    total = db.Column(db.String(80), nullable=False)
    client_name = db.Column(db.String(80), nullable=False)
    client_contact = db.Column(db.String(80), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))

class Products(db.Model):
    product_type = db.Column(db.String(80), nullable=False)
    client_role = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    product_code = db.Column(db.String(80), primary_key=True)
    quantity_range = db.Column(db.String(80), nullable=True)
    quantity_min = db.Column(db.String(80), nullable=True)
    quantity_max = db.Column(db.String(80), nullable=True)
    price = db.Column(db.String(80), nullable=False)


# Check if tables exist, if not create them
with app.app_context():
    #db.drop_all()
    db.create_all()
