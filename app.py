from flask import Flask, render_template, request, jsonify, session, redirect, url_for, current_app
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
import requests
from flask import flash

app = Flask(__name__)
babel = Babel(app)

# Define the languages you want to support
LANGUAGES = ['en', 'fr']
app.config['LANGUAGES'] = LANGUAGES

# Configure SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable SQLAlchemy track modifications
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)  # Ensure phone numbers are unique
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

@babel.localeselector
def get_locale():
    # Use language from session, or default to 'en'
    return session.get('language', 'en')

# --------------------------------------------------------------------------------
  
@app.route('/')
def indi():
    return render_template('welcome.html')

# --------------------------------------------------------------------------------

@app.route('/crop_recommendations')
def crop_recommendations():
    # Define hardcoded data for cities and their best crops to grow
    crop_recommendations = [
        {'city': 'City1', 'best_crop': 'Wheat'},
        {'city': 'City2', 'best_crop': 'Rice'},
        {'city': 'City3', 'best_crop': 'Corn'},
        # Add more data as needed
    ]
    return render_template('crop_recommendations.html', crop_recommendations=crop_recommendations)

# --------------------------------------------------------------------------------

@app.route('/signin', methods=['GET', 'POST'])
def signin_page():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        password = request.form['password']

        # Query the database to find the user with the provided phone number
        user = User.query.filter_by(phone_number=phone_number).first()

        if user and user.password == password:
            # User found and password matches
            session['user_id'] = user.id  # Store user's ID in session
            return redirect(url_for('profile_page'))  # Redirect to user profile page
        else:
            # User not found or password does not match
            flash('Invalid phone number or password. Please try again.', 'error')

    return render_template('signin.html')

# -------------------------------------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
@app.route('/signup')
def signup_page():
    # Handle signup page logic here
    return render_template('signup.html')

# --------------------------------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        location = request.form['location']
        phone_number = request.form['phone_number']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username or email already exists in the database
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists. Please choose another one.', 'error')
            return redirect(url_for('register_page'))

        # Create a new user object
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            location=location,
            phone_number=phone_number,
            username=username,
            email=email,
            password=password
        )

        # Add the new user to the database
        with app.app_context():  # Use app context to create database tables
            db.session.add(new_user)
            db.session.commit()

        # Pass user's name to the welcome.html template
        user_name = f'{first_name} {last_name}'

        # Redirect to the welcome page with the user's name
        return render_template('welcome.html', user_name=user_name)

    return render_template('register.html')

# ---------------------------------------------------------------------------------------------------

@app.route('/soil_profile')
def soil_profile():
    return render_template('soil_profile.html')

# ---------------------------------------------------------------------------------------

@app.route('/next_page')
def next_page():
    # Add logic for handling the next page
    return render_template('next_page.html')

# ---------------------------------------------------------------------------------------

@app.route('/show_weather')
def show_weather():
    # Add the logic to display weather information
    return render_template('indi.html')

# ---------------------------------------------------------------------------------------

@app.route('/government_schemes')
def government_schemes():
    return render_template('government_schemes.html')
  
# -------------------------------------------------------------------------------------

@app.route('/set_language', methods=['GET'])
def set_language():
    language = request.args.get('language', 'en')
    session['language'] = language  # Store the selected language in the session
    return jsonify({'status': 'success', 'language': language})
# ---------------------------------------------------------------------------------------


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        current_weather, forecast_weather, error_message = get_weather_data(city)
        return render_template('indi.html', current_weather=current_weather, forecast_weather=forecast_weather, error_message=error_message)

    return render_template('indi.html', current_weather=None, forecast_weather=None, error_message=None)
# ---------------------------------------------------------------------------------------

def get_weather_data(city):
    api_key = '759f8c8419a3090b77dface5eb5e88aa'
    current_url = 'http://api.openweathermap.org/data/2.5/weather'
    forecast_url = 'http://api.openweathermap.org/data/2.5/forecast'
    
    # Current weather data
    current_params = {'q': city, 'appid': api_key, 'units': 'metric'}
    current_response = requests.get(current_url, params=current_params)
    current_data = current_response.json()

    # Forecast data
    forecast_params = {'q': city, 'appid': api_key, 'units': 'metric'}
    forecast_response = requests.get(forecast_url, params=forecast_params)
    forecast_data = forecast_response.json()

    if current_response.status_code == 200 and forecast_response.status_code == 200:
        current_weather_info = {
            'city': current_data['name'],
            'temperature': current_data['main']['temp'],
            'description': current_data['weather'][0]['description'],
            'icon': current_data['weather'][0]['icon'],
        }

        forecast_weather_info = []
        for forecast in forecast_data['list']:
            forecast_info = {
                'datetime': forecast['dt_txt'],
                'temperature': forecast['main']['temp'],
                'description': forecast['weather'][0]['description'],
                'icon': forecast['weather'][0]['icon'],
            }
            forecast_weather_info.append(forecast_info)

        return current_weather_info, forecast_weather_info, None  # No error

    # Handle errors
    error_message = f"Error: {current_response.status_code} - {current_data.get('message', 'Unknown error')}"
    return None, None, error_message

if __name__ == '__main__':
    with app.app_context():  # Ensure app context is active
        db.create_all()  # Create the database tables
    app.secret_key = 'your_secret_key'  # Set a secret key for session management
    app.run(debug=True)
