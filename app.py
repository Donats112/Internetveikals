from flask import (
    Flask,
    request,
    render_template,
    redirect,
    flash,
    session)
#from flask_mysqldb import MySQL
#from flaskext.mysql import MySQL
from config import Config
from uuid import uuid4
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
#from flask_mysql_connector import MySQL
#import mysql.connector
import os
from werkzeug.utils import secure_filename
from verification import user_session, logout_user, login_required, admin_login_required
from decimal import Decimal
from datetime import datetime


app = Flask(__name__)
app.config.from_object(Config)
#mysql = MySQL(app)
#mysql.init_app(app)
cnx = mysql.connector.connect(user='root', password='#Password1',
 host='localhost',
 database='internetveikals')

# routes
@app.route('/delete_from_cart/<product_id>', methods=['GET'])
@login_required
def delete_product_from_cart(product_id):
    cur = cnx.cursor()
    user_id = session.get('user_id')
    try:
        # Get the cart_id for the user
        query_string = '''SELECT cart_id FROM cart WHERE user_id = %s'''
        cur.execute(query_string, (user_id,))
        cart_id = cur.fetchone()[0]

        # Delete the product from the cart_items table
        query_string = '''DELETE FROM cart_items WHERE product_id = %s AND cart_id = %s'''
        cur.execute(query_string, (product_id, cart_id))
        cnx.commit()

        cur.close()
        flash("Produkts izņemts no groza", "success")

        return redirect("/view_cart")
    except Exception as e:
        flash("Database error: " + str(e), "error")
        return redirect("/view_cart")

    

@app.route('/add_to_cart/<product_id>', methods=['GET'])
@login_required
def add_to_cart(product_id):
    cur = cnx.cursor()
    user_id = session.get('user_id')
    try:
        query_string = '''SELECT cart_id FROM cart WHERE user_id = %s'''
        cur.execute(query_string, (user_id,))
        cart_id = cur.fetchone()[0]  # Assuming cart_id is the first element of the tuple
        query_string = '''INSERT INTO cart_items (id, product_id, cart_id) VALUES (%s, %s, %s)'''
        val1 = (str(uuid4()), product_id, cart_id)
        cur.execute(query_string, val1)
        cnx.commit()
        cur.close()
        flash("Produkts pievienots grozam", "success")
        return redirect("/products")
    except Exception as e:
        flash("Database error: " + str(e), "error")
        return redirect("/products")
    

@app.route('/admin_products', methods=['GET', 'POST'])
@admin_login_required
def admin_products():
    if request.method == "POST":
        name = request.form.get('prod_name')
        kategorija = request.form.get('kategorija')
        cost = request.form.get('cost')
        size = request.form.get('size')
        image_file = request.files['image']
        description = request.form.get('description')

        # Save the image file to the 'images' folder
        if image_file:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        else:
            image_path = 'static/images/default_image.png'

        try:
            cur = cnx.cursor()
            query_string = """INSERT INTO products (product_id, prod_name, categ_id, cost, size, image_file, description) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            val = (str(uuid4()), name, kategorija, cost, size, image_path, description)
            cur.execute(query_string, val)
            cnx.commit()
            cur.close()
            flash("Produkts pievienots", "success")
            return redirect("/admin_products")
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return redirect("/admin_products")

    else:
        try:
            cur = cnx.cursor()
            query_string = """SELECT products.prod_name, categories.kategorija, products.cost, products.size, products.image_file, products.description, products.product_id 
                            FROM products 
                            JOIN categories ON products.categ_id = categories.categ_id
                            """
            cur.execute(query_string)
            produkts = cur.fetchall()
            query_string = """SELECT * from categories"""
            cur.execute(query_string)
            kategorijas = cur.fetchall()
            cur.close()
            return render_template("admin_produkti.html", produkts=produkts, kategorijas=kategorijas)
            
        except Exception as e:
            flash("Database error: " + str(e), "error")


@app.route('/products', methods=['GET'])
def produkti():
    try:
        cur = cnx.cursor()
        query_string = """SELECT products.prod_name, categories.kategorija, products.cost, products.size, products.image_file, products.description, products.product_id
                        FROM products 
                        JOIN categories ON products.categ_id = categories.categ_id
                        """
        cur.execute(query_string)
        produkts = cur.fetchall()
        cur.close()
        print(produkts)
        return render_template("produkti.html", produkts=produkts)
        
    except Exception as e:
        flash("Database error: " + str(e), "error")
            
#categories
@app.route('/categ', methods=['POST', 'GET'])
@admin_login_required
def categ():
    if request.method == "POST":
        try:
            kategorija = request.form.get("kategorija")
            print("Received kategorija value:", kategorija)
            categ_id = str(uuid4())
            cur = cnx.cursor()
            add_category = ("INSERT INTO internetveikals.categories "
                "(categ_id, kategorija) "
                "VALUES (%s,%s)")
            val = (categ_id, kategorija)
            cur.execute(add_category, val)
            cnx.commit()
            cur.close()
            flash("Kategorija pievienota", "success")
            return redirect("/categ")
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return redirect("/categ")
    else:
        try:
            cur = cnx.cursor()
            query_string = "SELECT * FROM categories"
            cur.execute(query_string)
            kategorijas = cur.fetchall()
            cur.close()
            print(kategorijas)
            return render_template("categ.html", manas_kategorijas=kategorijas)
            
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return render_template("categ.html", categories=[])
        
#Home
@app.route('/', methods = ['GET'])
@app.route('/home', methods = ['GET'])
def home():
        try:
            cur = cnx.cursor()
            # Fetch three random products from the database
            query_string = """SELECT products.prod_name, categories.kategorija, products.cost, products.size, products.image_file, products.description, products.product_id
                        FROM products 
                        JOIN categories ON products.categ_id = categories.categ_id
                        ORDER BY RAND()
                        LIMIT 3
                        """
            cur.execute(query_string)
            random_products = cur.fetchall()
            cur.close()
            return render_template("home.html", random_products=random_products)
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return render_template("home.html")
        
#Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        try:
            cur = cnx.cursor()
            username = request.form["username"]
            password = request.form["password"]
            cur.execute("SELECT user_id, password, admin FROM users WHERE username = %s", (username, ))
            user = cur.fetchall()
            if len(user) > 0:
                if check_password_hash(user[0][1], password):
                    user_session(user, username)
                    flash("Pieslēgšanās izdevusies")
                else:
                    flash("Nepareiza parole")
            else:
                flash("Lietotājs neeksistē")
                return redirect("/login")
            cur.close()
            return redirect("/home")
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return render_template("login.html")
    else:
        return render_template("login.html")
#Register
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_check = request.form["password-check"]
        if password != password_check:
            flash("Paroles nesakrīt")
            return redirect("/register")
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        e_mail = request.form["e-mail"]
        phone = request.form["phone"]
        address = request.form["address"]
        user_id = str(uuid4())
        newUserSql = ''' INSERT INTO users (user_id, username, password, first_name, last_name, e_mail, phone, adress, admin) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) '''
        val1 = (user_id,
                username, 
                generate_password_hash(password), 
                first_name, 
                last_name, 
                e_mail, 
                phone,
                address,
                int(0))
        UserCartSql = ''' INSERT INTO cart (cart_id, user_id) VALUES (%s, %s)'''
        val2 = (str(uuid4()), user_id)
        try:
            cur = cnx.cursor()
            cur.execute(newUserSql, val1)
            cnx.commit()
            cur.execute(UserCartSql, val2)
            cnx.commit()
            cur.close()
            flash("Lietotāja konts veiksmīgi izveidots")
            return redirect("/login")
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return redirect("/register")
    else:
        return render_template("register.html")
    
#Admin
@app.route("/admin", methods=['POST', 'GET'])
@admin_login_required
def admin():
    if request.method=="POST":
        pass
    else:
        return render_template("admin.html")

#Logout
@app.route("/logout")
def logout():
    logout_user()
    flash("Jūs neesat pieslēdzies")
    return redirect("/home")

#Cart
@app.route("/view_cart", methods=['POST', 'GET'])
@login_required
def view_cart():
    if request.method=="GET":
        try:
            cur = cnx.cursor()
            user_id = session.get('user_id')
            # Fetch products in the user's cart
            query_string = """
                SELECT products.product_id, products.prod_name, categories.kategorija, products.cost, products.size, products.image_file, products.description 
                FROM products
                JOIN categories ON products.categ_id = categories.categ_id
                WHERE products.product_id IN (
                    SELECT product_id FROM cart_items WHERE cart_id = (
                        SELECT cart_id FROM cart WHERE user_id = %s
                    )
                )
            """
            cur.execute(query_string, (user_id,))
            produkts = cur.fetchall()
            cur.close()
            return render_template("view_cart.html", produkts=produkts)
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return render_template("view_cart.html")
    else:
        ...


from datetime import datetime

@app.route("/buy", methods=["POST"])
def buy():
    try:
        cur = cnx.cursor()
        user_id = session.get('user_id')
        
        # Fetch the product_id and cost for each item in the user's cart
        sql = """
            SELECT products.product_id, products.cost
            FROM products
            JOIN cart_items ON products.product_id = cart_items.product_id
            JOIN cart ON cart_items.cart_id = cart.cart_id
            WHERE cart.user_id = %s 
        """
        cur.execute(sql, (user_id,))
        cart_items = cur.fetchall()
        
        total_cost = 0  # Initialize total cost
        
        # Insert data into orders table for each item in the cart
        for item in cart_items:
            product_id = item[0]
            count = request.form.get("count_" + product_id)  # Get the count for the current product
            cost_per_item = 0
            if item[1] is not None:
                cost_per_item = item[1] * Decimal(count)  # Calculate cost per item based on count
                total_cost += cost_per_item  # Add the cost per item to the total cost
                
                # Insert into orders table
                order_id = str(uuid4())
                order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql_insert_order = """
                    INSERT INTO orders (order_id, user_id, order_date, product_id, quantity, total_cost)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql_insert_order, (order_id, user_id, order_date, product_id, count, cost_per_item))
        
        # Commit changes to the database
        cnx.commit()
        cur.close()
        
        # Clear the user's cart after purchase
        clear_cart(user_id)
        
        # Redirect to the order page
        return render_template("buy.html", total_cost=total_cost)

    except Exception as e:
        flash("Database error: " + str(e), "error")
        return render_template("view_cart.html")
    

@app.route("/order")
@login_required
def order():
    try:
        cur = cnx.cursor()
        user_id = session.get('user_id')
        
        # Fetch orders for the current user
        sql = """
            SELECT orders.order_id, orders.order_date, orders.product_id, orders.quantity, orders.total_cost, products.prod_name
            FROM orders
            JOIN products ON products.product_id = orders.product_id
            WHERE user_id = %s
        """
        cur.execute(sql, (user_id,))
        orders = cur.fetchall()
        
        cur.close()
        return render_template("order.html", orders=orders)

    except Exception as e:
        flash("Database error: " + str(e), "error")
        return render_template("order.html", orders=[])
    

def clear_cart(user_id):
    try:
        cur = cnx.cursor()
        # Fetch the cart_id for the user
        query_string = '''SELECT cart_id FROM cart WHERE user_id = %s'''
        cur.execute(query_string, (user_id,))
        cart_id = cur.fetchone()[0]

        # Delete all items from the cart_items table for the user's cart
        query_string = '''DELETE FROM cart_items WHERE cart_id = %s'''
        cur.execute(query_string, (cart_id,))
        cnx.commit()

        cur.close()
    except Exception as e:
        flash("Database error: " + str(e), "error")



if app.config["FLASK_ENV"] == "development":
    if __name__ == "__main__":
        app.run(debug=True)

cnx.close()
