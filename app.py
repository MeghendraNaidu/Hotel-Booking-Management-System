import datetime
import random
import stripe
from decimal import Decimal
from io import BytesIO
from reportlab.pdfgen import canvas
from flask import send_file
from flask import Flask, render_template, request, redirect, send_file, url_for, session, flash
import mysql.connector  # Import MySQL connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'
stripe.api_key = 'your_stripe_secret_key'

db_config = {
    'user': 'root',  # MySQL username
    'password': '1234',  # MySQL password
    'host': 'localhost',  # MySQL server host (usually localhost)
    'database': 'hotel_management',  # The database we created
}

ROOM_RATES = {
    'Single': 1500.00,
    'Double': 2000.00,
    'Suite': 2500.00
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch the admin from the database
        query = "SELECT * FROM admin WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        admin = cursor.fetchone()

        cursor.close()
        connection.close()

        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin.html')

@app.route('/admin/rooms', methods=['GET', 'POST'])
def manage_rooms():
    # Connect to MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        # Add new room
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        room_rate = request.form['room_rate']
        is_available = request.form['is_available'] == 'True'
        clean_status = request.form.get('clean_status', 'Clean')

        insert_room_query = '''INSERT INTO rooms (room_number, room_type, room_rate, is_available, clean_status) 
                                VALUES (%s, %s, %s, %s, %s)'''
        cursor.execute(insert_room_query, (room_number, room_type, room_rate, is_available, clean_status))
        connection.commit()
        flash("Room added successfully", "success")

    # Fetch all rooms to display in the admin panel
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('admin_rooms.html', rooms=rooms)

@app.route('/admin/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
def edit_room(room_id):
    # Connect to MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        # Update room information
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        room_rate = request.form['room_rate']
        is_available = request.form['is_available'] == 'True'
        clean_status = request.form['clean_status']

        update_room_query = '''UPDATE rooms 
                                SET room_number = %s, room_type = %s, room_rate = %s, is_available = %s, clean_status = %s 
                                WHERE room_id = %s'''
        cursor.execute(update_room_query, (room_number, room_type, room_rate, is_available, clean_status, room_id))
        connection.commit()
        flash("Room updated successfully", "success")
        return redirect(url_for('manage_rooms'))

    # Fetch room information for editing
    cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (room_id,))
    room = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('edit_room.html', room=room)

@app.route('/admin/restaurant', methods=['GET', 'POST'])
def manage_restaurant():
    
    conn = mysql.connector.connect(**db_config)  # Corrected connection initialization
    cursor = conn.cursor()

    if request.method == 'POST':
        # Add a new menu item
        item_name = request.form['item_name']
        item_price = request.form['item_price']
        item_category = request.form['item_category']
        availability = request.form['availability']

        insert_item_query = '''INSERT INTO restaurant (item_name, item_price, item_category, availability) 
                                VALUES (%s, %s, %s, %s)'''
        cursor.execute(insert_item_query, (item_name, item_price, item_category, availability))
        conn.commit()
        flash("Menu item added successfully", "success")

    # Fetch all menu items to display in the admin panel
    cursor.execute("SELECT * FROM restaurant")
    menu_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin_restaurant.html', menu_items=menu_items)

@app.route('/admin/restaurant/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    conn = mysql.connector.connect(**db_config)  # Corrected connection initialization
    cursor = conn.cursor()

    if request.method == 'POST':
        # Update menu item
        item_name = request.form['item_name']
        item_price = request.form['item_price']
        item_category = request.form['item_category']
        availability = request.form['availability']

        update_item_query = '''UPDATE restaurant 
                                SET item_name = %s, item_price = %s, item_category = %s, availability = %s 
                                WHERE item_id = %s'''
        cursor.execute(update_item_query, (item_name, item_price, item_category, availability, item_id))
        conn.commit()
        flash("Menu item updated successfully", "success")
        
        cursor.close()
        conn.close()
        return redirect(url_for('manage_restaurant'))

    # Fetch menu item data for editing
    cursor.execute("SELECT * FROM restaurant WHERE item_id = %s", (item_id,))
    menu_item = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('edit_menu_item.html', menu_item=menu_item)

@app.route('/admin/restaurant/delete/<int:item_id>', methods=['GET'])
def delete_menu_item(item_id):
    conn = mysql.connector.connect(**db_config)  # Corrected connection initialization
    cursor = conn.cursor()

    delete_item_query = '''DELETE FROM restaurant WHERE item_id = %s'''
    cursor.execute(delete_item_query, (item_id,))
    conn.commit()
    
    cursor.close()
    conn.close()

    flash("Menu item deleted successfully", "success")
    return redirect(url_for('manage_restaurant'))

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/user')
def user_home():
    return render_template('user_home.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        try:
            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if user and user['password'] == password:
                session['user'] = user['customer_name']  # Store first name in session
                session['users_id'] = user['users_id']
                flash("Login successful!", "success")
                return redirect(url_for('user_home'))
            else:
                flash("Invalid email or password.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
        finally:
            cursor.close()
            connection.close()

    return render_template('user_login.html')

@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        father_name = request.form['father_name']
        gender = request.form['gender']
        mobile_number = request.form['mobile_number']
        email = request.form['email']
        nationality = request.form['nationality']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        security_question = request.form['security_question']
        security_answer = request.form['security_answer']
        
        # Validate that passwords match
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('register'))

        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Insert new user into the users table
        try:
            query = "INSERT INTO users (customer_name, father_name, gender, mobile_number, email, nationality, password, security_question, security_answer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (customer_name, father_name, gender, mobile_number, email, nationality, password, security_question, security_answer))
            connection.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('user_login'))
        except mysql.connector.IntegrityError:
            flash('Username already exists. Please choose another.', 'error')
        finally:
            cursor.close()
            connection.close()

    return render_template('user_register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Check if the email is registered
            query = "SELECT security_question FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user:
                return render_template('reset_password.html', email=email, security_question=user['security_question'])
            else:
                flash("Email not found.", "danger")
                return redirect(url_for('forgot_password'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
        finally:
            cursor.close()
            connection.close()
    
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form['email']
    security_answer = request.form['security_answer']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']
    
    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch user's security answer from the database
        query = "SELECT security_answer FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user is None:
            flash("Email not found.", "danger")
            return redirect(url_for('forgot_password'))

        # Validate security answer
        if user['security_answer'].lower() != security_answer.lower():
            flash("Incorrect security answer.", "danger")
            return redirect(url_for('forgot_password'))

        # Validate that new passwords match
        if new_password != confirm_new_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('forgot_password'))

        # Update the user's password in the database (plain text)
        update_query = "UPDATE users SET password = %s WHERE email = %s"
        cursor.execute(update_query, (new_password, email))  # Remove hashing
        connection.commit()

        flash("Password reset successful! You can now login.", "success")
        return redirect(url_for('user_login'))
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
        return redirect(url_for('forgot_password'))
    finally:
        cursor.close()
        connection.close()

@app.route('/user_home')
def user_dashboard():
    if not session.get('user_logged_in'):
        return redirect(url_for('user_login'))
    
    return render_template('user_home.html')

@app.route('/user_logout')
def user_logout():
    session.pop('user_logged_in', None)
    return redirect(url_for('home'))

def fetch_available_rooms():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Query to get available rooms
    cursor.execute("SELECT room_number, room_type FROM rooms WHERE is_available = TRUE AND clean_status = 'Clean'")
    available_rooms = cursor.fetchall()

    # Ensure we have results
    if not available_rooms:
        return []

    # Map room numbers based on their prefixes
    categorized_rooms = []
    for room in available_rooms:
        room_number = str(room[0])  # Convert to string for prefix checking
        if room_number.startswith('1'):
            room_type = 'Single'
        elif room_number.startswith('2'):
            room_type = 'Double'
        elif room_number.startswith('3'):
            room_type = 'Suite'
        else:
            room_type = 'Unknown'  # Default for unexpected prefixes

        categorized_rooms.append({'room_number': room_number, 'room_type': room_type})

    cursor.close()
    connection.close()
    return categorized_rooms

@app.route('/get_rooms_by_type', methods=['GET'])
def get_rooms_by_type():
    room_type = request.args.get('room_type')
    
    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    query = "SELECT room_number FROM rooms WHERE room_type = %s AND is_available = TRUE AND clean_status = 'Clean'"
    cursor.execute(query, (room_type,))
    rooms = cursor.fetchall()
    
    cursor.close()
    connection.close()

    # Return room numbers as a JSON response
    return {'rooms': [room['room_number'] for room in rooms]}

@app.route('/book_room', methods=['GET', 'POST'])
def book_room():
    room_number = None

    if request.method == 'POST':
        # Generate a random customer ID if not provided
        customer_id = random.randint(1000, 9999)

        customer_id = request.form['customer_id']
        customer_name = request.form['customer_name']
        id_proof_type = request.form['id_proof_type']
        id_number = request.form['id_number']
        address = request.form['address']
        room_number = request.form.get('room_number', None)
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        number_of_guests = request.form['number_of_guests']
        special_requests = request.form['special_requests']
        terms_and_conditions = request.form.get('terms_and_conditions', False)

        if not terms_and_conditions:
            flash("You must agree to the terms and conditions to proceed.", "danger")
            return redirect(url_for('book_room'))

        # Determine room type based on room number prefix
        if room_number.startswith('1'):
            room_type = 'Single'
        elif room_number.startswith('2'):
            room_type = 'Double'
        elif room_number.startswith('3'):
            room_type = 'Suite'
        else:
            flash("Invalid room selection.", "danger")
            return redirect(url_for('book_room'))

        # Get room rate based on room type
        room_rate = ROOM_RATES.get(room_type)

        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        try:
            # Insert the booking into the room_booking table
            query = '''INSERT INTO room_booking
                (customer_id, customer_name, id_proof_type, id_number, address, room_type, room_number, check_in, check_out, number_of_guests, special_requests, room_rate) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

            cursor.execute(query,
                (customer_id, customer_name, id_proof_type, id_number, address, room_type, room_number, check_in, check_out, number_of_guests, special_requests, room_rate))
            
            connection.commit()
            booking_id = cursor.lastrowid

            # Update the room's availability status in the rooms table
            update_query = '''UPDATE rooms SET is_available = FALSE WHERE room_number = %s'''
            cursor.execute(update_query, (room_number,))
            connection.commit()

            flash("Room booked successfully!", "success")
            return redirect(url_for('generate_bill', booking_id=booking_id))
        
        except Exception as e:
            connection.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
        
        finally:
            cursor.close()
            connection.close()

    # Fetch available rooms from the database
    available_rooms = fetch_available_rooms()

    customer_id = random.randint(1000, 9999)
    return render_template('book_room.html', customer_id=customer_id, available_rooms=available_rooms, selected_room_number=room_number, ROOM_RATES=ROOM_RATES)

@app.route('/bill/<int:booking_id>')
def generate_bill(booking_id):
    
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Retrieve booking information by booking_id
    query = '''SELECT customer_name, room_type, room_number, room_rate, check_in, check_out
                FROM room_booking WHERE booking_id = %s'''
    cursor.execute(query, (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        flash("No booking found with this ID", "danger")
        return redirect(url_for('home'))

    customer_name, room_type, room_number, room_rate, check_in, check_out = booking

    # Check if check_in and check_out are datetime.date objects
    check_in_date = check_in if isinstance(check_in, datetime.date) else datetime.datetime.strptime(check_in, '%Y-%m-%d')
    check_out_date = check_out if isinstance(check_out, datetime.date) else datetime.datetime.strptime(check_out, '%Y-%m-%d')

    # Calculate number of days
    number_of_days = (check_out_date - check_in_date).days

    # Room cost calculation
    room_cost = number_of_days * float(room_rate)  # Ensure room_rate is float

    # Tax calculations (assuming 10% tax)
    tax_rate = 0.05
    sub_tax = room_cost * tax_rate  # Now this works
    paid_tax = 0.10 * room_cost

    # Total cost calculation
    total_cost = room_cost + sub_tax + paid_tax
    
    # Insert the bill into the database
    insert_bill_query = '''INSERT INTO room_bill (booking_id, room_cost, sub_tax, paid_tax, total_cost)
                            VALUES (%s, %s, %s, %s,%s)'''
    cursor.execute(insert_bill_query, (booking_id, room_cost, sub_tax, paid_tax, total_cost))
    connection.commit()
    
    # Fetch the generated bill_id
    bill_id = cursor.lastrowid
    
    cursor.close()
    connection.close()
    
    # # Redirect to payment page
    # return redirect(url_for('make_payment', bill_id=bill_id))

    return render_template('bill.html', action='make_payment', 
    customer_name=customer_name, room_type=room_type,
    room_number=room_number, room_rate=room_rate, number_of_days=number_of_days,
    room_cost=room_cost, sub_tax=sub_tax, paid_tax=paid_tax, total_cost=total_cost, 
    bill_id=bill_id)
    
@app.route('/download_bill/<int:bill_id>')
def download_bill(bill_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Fetch bill details
    query = '''SELECT rb.booking_id, rb.room_cost, rb.sub_tax, rb.paid_tax, rb.total_cost,
                        r.customer_name, r.room_type, r.room_number, r.check_in, r.check_out
                FROM room_bill rb
                JOIN room_booking r ON rb.booking_id = r.booking_id
                WHERE rb.bill_id = %s'''
    cursor.execute(query, (bill_id,))
    bill = cursor.fetchone()

    if not bill:
        flash("No bill found with this ID", "danger")
        return redirect(url_for('home'))

    # Unpack bill details
    (
        booking_id,
        room_cost,
        sub_tax,
        paid_tax,
        total_cost,
        customer_name,
        room_type,
        room_number,
        check_in,
        check_out,
    ) = bill

    # Generate PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    # Add content to the PDF
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, "Hotel Management System - Bill")
    pdf.line(50, 780, 550, 780)

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 750, f"Customer Name: {customer_name}")
    pdf.drawString(50, 730, f"Booking ID: {booking_id}")
    pdf.drawString(50, 710, f"Room Type: {room_type}")
    pdf.drawString(50, 690, f"Room Number: {room_number}")
    pdf.drawString(50, 670, f"Check-In Date: {check_in}")
    pdf.drawString(50, 650, f"Check-Out Date: {check_out}")

    pdf.line(50, 630, 550, 630)

    pdf.drawString(50, 610, f"Room Cost: ${room_cost:.2f}")
    pdf.drawString(50, 590, f"Sub Tax (5%): ${sub_tax:.2f}")
    pdf.drawString(50, 570, f"Paid Tax (10%): ${paid_tax:.2f}")
    pdf.drawString(50, 550, f"Total Cost: ${total_cost:.2f}")

    pdf.line(50, 530, 550, 530)
    pdf.drawString(50, 510, "Thank you for choosing us!")

    # Finalize PDF
    pdf.showPage()
    pdf.save()

    # Return the PDF as a downloadable file
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"bill_{bill_id}.pdf",
        mimetype="application/pdf"
    )

@app.route('/payment/<int:bill_id>', methods=['GET', 'POST'])
def make_payment(bill_id):
    
    # Use mysql.connector.connect() here
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Retrieve bill and customer details
    query = '''SELECT booking_id, total_cost FROM room_bill WHERE bill_id = %s'''
    cursor.execute(query, (bill_id,))
    bill = cursor.fetchone()

    if not bill:
        flash("Bill not found", "danger")
        return redirect(url_for('home'))

    booking_id, total_cost = bill

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        # Validate if payment_method is None or empty
        if not payment_method:
            flash("Please select a payment method.", "danger")
            
            # Re-render the payment form without executing the SQL query
            return render_template('payment.html', total_cost=total_cost, bill_id=bill_id)

        # Insert payment record into the payment table
        insert_payment_query = '''INSERT INTO payment (bill_id, booking_id, amount_paid, payment_method, payment_status) 
                                    VALUES (%s, %s, %s, %s, %s)'''
        cursor.execute(insert_payment_query, (bill_id, booking_id, total_cost, payment_method, 'Completed'))
        connection.commit()

        flash("Payment successful!", "success")
        return redirect(url_for('payment_confirmation', bill_id=bill_id))

    return render_template('payment.html', total_cost=total_cost, bill_id=bill_id)

@app.route('/payment_confirmation/<int:bill_id>')
def payment_confirmation(bill_id):
    connection = mysql.connector.connect(**db_config)  # Use mysql.connector.connect()
    cursor = connection.cursor()

    # Fetch payment details
    query = '''SELECT payment_id, amount_paid, payment_method, payment_date 
                FROM payment WHERE bill_id = %s'''
    cursor.execute(query, (bill_id,))
    payment = cursor.fetchone()

    if not payment:
        flash("Payment not found", "danger")
        return redirect(url_for('home'))

    payment_id, amount_paid, payment_method, payment_date = payment

    return render_template('payment_confirmation.html', payment_id=payment_id, amount_paid=amount_paid,
                            payment_method=payment_method, payment_date=payment_date)

@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant_menu():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch menu items
    cursor.execute("SELECT * FROM restaurant WHERE availability = 'Available'")
    menu_items = cursor.fetchall()

    if request.method == 'POST':
        users_id = session.get('users_id')  # Assume user is logged in
        if not users_id:
            flash("You must be logged in to place an order.", "danger")
            return redirect(url_for('users_login'))

        # Iterate through all menu items and process orders
        orders = []
        for item in menu_items:
            item_id = item[0]
            quantity = request.form.get(f'quantity_{item_id}')
            if quantity and int(quantity) > 0:
                # Fetch item price
                cursor.execute("SELECT item_price FROM restaurant WHERE item_id = %s", (item_id,))
                item_price = cursor.fetchone()[0]
                total_price = int(quantity) * item_price

                # Add order to the list
                orders.append((users_id, item_id, quantity, total_price))

        # Insert all orders into the database
        if orders:
            order_query = '''INSERT INTO orders (users_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)'''
            cursor.executemany(order_query, orders)
            conn.commit()
            
            order_id = cursor.lastrowid
            
            flash("Order placed successfully!", "success")
            return redirect(url_for('generate_user_bill', order_id=order_id))
        else:
            flash("No items selected to order.", "danger")

    # Close the connection
    cursor.close()
    conn.close()

    return render_template('restaurant_menu.html', menu_items=menu_items)

@app.route('/generate_bill/<int:order_id>', methods=['GET'])
def generate_user_bill(order_id):
    # Corrected line
    conn = mysql.connector.connect(**db_config)  # Use mysql.connector.connect() instead of mysql.connect()

    cursor = conn.cursor()

    # Fetch order details from the orders table
    cursor.execute('''SELECT o.order_id, o.users_id, r.item_name, o.quantity, 
                        r.item_price FROM orders o
                        JOIN restaurant r ON o.item_id = r.item_id
                        WHERE o.order_id = %s''', (order_id,))
    order_details = cursor.fetchall()

    # Calculate the total price of the order
    total_amount = 0
    for detail in order_details:
        total_amount += detail[3] * detail[4]  # quantity * item_price

    # Apply tax (for example, 5%)
    tax = total_amount * Decimal('0.05')
    final_amount = total_amount + tax

    # Insert the bill into the restaurant_bill table
    cursor.execute('''INSERT INTO restaurant_bill (users_id, order_id, total_amount, 
                        tax, final_amount) VALUES (%s, %s, %s, %s, %s)''', 
                    (order_details[0][1], order_id, total_amount, tax, final_amount))
    conn.commit()

    # Fetch the bill from the restaurant_bill table
    cursor.execute('SELECT * FROM restaurant_bill WHERE order_id = %s', (order_id,))
    bill = cursor.fetchone()

    # Close the database connection
    conn.close()

    return render_template('restaurant_bill.html', order_details=order_details, bill=bill)

@app.route('/process_payment/<int:bill_id>', methods=['POST'])
def process_payment(bill_id):
    payment_method = request.form['payment_method']
    payment_amount = float(request.form['payment_amount'])

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch the bill details
    cursor.execute('SELECT * FROM restaurant_bill WHERE bill_id = %s', (bill_id,))
    bill = cursor.fetchone()
    
    # Debugging: Print the bill_id and the fetched bill data
    print(f"Looking for bill with ID: {bill_id}")
    print(f"Bill found: {bill}")  # This will print None if no bill was found
    
    if bill is None:
        conn.close()
        return "Bill not found.", 404

    if payment_amount == bill[5]:  # Ensure payment amount matches the final bill amount
        if payment_method == 'stripe':
            # Handle Stripe Payment Processing
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(payment_amount * 100),  # Amount in cents
                    currency='usd',
                    payment_method=payment_method,
                    confirm=True
                )

                # Update bill status to Paid
                cursor.execute('''UPDATE restaurant_bill SET status = 'Paid' WHERE bill_id = %s''', (bill_id,))
                conn.commit()

                # Insert payment details into the payments table
                cursor.execute('''INSERT INTO payments (bill_id, payment_method, amount_paid) 
                                    VALUES (%s, %s, %s)''', (bill_id, payment_method, payment_amount))
                conn.commit()

                conn.close()

                return redirect(url_for('payment_success', bill_id=bill_id))

            except stripe.error.StripeError as e:
                conn.close()
                return f"Payment failed: {e.user_message}", 400

        else:
            # Handle Non-Stripe Payment (e.g., Cash)
            cursor.execute('''UPDATE restaurant_bill SET status = 'Paid' WHERE bill_id = %s''', (bill_id,))
            conn.commit()

            # Insert payment details into payments table
            cursor.execute('''INSERT INTO payments (bill_id, payment_method, amount_paid) 
                                VALUES (%s, %s, %s)''', (bill_id, payment_method, payment_amount))
            conn.commit()

            conn.close()

            return redirect(url_for('payment_success', bill_id=bill_id))

    else:
        conn.close()
        return "Payment failed. Amount doesn't match the bill.", 400

@app.route('/payment_success/<int:bill_id>')
def payment_success(bill_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch the bill details
    cursor.execute('SELECT * FROM restaurant_bill WHERE bill_id = %s', (bill_id,))
    bill = cursor.fetchone()

    conn.close()
    return render_template('payment_success.html', bill=bill)

@app.route('/user/orders', methods=['GET'])
def view_orders():
    # Establish the database connection
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    users_id = session.get('users_id')  # Assume user is logged in
    
    if not users_id:
        flash("You must be logged in to view orders.", "danger")
        return redirect(url_for('user_login'))  # Redirect to login page if not logged in

    # Fetch user's orders
    orders_query = '''SELECT orders.order_id, restaurant.item_name, orders.quantity, 
                        orders.total_price, orders.order_date 
                        FROM orders 
                        JOIN restaurant ON orders.item_id = restaurant.item_id 
                        WHERE orders.users_id = %s'''
    cursor.execute(orders_query, (users_id,))
    orders = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    return render_template('user_orders.html', orders=orders)

@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
    # No login check, anyone can submit a review
    # Establish database connection
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get review data from the form
        customer_name = request.form['customer_name']
        rating = int(request.form['rating'])
        review = request.form['review']
        
        # Get the logged-in user's ID (if available)
        users_id = session.get('users_id', None)  # Assuming user ID is stored in session

        # If users_id is None, it means the user is not logged in, so we set it to NULL
        if users_id is None:
            users_id = None

        # Check if the required fields are filled
        if not customer_name or rating == 0 or not review:
            flash('All fields are required!', 'danger')
            return redirect(url_for('add_review'))

        # Insert the review into the database
        cursor.execute('''
            INSERT INTO reviews (users_id, customer_name, rating, review)
            VALUES (%s, %s, %s, %s)
        ''', (users_id, customer_name, rating, review))
        conn.commit()

        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('view_reviews'))

    cursor.close()
    conn.close()

    return render_template('add_review.html')

@app.route('/view_reviews')
def view_reviews():
    # Establish database connection
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch all reviews
    cursor.execute('SELECT customer_name, rating, review, created_at FROM reviews ORDER BY created_at DESC')
    reviews = cursor.fetchall()

    # Calculate average rating
    cursor.execute('SELECT AVG(rating) FROM reviews')
    avg_rating = cursor.fetchone()[0]
    conn.close()

    return render_template('view_reviews.html', reviews=reviews, avg_rating=avg_rating)

if __name__ == '__main__':
    app.run(debug=True)
