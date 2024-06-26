from flask import render_template,flash, request,jsonify,redirect,url_for,make_response
from orders import app,db
from orders.models import Orders,Orders_items,Products,Users
import pdfkit
from datetime import date
from sqlalchemy import func
from orders.forms import RegisterForm
from flask_login import login_user, current_user, logout_user, login_required
from passlib.hash import sha256_crypt
from datetime import datetime, timedelta
from flask import session

def getlist():
    user = Users.query.filter_by(email=current_user.email).first()
    my_list = user.Roles.split(",")
    return my_list


@app.route('/dashboard')
#@login_required
def dashboard():
    count = db.session.query(Orders_items).filter(func.date(Orders_items.order_date) == date.today()).count()

    num_orders = db.session.query(Orders_items).count()
    today = datetime.today()
    # Calculate the start of the current week (Monday)
    start_of_this_week = today - timedelta(days=today.weekday())
    # Calculate the start of the last week (Monday)
    end_of_this_week = start_of_this_week + timedelta(days=7)
    print(start_of_this_week)
    #print(start_of_last_week)
    print(end_of_this_week)
    orders = db.session.query(Orders_items).filter(
        Orders_items.order_date >= start_of_this_week,
        Orders_items.order_date <= end_of_this_week
    ).all()

    # Query orders with "pending" status
    pending_orders = db.session.query(Orders_items).filter(Orders_items.status == "pending").all()
    #print(orders)
    context = {
        'daily' : count,
        'numorders' : num_orders
    }

    return render_template('index.html',context=context, orders=orders, pending_orders=pending_orders)


@app.route('/',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        user=Users.query.filter_by(email=email).first()
        if user:

            passwordd=Users.query.filter_by(email=email).first()
            if sha256_crypt.verify(password_candidate, passwordd.password):
                login_user(user)
                session['username'] = user.username
                #flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))

            else:
                error = "Invalid Password"
                return render_template('login.html', error=error)

        else:
            error = "Invalid email"
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
#@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register',methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        addd = Users(username=username,email=email,password= password)
        db.session.add(addd)
        db.session.commit()
        flash('You are now registered', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/roles')
#@login_required
def roles():
    users = Users.query.all()
    return render_template('roles.html',users=users)

@app.route('/order')
#@login_required
def order():
    return render_template('makeorder.html')

@app.route('/insert', methods=['POST'])
# @login_required
def insert():
    client_name = request.form.get('client_name')
    client_contact = request.form.get('client_contact')
    order_date = request.form.get('order_date')
    total_amount = request.form.get('total_amount')

    barcode = request.form.getlist('item_bar[]')
    qua = request.form.getlist('item_quantity[]')
    name = request.form.getlist('item_name[]')
    total = request.form.getlist('total[]')

    price = request.form.getlist('price[]')

    # Convert order_date string to datetime object
    order_date = datetime.strptime(order_date, '%Y-%m-%d')
    order_date = order_date.strftime('%m-%d-%Y')  # Convert to new format
    order_date = datetime.strptime(order_date, '%m-%d-%Y')  # Convert back to datetime object
    order_date = order_date.date()
    print(order_date)

    #print(order_date)



    # Insert order items into database
    try:
        # Insert order items into database
        for q, p, t, n, b in zip(qua, price, total, name, barcode):
            t = round(float(t), 2)
            ord = Orders_items(product_code=b, quantity=q, product_type=n, price=p, total=t,
                               client_name=client_name, client_contact=client_contact, order_date=order_date, status="pending")
            db.session.add(ord)
        db.session.commit()
        print("1")  # Print "1" if insertion is successful
        orders = Orders.query.all()
        print(orders)

    except Exception as e:
        print(e)

    return jsonify({'data': 'ok'})


@app.route('/data',methods=['POST'])
#@login_required
def getdata():
    input_item = request.json
    pro = Products.query.filter_by(product_code=input_item).first()
    return jsonify({'price':pro.price ,'product_type':pro.product_type,'quantity_range':pro.quantity_range, 'quantity_min':pro.quantity_min, 'quantity_max':pro.quantity_max})

@app.route('/products',methods=['GET','POST'])
#@login_required
def products():
        products = Products.query.all()
        if request.method == 'POST':
            product_type = request.form.get('product_type')
            client_role = request.form.get('client_role')
            description = request.form.get('description')
            product_code = request.form.get('product_code')
            quantity_range = request.form.get('quantity_range')
            stock = request.form.get('stock')


            if "-" in quantity_range:
                quantity_min, quantity_max = map(int, quantity_range.split('-'))
            price = request.form.get('price')
            add = Products(product_type=product_type,client_role=client_role,description=description,product_code=product_code, quantity_range=quantity_range, quantity_min=quantity_min, quantity_max=quantity_max, price=price, stock=stock)
            db.session.add(add)


            db.session.commit()
            return redirect(url_for('products'))
        return render_template('product.html',products=products)


@app.route("/product/delete/<int:product_code>", methods=['POST'])
#@login_required
def delete_product(product_code):
    product = Products.query.get(product_code)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))


@app.route("/product/update/<int:product_code>", methods=['POST','GET'])
#@login_required
def update_product(product_code):
    product = Products.query.get(product_code)
    if request.method == 'POST':
        product.product_type = request.form.get('product_type')
        product.client_role = request.form.get('client_role')
        product.description = request.form.get('description')
        product.product_code = request.form.get('product_code')
        product.quantity = request.form.get('quantity_range')
        product.stock = request.form.get('stock')
        product.price = request.form.get('price')
        db.session.commit()
        return redirect(url_for('products'))

    return render_template('update_product.html',product=product)

@app.route("/manageorder")
#@login_required
def manageorder():
    orders = Orders_items.query.all()
    print(orders)
    return render_template('manageorder.html',orders=orders)


def deleteorder(order_id):
    order = Orders_items.query.get(order_id)
    db.session.delete(order)
    db.session.commit()


@app.route("/order/delete/<int:order_id>", methods=['POST'])
#@login_required
def delete_order(order_id):
    deleteorder(order_id)
    return redirect(url_for('manageorder'))

@app.route("/order/update/<int:order_id>", methods=['POST','GET'])
#@login_required
def update_order(order_id):

    order = Orders_items.query.get(order_id)

    if request.method == 'POST':
        product_code = request.form.get('product_code')
        quantity = request.form.get('item_quantity')
        product_type = request.form.get('product_type')
        total = request.form.get('total')
        total = round(float(total), 2)
        price = request.form.get('price')
        client_name = request.form.get('client_name')
        client_contact = request.form.get('client_contact')
        status = request.form.get('status')

        existing_order = Orders_items.query.filter_by(id=order_id).first()

        if existing_order:
            # Update the attributes of the existing item
            existing_order.product_code = product_code
            existing_order.quantity = quantity
            existing_order.price = price
            existing_order.total = total
            existing_order.product_type = product_type
            existing_order.client_name = client_name
            existing_order.client_contact = client_contact
            existing_order.status = status
            #existing_order.order_date = order_date
            #order_date = datetime.strptime(order_date, '%m/%d/%Y')
        db.session.commit()
        if status=="completed":
            product = Products.query.get(product_code)
            product.stock = str(int(product.stock)- int(quantity))
            db.session.commit()
        return redirect(url_for('manageorder'))

    return render_template('update_order.html',order = order,order_amount=order)

@app.route("/printInvoice/<int:order_id>")
#@login_required
def printInvoice(order_id):
      order = Orders_items.query.get(order_id)
      #renderd = render_template('print.html',order=order)
      #css = ['orders/static/css/sb-admin-2.min.css']
      #pdf = pdfkit.from_string(renderd,False,css=css)
      #response = make_response(pdf)
      #response.headers['Content-Type'] = 'application/pdf'
      #response.headers['Content-Disposition'] = f'attachment; filename = {order_id}.pdf'
      return render_template('print.html',order=order)


@app.route('/generate_report', methods=['GET'])
#@login_required
def generate_report():
    # Fetch all orders and their items from the database
    orders = Orders.query.all()

    # Prepare data for the report
    report_data = []
    for order in orders:
        order_details = {
            'order_id': order.id,
            'user_id': order.user_id,
            'total_amount': order.total_amount,
            'date_creation': order.date_creation,
            'items': []
        }
        for item in order.orders:
            order_details['items'].append({
                'product_code': item.product_code,
                'quantity': item.quantity,
                'product_type': item.product_type,
                'price': item.price,
                'total': item.total,
                'client_name': item.client_name,
                'client_contact': item.client_contact,
                'status': item.status,
                'order_date': item.order_date
            })
        report_data.append(order_details)

    # Render the report template with the data
    return render_template('report.html', report_data=report_data)