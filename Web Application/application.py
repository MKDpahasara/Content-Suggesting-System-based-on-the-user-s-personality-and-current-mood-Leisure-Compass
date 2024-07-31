from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
import numpy as np
from tensorflow.keras.models import load_model
import pandas as pd
import cv2
import boto3
import base64
import os
import json
import sqlite3
from datetime import datetime
import random
from db import get_db 

# Third-party libraries
 
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from db import init_db_command
from user import User

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

# Configuration
GOOGLE_CLIENT_ID = "Google Client ID"
GOOGLE_CLIENT_SECRET = "Google Client Secret"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

application = Flask(__name__)
application.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
application.config['SESSION_TYPE'] = 'filesystem'
Session(application)

# User session management setup
login_manager = LoginManager()
login_manager.init_app(application)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Load the machine learning model
loaded_model = load_model("my_model3.h5")

global movie_data_array
global series_data_array

# Labels for personality traits
labels = {
    0: 'agreeableness',
    1: 'conscientiousness',
    2: 'extroversion',
    3: 'neuroticism',
    4: 'openness'
}

# Questions for personality traits
questions = {
    'EXT1': 'I am the life of the party.',
    'EXT2': "I don't talk a lot.",
    'EXT3': 'I feel comfortable around people.',
    'EXT4': 'I keep in the background.',
    'EXT5': 'I start conversations.',
    'EXT6': 'I have little to say.',
    'EXT7': 'I talk to a lot of different people at parties.',
    'EXT8': "I don't like to draw attention to myself.",
    'EXT9': "I don't mind being the center of attention.",
    'EXT10': 'I am quiet around strangers.',
    'EST1': 'I get stressed out easily.',
    'EST2': 'I am relaxed most of the time.',
    'EST3': 'I worry about things.',
    'EST4': 'I seldom feel blue.',
    'EST5': 'I am easily disturbed.',
    'EST6': 'I get upset easily.',
    'EST7': 'I change my mood a lot.',
    'EST8': 'I have frequent mood swings.',
    'EST9': 'I get irritated easily.',
    'EST10': 'I often feel blue.',
    'AGR1': 'I feel little concern for others.',
    'AGR2': 'I am interested in people.',
    'AGR3': 'I insult people.',
    'AGR4': "I sympathize with others' feelings.",
    'AGR5': "I am not interested in other people's problems.",
    'AGR6': 'I have a soft heart.',
    'AGR7': 'I am not really interested in others.',
    'AGR8': 'I take time out for others.',
    'AGR9': "I feel others' emotions.",
    'AGR10': 'I make people feel at ease.',
    'CSN1': 'I am always prepared.',
    'CSN2': 'I leave my belongings around.',
    'CSN3': 'I pay attention to details.',
    'CSN4': 'I make a mess of things.',
    'CSN5': 'I get chores done right away.',
    'CSN6': 'I often forget to put things back in their proper place.',
    'CSN7': 'I like order.',
    'CSN8': 'I shirk my duties.',
    'CSN9': 'I follow a schedule.',
    'CSN10': 'I am exacting in my work.',
    'OPN1': 'I have a rich vocabulary.',
    'OPN2': 'I have difficulty understanding abstract ideas.',
    'OPN3': 'I have a vivid imagination.',
    'OPN4': 'I am not interested in abstract ideas.',
    'OPN5': 'I have excellent ideas.',
    'OPN6': 'I do not have a good imagination.',
    'OPN7': 'I am quick to understand things.',
    'OPN8': 'I use difficult words.',
    'OPN9': 'I spend time reflecting on things.',
    'OPN10': 'I am full of ideas.'
}


df = pd.read_csv("processed_data movies10000.csv")
df2 = pd.read_csv("TMDB_tv_preprocessed_data2.csv")

df2 = df2[df2['adult'] == False]

# Reset index after dropping rows
df2.reset_index(drop=True, inplace=True)

# Personality traits mapping to movie genres
personality_traits = {
    'extroversion': ['Comedy', 'Romance', 'Action', 'Adventure', 'Science Fiction', 'Music'],
    'agreeableness': ['Romance', 'Drama', 'Family', 'Comedy', 'Music'],
    'conscientiousness': ['History', 'Thriller', 'Drama', 'Science Fiction'],
    'neuroticism': ['Horror', 'Drama', 'Thriller', 'Mystery', 'Science Fiction', 'Fantasy'],
    'openness': ['Fantasy', 'Thriller', 'Science Fiction', 'Adventure', 'Mystery', 'Drama', 'Animation', 'Comedy']
}

# Function to get movie recommendations based on personality trait

def get_movies_by_personality(personality_trait):
    if personality_trait in personality_traits:
        preferred_genres = personality_traits[personality_trait]
        filtered_data = df[df['first_genre'].isin(preferred_genres) | df['Second_Genre'].isin(preferred_genres)]
        return filtered_data[['Movie_id', 'title', 'first_genre', 'Second_Genre']]
    else:
        return pd.DataFrame()
    
# Function to get TV Series recommendations based on personality trait

def get_series_by_personality(personality_trait):
    if personality_trait in personality_traits:
        preferred_genres = personality_traits[personality_trait]
        filtered_data = df2[df2['first_genre'].isin(preferred_genres) | df2['second_genre'].isin(preferred_genres)]
        return filtered_data[['id','name','first_genre', 'second_genre']]
         # return filtered_data[['id','name','first_genre', 'second_genre']].sample(n=100, random_state=3)
    else:
        return pd.DataFrame()
    
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@application.route('/')
def index():
    return render_template('index.html')

#  --------------------------------------------------------------------------------------------------
@application.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
        prompt="select_account"
    )
    return redirect(request_uri)

@application.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    
    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))

@application.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("index"))
#  --------------------------------------------------------------------------------------------------


@application.route('/error')
def error():
    return render_template('error.html')

@application.route('/start')
@login_required
def start():
    return render_template('start.html', questions=questions)

# Create a folder named "mood_detection" to store captured images
MOOD_DETECTION_FOLDER = 'mood_detection'
if not os.path.exists(MOOD_DETECTION_FOLDER):
    os.makedirs(MOOD_DETECTION_FOLDER)


# Helper function to convert data URL to image
def convert_data_url_to_image(data_url):
    encoded_data = data_url.split(',')[1]
    decoded_data = base64.b64decode(encoded_data)
    image_array = np.frombuffer(decoded_data, dtype=np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)


# Function to save captured mood image with a unique filename
def save_captured_mood_image(data_url):
    try:
        # Generate a unique filename using current timestamp and session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = session.get('id', 'unknown_session')
        filename = f"captured_mood_{session_id}_{timestamp}.jpg"

        # Specify the folder path where the images should be saved
        filepath = os.path.join(MOOD_DETECTION_FOLDER, filename)

        # Decode the data URL and save the image to a file
        encoded_data = data_url.split(',')[1]
        decoded_data = base64.b64decode(encoded_data)
        with open(filepath, 'wb') as f:
            f.write(decoded_data)

        return filepath
    except Exception as e:
        print(f"Error saving captured mood image: {str(e)}")
        return None





# Get the user mood
def get_mood(captured_mood):
    try:
        # Convert the captured mood from data URL to image and save it
        captured_mood_image = convert_data_url_to_image(captured_mood)
        image_path = 'captured_mood_image.jpg'
        cv2.imwrite(image_path, captured_mood_image)

        # Use AWS Rekognition to analyze the mood
        aws_access_key_id = 'AWS Access Key'
        aws_secret_access_key = 'AWS Access Secret Key'
        region_name = 'Your Region'
        rekognition = boto3.client('rekognition', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()

        response = rekognition.detect_faces(Image={'Bytes': image_data}, Attributes=['ALL'])

        # Extract mood information from the response
        mood = "UNKNOWN"
        if 'FaceDetails' in response and len(response['FaceDetails']) > 0:
            emotions = response['FaceDetails'][0]['Emotions']
            dominant_emotion = max(emotions, key=lambda x: x['Confidence'])
            detected_mood = dominant_emotion['Type']
            
            mood = detected_mood
        return mood
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return "CALM"  # Return a default value in case of an error




@application.route('/recommend', methods=['POST'])
@login_required
def recommend():
    if current_user.is_authenticated:
        # Fetch the user's personality label from the database
        user = User.get(current_user.id)
        if user and user.personality_label:
            predicted_label = user.personality_label
            print(predicted_label)
        else:
            data_dict = {}
            for trait in ['EXT', 'EST', 'AGR', 'CSN', 'OPN']:
                for i in range(1, 11):
                    code = f'{trait}{i}'
                    response = request.form.get(code)

                    # print(response)

                    while True:
                        if response.isdigit() and 1 <= int(response) <= 5:
                            break
                        else:
                            response = request.form.get(code)

                    data_dict[code] = int(response)

            # Convert data_dict to input_data for the model
            input_data = np.array([list(data_dict.values())])

            # Make predictions with the loaded model
            predictions = loaded_model.predict(input_data)

            # Get the predicted personality trait label
            predicted_class_index = np.argmax(predictions)
            predicted_label = labels[predicted_class_index]

            # Save the predicted personality label to the database
            db = get_db()
            db.execute(
                'UPDATE user SET personality_label = ? WHERE id = ?',
                (predicted_label, current_user.id)
            )
            db.commit()
        try:
            # Get movie recommendations based on personality trait
            movies_by_personality = get_movies_by_personality(predicted_label)
            
            # Get Series recommendations based on personality trait
            series_by_personality = get_series_by_personality(predicted_label)


            captured_mood = request.form.get('mood_input') 
            # print(user_mood)

            def get_movies_by_mood(mood):
                mood_genres = {
                    'HAPPY': ['Action', 'Adventure', 'Animation', 'Romance'],
                    'SAD': ['Drama', 'Comedy', 'Family', 'Animation', 'Music'],
                    'ANGRY': ['Action', 'Thriller', 'Horror', 'Drama'],
                    'CONFUSED': ['Mystery', 'Science Fiction', 'Thriller', 'Fantasy'],
                    'SURPRISED': ['Mystery', 'Thriller', 'Action', 'Comedy'],
                    'CALM': ['Drama', 'Romance', 'Family', 'Animation', 'Music'],
                    'FEAR': ['Horror', 'Thriller', 'Mystery', 'Action']
                }

                if mood.upper() in mood_genres:
                    selected_genres = mood_genres[mood.upper()]
                    filtered_data = movies_by_personality[movies_by_personality['first_genre'].isin(selected_genres) | movies_by_personality['Second_Genre'].isin(selected_genres)]
                    return filtered_data[['Movie_id', 'title', 'first_genre', 'Second_Genre']]
                else:
                    return pd.DataFrame()

            def get_series_by_mood(mood):
                mood_genres = {
                    'HAPPY': ['Action', 'Adventure', 'Animation', 'Romance'],
                    'SAD': ['Drama', 'Comedy', 'Family', 'Animation', 'Music'],
                    'ANGRY': ['Action', 'Thriller', 'Horror', 'Drama'],
                    'CONFUSED': ['Mystery', 'Science Fiction', 'Thriller', 'Fantasy'],
                    'SURPRISED': ['Mystery', 'Thriller', 'Action', 'Comedy'],
                    'CALM': ['Drama', 'Romance', 'Family', 'Animation', 'Music'],
                    'FEAR': ['Horror', 'Thriller', 'Mystery', 'Action']
                }

                if mood.upper() in mood_genres:
                    selected_genres = mood_genres[mood.upper()]
                    
                    filtered_data = series_by_personality[series_by_personality['first_genre'].isin(selected_genres) | series_by_personality['second_genre'].isin(selected_genres)]
                    return filtered_data[['id','name','first_genre', 'second_genre']]
                else:
                    return pd.DataFrame()

            user_mood=get_mood(captured_mood)

            # Get movies for the provided mood
            movies_for_mood = get_movies_by_mood(user_mood)
            series_for_mood = get_series_by_mood(user_mood)

            
            movie_data_array = movies_for_mood['Movie_id'].tolist()
            series_data_array = series_for_mood['id'].tolist()

            # return display(movie_data_array,series_data_array)

            # filtered_movies=get_filtered_movies(movie_data_array)
            session['movie_data_array'] = movie_data_array
            session['series_data_array'] = series_data_array


            return render_template('result.html',user_mood=user_mood,predicted_label=predicted_label)
            # return render_template('result_tvseries.html',user_mood=user_mood, predicted_label=predicted_label, movie_data_array=movie_data_array,series_data_array=series_data_array)

        except Exception as e:
            return render_template('error.html', error=str(e))

@application.route('/resultmovies')
@login_required
def resultmovies():
    movie_data_array = session.get('movie_data_array', [])
    return render_template('resultmovies.html',movie_data_array=movie_data_array)

@application.route('/resulttvseries')
@login_required
def resulttvseries():
    series_data_array = session.get('series_data_array', [])
    return render_template('resulttvseries.html',series_data_array=series_data_array)
# @application.route('/display', methods=['POST'])
# def display(movie_data_array,series_data_array):
#     return render_template('result.html', movie_data_array=movie_data_array,series_data_array=series_data_array)

@application.route('/go_back')
def go_back():
    previous_url = request.args.get('url', '/')
    return redirect(previous_url)

@application.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='404 - Page Not Found'), 404

@application.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error='500 - Internal Server Error'), 500

@application.errorhandler(Exception)
def handle_exception(e):
    return render_template('error.html', error='An unexpected error occurred'), 500

@application.route("/users")
def list_users():
    users = User.get_all()
    return render_template('users.html', users=users)

@application.route('/status')
def status():
    base_url = request.base_url
    application.logger.info(f"Base URL: {base_url}")
    return f"Base URL: {base_url}"

if __name__ == '__main__':
    application.run(debug=True)
