from flask import Flask, render_template, session, request, jsonify, redirect, url_for
import pyttsx3
import os
import speech_recognition as sr
import pywhatkit
import datetime
import wikipedia
import pyjokes
import requests
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from bs4 import BeautifulSoup

basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mongo = PyMongo(app)

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Function to make the bot talk
def talk(text):
    engine.say(text)
    engine.runAndWait()

def transcript_audio():
    recognizer = sr.Recognizer()
    with sr.AudioFile(os.path.join(app.config['UPLOAD_FOLDER'], 'audio.wav')) as source:
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            return command
        except Exception as e:
            print("Error: ", e)
            return "Error"

# Function to take voice command
def take_command():
    listener = sr.Recognizer()
    command = ""
    try:
        with sr.Microphone() as source:
            print('Listening...')
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'charbot' in command:
                command = command.replace('charbot', '')
                print(command)
    except Exception as e:
        print("Error: ", e)
    return command

# Function to run the chatbot
def run_charbot(command):
    if 'play' in command:
        song = command.replace('play', '')
        url = pywhatkit.playonyt(song, open_video=False)
        return f"play_youtube('{url}')"
    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        return f"speak('The current time is {time}')"
    elif 'who is' in command:
        person = command.replace('who is', '')
        try:
            info = wikipedia.summary(person, 2, auto_suggest=False)
            return f"speak('{info}')"
        except wikipedia.exceptions.DisambiguationError as e:
            return "speak('Please be more specific')"
        except wikipedia.exceptions.PageError as e:
            return "speak('No information found')"
    elif 'what is' in command:
        person = command.replace('what is', '')
        try:
            info = wikipedia.summary(person, 2, auto_suggest=False)
            return f"speak('{info}')"
        except wikipedia.exceptions.DisambiguationError as e:
            return "speak('Please be more specific')"
        except wikipedia.exceptions.PageError as e:
            return "speak('No information found')"
    elif 'joke' in command:
        joke = pyjokes.get_joke()
        return f"speak('{joke}')"
    elif 'open' in command:
        website = command.replace('open', '')
        website = website.strip()
        # if the url is not a valid url, then search for the website on google
        if not website.startswith('http'):
            website = get_first_non_ad_url(f"https://www.google.com/search?q={website}")
        return f"open_website('{website}')"
    elif 'ben10' in command or 'ben 10' in command:
        return "speak('I am ben10')"
    elif 'stop' in command:
        return "goodbye()"
    else:
        return "speak('Please say the command again.')"

def get_first_non_ad_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if not (href.startswith('http') or href.startswith('/')):
                continue
            return href
        return url
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return url

@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        if not username or not password:
            return jsonify({'error': 'Username and password are required!'}), 400

        if mongo.db.users.find_one({'username': username}):
            error_message = 'Username already exists!'
            return render_template('signup.html', error_message=error_message)

        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({'username': username, 'password': hashed_password, 'name': name})

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required!'}), 400

        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('index'))

        error_message = 'Invalid username or password!'

    return render_template('login.html', error_message=error_message)

@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/live')
def live():
    return render_template('live.html')

@app.route('/command', methods=['POST'])
def command():
    command = request.json['command']
    response = run_charbot(command.lower())
    return response

@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file found'}), 400
    audio_file = request.files['audio']
    audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'audio.wav'))
    command = transcript_audio()
    if command == "Error":
        return jsonify({'error': 'Error in transcribing audio'}), 400
    response = run_charbot(command)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
