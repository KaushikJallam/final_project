from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select,not_
from flask_migrate import Migrate
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from dotenv import load_dotenv
import socket
from forms import PasswordResetForm,ResetPasswordForm,PassengerRegistrationForm,PassengerSignInForm,DriverRegistrationForm,DriverSignInForm,QuotationForm



app = Flask(__name__)

mailUser = os.environ.get('MAIL_USERNAME')
password = os.environ.get('MAIL_PASSWORD')
mailId = os.environ.get('MAIL_ID')
app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Configure Flask-Mail settings
app.config['MAIL_SERVER'] = 'gsmtp.gmail.com'
app.config['MAIL_PORT'] = 465  # Replace with your email server's port number
# app.config['MAIL_PORT'] = 587  # Replace with your email server's port number
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_PORT'] = 25
# app.config['MAIL_USE_TLS'] = True
app.config['MAIL_TIMEOUT'] = 120
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_ID')
mail = Mail(app)
socket.setdefaulttimeout(app.config['MAIL_TIMEOUT'])

from models import User,Ride,Trip,Quotation,Notification

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/driver')
def driver():
    print(f'---->{os.environ.get("MAIL_PASSWORD")}')
    return render_template('driver_page.html')

@app.route('/passenger')
def passenger():
    return render_template('passenger_page.html')
@app.route('/driver/register', methods=['GET', 'POST'])
def driver_register():
    form = DriverRegistrationForm()
    if form.validate_on_submit():
        # Process the driver registration form data
        username = form.name.data
        email = form.email.data
        password = form.password.data

        # Check if a user with the same email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use. Please use a different email.', 'danger')
            return redirect(url_for('driver_register'))

        # Create a new driver instance and set the password
        new_driver = User(username=username, email=email, password=password, user_type='driver')

        # Add the driver to the database and commit the changes
        db.session.add(new_driver)
        db.session.commit()

        flash('Driver registration successful! You can now sign in.', 'success')
        return redirect(url_for('driver_login'))

    return render_template('driver_register.html', form=form)

@app.route('/passenger/register', methods=['GET', 'POST'])
def passenger_register():
    form = PassengerRegistrationForm()
    if form.validate_on_submit():
        # Process the passenger registration form data
        username = form.name.data
        email = form.email.data
        password = form.password.data

        # Check if a user with the same email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use. Please use a different email.', 'danger')
            return redirect(url_for('passenger_register'))

        # Create a new passenger instance and set the password
        new_passenger = User(username=username, email=email, password=password, user_type='passenger')

        # Add the passenger to the database and commit the changes
        db.session.add(new_passenger)
        db.session.commit()

        flash('Passenger registration successful! You can now sign in.', 'success')
        return redirect(url_for('passenger_login'))

    return render_template('passenger_register.html', form=form)

@app.route('/driver/login', methods=['GET', 'POST'])
def driver_login():
    if current_user.is_authenticated:
        # If the driver is already logged in, redirect them to the driver dashboard
        return redirect(url_for('driver_dashboard'))  # Replace 'driver_dashboard' with your desired route for the driver dashboard
    form = DriverSignInForm()
    if request.method == 'POST':
        # Process the driver sign-in form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Verify the login credentials and check the user_type as 'driver'
        driver = User.query.filter_by(email=email, user_type='driver').first()
        if driver and driver.check_password(password):
            login_user(driver)
            flash('Driver login successful!', 'success')
            return redirect(url_for('driver_dashboard'))  # Replace 'driver_dashboard' with your desired route for the driver dashboard
        else:
            flash('Invalid email or password', 'danger')

    return render_template('driver_login.html',form=form)




@app.route('/passenger/login', methods=['GET', 'POST'])
def passenger_login():
    if current_user.is_authenticated:
        # If the passenger is already logged in, redirect them to the passenger dashboard
        return redirect(url_for('passenger_dashboard'))  # Replace 'passenger_dashboard' with your desired route for the passenger dashboard
    form = PassengerSignInForm()
    if request.method == 'POST':
        # Process the passenger sign-in form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Verify the login credentials and check the user_type as 'passenger'
        passenger = User.query.filter_by(email=email, user_type='passenger').first()
        if passenger and passenger.check_password(password):
            login_user(passenger)
            flash('Passenger login successful!', 'success')
            return redirect(url_for('passenger_dashboard'))  # Replace 'passenger_dashboard' with your desired route for the passenger dashboard
        else:
            flash('Invalid email or password', 'danger')

    return render_template('passenger_login.html',form = form)

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@login_required
@app.route('/driver_dashboard', methods=['GET', 'POST'])
def driver_dashboard():
    # Fetch available trips without a quotation using a subquery
    subquery = db.session.query(Quotation.trip_id)
    # trip_id_column = subquery.c.trip_id 
    available_trips = db.session.query(Trip).outerjoin(Quotation).filter(Quotation.id.is_(None)).filter(Trip.driver_id.is_(None)).all()
    print(f'************************available trips****************** {available_trips}')
    quotation_form = QuotationForm()
    if quotation_form.validate_on_submit():
        trip_id = quotation_form.trip_id.data
        quotation_amount = quotation_form.quotation_amount.data

        # Retrieve the trip for which the driver is submitting the quotation
        ride = Ride.query.get(trip_id)
        print(f'@@@@@@@@ {ride}')

        # Check if the trip is available for quotation and not assigned to the driver
        if ride and not ride.quotation and not ride.driver_id == current_user.id:
            # Create a new quotation object
            quotation = Quotation(driver_id=current_user.id, passenger_id=ride.passenger.id, trip_id=ride.id,
                                  quotation_amount=quotation_amount, status="Pending")
            db.session.add(quotation)
            db.session.commit()

            # Update the ride's driver_id to the current driver
            ride.driver_id = current_user.id
            db.session.commit()

            flash('Quotation submitted successfully!', 'success')
            return redirect(url_for('driver_dashboard'))
        else:
            if not ride or ride.quotation:
                flash('This trip is no longer available for quotation.', 'warning')
            elif ride.driver_id == current_user.id:
                flash("You can't send a quotation for your own ride.", 'warning')

    print(f'===============available trips {len(available_trips)}')

    return render_template('driver_dashboard.html', available_trips=available_trips, quotation_form=quotation_form)

@login_required
@app.route('/passenger_dashboard')
def passenger_dashboard():
    print(f'**************************')
    if request.method == 'POST':
        # Get the "from" and "to" inputs from the form
        from_location = request.form.get('from_location')
        to_location = request.form.get('to_location')

        # Create a new upcoming ride instance and save it in the database
        new_ride = Ride(passenger_id=current_user.id, driver_id=None, from_location=from_location, to_location=to_location)
        db.session.add(new_ride)
        db.session.commit()

        flash('New upcoming ride created successfully!', 'success')

    # Retrieve upcoming rides for the current passenger
    upcoming_rides = [ride for ride in current_user.rides_as_passenger if ride.driver_id is None]
    quotations = Quotation.query.filter_by(passenger_id=current_user.id, status='Pending').all()


    return render_template('passenger_dashboard.html',upcoming_rides=upcoming_rides,quotations=quotations)

@app.route('/driver/logout')
@login_required
def driver_logout():
    logout_user()  # Log out the user
    return redirect(url_for('driver_login'))


@app.route('/passenger/logout')
@login_required
def passenger_logout():
    logout_user()  # Log out the user
    return redirect(url_for('passenger_login'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = PasswordResetForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()  # Assuming email is used for password reset
        if user:
            reset_token = user.generate_reset_token()
            # Send the reset token to the user's email or mobile number (implement this logic)
            print(f'-----------------{user.email},{reset_token}')
            send_reset_token_email(user.email, reset_token)
            flash('Password reset token sent. Please check your email or mobile for further instructions.', 'info')
            return redirect(url_for('index'))
        else:
            flash('User with provided email or mobile number does not exist.', 'danger')

    return render_template('forgot_password.html', form=form)

def send_reset_token_email(email, token):
    print(f'send_reset_token')
    subject = 'Password Reset Request'
    reset_url = url_for('reset_password', reset_token=token, _external=True)
    body = f'Please use the following link to reset your password: {reset_url}'
    sender_email = mailId
    print(f'subject:{subject} body:{body} sender email: {mailId}')
    
    msg = Message(subject=subject, body=body, sender=sender_email, recipients=[email])
    print(f'------------------------{msg}------------------')
    mail.send(msg)



@app.route('/reset_password/<string:reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):
    user = User.query.filter_by(reset_token=reset_token).first()
    if not user or datetime.utcnow() > user.reset_token_expiration:
        flash('Invalid or expired reset token. Please request a new password reset.', 'danger')
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        flash('Your password has been reset successfully! You can now log in with your new password.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', form=form)

@app.route('/create_ride', methods=['POST'])
@login_required
def create_ride():
    from_location = request.form['from_location']
    to_location = request.form['to_location']

    # Create a new Trip object with the passenger_id set to the current user's id
    # Set driver_id to None initially
    new_trip = Trip(from_location=from_location, to_location=to_location, passenger_id=current_user.id, driver_id=None)
    db.session.add(new_trip)
    db.session.commit()

    # Create a new Ride object and save it to the database
    new_ride = Ride(passenger_id=current_user.id, from_location=from_location, to_location=to_location)
    db.session.add(new_ride)
    db.session.commit()

    return render_template('create_ride.html', ride=new_ride)
@app.route('/available_rides')
@login_required  # Ensure only authenticated users (drivers) can access this page
def available_rides():
    # Retrieve all rides where the driver_id is None, indicating they are not assigned to any driver yet
    available_rides = Ride.query.filter(Ride.driver_id == None).all()
    return render_template('available_rides.html', rides=available_rides)


@app.route('/accept_ride/<int:ride_id>', methods=['POST'])
@login_required
def accept_ride(ride_id):
    # Get the current authenticated user (driver)
    driver = current_user

    # Find the ride with the given ride_id
    ride = Ride.query.get(ride_id)

    # Check if the ride is available for assignment and not assigned to the driver
    if ride and not ride.driver_id and ride.trip.driver_id is None:
        # Assign the ride to the driver by updating the driver_id column in the corresponding Trip object
        ride.trip.driver_id = driver.id
        db.session.commit()
        quotation_amount = float(request.form['quotation_amount'])
        new_quotation = Quotation(driver_id=driver.id, passenger_id=ride.passenger_id, trip_id=ride.trip_id, quotation_amount=quotation_amount)
        db.session.add(new_quotation)
        db.session.commit()

        passenger = User.query.get(ride.passenger_id)
        notification_message = f"You have received a new quotation from {driver.username}"
        notification = Notification(passenger_id=passenger.id, driver_id=driver.id, trip_id=ride.trip_id, quotation_id=new_quotation.id, message=notification_message)
        db.session.add(notification)
        db.session.commit()

        # Redirect the driver back to the available rides page or their dashboard
        return redirect(url_for('available_rides'))
    else:
        # Handle cases where the ride is not available or is already assigned to a driver
        flash('This ride is no longer available for assignment.', 'warning')
        return redirect(url_for('available_rides'))
    

@app.route('/passenger_dashboard/accept_quotation/<int:quotation_id>', methods=['POST'])
def accept_quotation(quotation_id):
    # Retrieve the quotation by ID
    quotation = Quotation.query.get(quotation_id)
    if quotation:
        # Mark the quotation as accepted (you may have additional logic here)
        quotation.status = "Accepted"
        db.session.commit()
        flash('Quotation accepted successfully!', 'success')
    else:
        flash('Quotation not found!', 'error')
    
    return redirect('/passenger_dashboard')

@app.route('/passenger_dashboard/reject_quotation/<int:quotation_id>', methods=['POST'])
def reject_quotation(quotation_id):
    # Retrieve the quotation by ID
    quotation = Quotation.query.get(quotation_id)
    if quotation:
        # Mark the quotation as rejected (you may have additional logic here)
        quotation.status = "Rejected"
        db.session.commit()
        flash('Quotation rejected successfully!', 'success')
    else:
        flash('Quotation not found!', 'error')
    
    return redirect('/passenger_dashboard')

@app.route('/ride_history')
@login_required
def ride_history():
    # Retrieve accepted and rejected rides for the current passenger
    accepted_rides = Ride.query.filter_by(passenger_id=current_user.id, status='Accepted').all()
    rejected_rides = Ride.query.filter_by(passenger_id=current_user.id, status='Rejected').all()

    return render_template('ride_history.html', accepted_quotations=accepted_quotations, rejected_quotations=rejected_quotations)

if __name__ == '__main__':
    app.run(debug=True)

