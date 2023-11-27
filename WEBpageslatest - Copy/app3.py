# app2.py
from flask import Flask, render_template, redirect, request, session, url_for
from werkzeug.utils import secure_filename
import cv2
import face_recognition
import os
import pyrebase
from firebase_admin import initialize_app, storage, db as firebase_db
import logging

app = Flask(__name__)

firebaseConfig = {
    "apiKey": "AIzaSyCfz9cWzB-q2sVxZQvxg2AdSmS-onQUm9I",
    "authDomain": "faces-38f82.firebaseapp.com",
    "databaseURL": "https://faces-38f82-default-rtdb.firebaseio.com",
    "projectId": "faces-38f82",
    "storageBucket": "faces-38f82.appspot.com",
    "messagingSenderId": "561665683184",
    "appId": "1:561665683184:web:62e1ea55549aef5bdcdc35",
    "measurementId": "G-PHWLRQ9GZN"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)  # Generate a secure secret key
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_storage(file, filename):
    blob = storage.bucket().blob(filename)
    blob.upload_from_file(file)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def page1():
    return render_template('index.html')

@app.route('/login2', methods=['GET', 'POST'])
def page2():
    # if request.method == 'POST':
    #     email = request.form.get('email')
    #     password = request.form.get('password')
    #     person_name = request.form.get('person_name')

    #     # Check if any of the required fields is missing
    #     if not email or not password or not person_name:
    #         return render_template('login2.html', error='All fields are required. Please try again.')

    #     users_ref = firebase_db.reference('myform')
    #     users = users_ref.get()

    #     if users:
    #         for user_key, user_data in users.items():
    #             if user_data.get('email') == email and user_data.get('password') == password:
    #                 session['user_id'] = user_key
    #                 register_faces(person_name)
    #                 return redirect(url_for('result'))

    #         # If the loop completes without a match, show an error message
    #         return render_template('login2.html', error='Invalid credentials. Please try again.')

    #     return redirect(url_for('index'))

    # return render_template('login2.html')
    # 2nd method



    # if request.method == 'POST':
    #     email = request.form.get('email')
    #     password = request.form.get('password')
    #     person_name = request.form.get('person_name')

    #     if not email or not password or not person_name:
    #         return render_template('login2.html', error='All fields are required. Please try again.')

    #     users_ref = firebase_db.reference('myForm')
    #     users = users_ref.get()

    #     if users:
    #         for user_key, user_data in users.items():
    #             if user_data.get('email') == email and user_data.get('password') == password:
    #                 session['user_id'] = user_key

    #                 # Adding logging for debugging
    #                 logging.info(f'User {person_name} logged in successfully.')

    #                 # Check if register_faces is called
    #                 logging.info('Calling register_faces function...')
    #                 register_faces(person_name)

    #                 return redirect(url_for('result'))

    #         # If the loop completes without a match, show an error message
    #         return render_template('login2.html', error='Invalid credentials. Please try again.')

    #     return redirect(url_for('index'))

    # return render_template('login2.html')

    # 3rd method


        # if request.method == 'POST':
        #     email = request.form.get('email')
        #     password = request.form.get('password')
        #     person_name = request.form.get('person_name')

        #     if not email or not password or not person_name:
        #         return render_template('login2.html', error='All fields are required. Please try again.')

        #     users_ref = firebase_db.reference('myForm')
        #     users = users_ref.get()

        #     if users:
        #         for user_key, user_data in users.items():
        #             if user_data.get('email') == email and user_data.get('password') == password:
        #                 session['user_id'] = user_key

        #                 # Adding logging for debugging
        #                 logging.info(f'User {person_name} logged in successfully.')

        #                 # Check if register_faces is called
        #                 logging.info('Calling register_faces function...')
        #                 register_faces(person_name)

        #                 return redirect(url_for('result'))

        #         # If the loop completes without a match, show an error message
        #         return render_template('login2.html', error='Invalid credentials. Please try again.')

        #     # return redirect(url_for('index'))

        # return render_template('login2.html')


        # method 4
        error = None
        if request.method == 'POST':
            
            email = request.form.get('email')
            password = request.form.get('password')
            person_name = request.form.get('person_name')

            # Perform Firebase authentication (replace with your actual authentication code)
            # Example: authenticate the user using Firebase Auth
            # auth_result = authenticate_with_firebase(email, password)

            # Assuming auth_result is a dictionary containing user information
            
            auth_result = {'uid': 'user_uid'}

            if auth_result:
                session['user_id'] = auth_result['uid']

                # Update last login time in the database
                # update_last_login(auth_result['uid'])
                register_faces(person_name)
                return redirect(url_for('result'))
            error = 'Invalid credentials. Please try again.'

            # Handle authentication failure
            return render_template('login2.html', error='Invalid credentials. Please try again.')
            
        return render_template('login2.html',error=error)


@app.route('/register', methods=['GET', 'POST'])
def page3():
    if request.method == 'POST':
        # Extract user data from the registration form
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']  # Fix the typo here
        person_name = request.form['person_name']

        # Create a new user in Firebase Authentication
        try:
            user = auth.create_user_with_email_and_password(email, password)
        except Exception as e:
            # Handle registration error
            return render_template('register.html', error=str(e))

        # Handle file upload
        file = request.files['image']
        if file and allowed_file(file.filename):
            # Save the file to Firebase Storage
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            with open(file_path, 'rb') as image_file:
                storage.child("images/" + filename).put(image_file)

            # Get the download URL of the uploaded image
            image_url = storage.child("images/" + filename).get_url(None)

        # Save the form data and image URL to the Firebase Realtime Database
        form_data = {
            "name": request.form.get('name', ''),
            "person_name": request.form.get('person_name', ''),
            "password": password,  # Use the corrected variable here
            "date": request.form.get('date', ''),
            "gender": request.form.get('gender', ''),
            "email": request.form.get('email', ''),
            "address": request.form.get('address', ''),
            "image_url": image_url if 'image_url' in locals() else ''  # Handle when image_url is not available
        }

        save_to_firebase(form_data)

        return redirect('/login2')
    elif request.method == 'GET':
        return render_template('register.html')


@app.route('/final')
def page5():
    return render_template('final.html')

@app.route('/result')
def result():
    user_id = session.get('user_id')
    if user_id:
        return render_template('result.html')
    else:
        return redirect(url_for('index'))

def register_faces(person_name):
    # Your face registration logic (similar to the provided code)
    # ...
    # Your face registration logic (similar to the provided code)
    # ...
    if not os.path.exists(person_name):
        os.makedirs(person_name)

    # Open a connection to the camera (0 is the default camera)
    video_capture = cv2.VideoCapture(0)

    # Initialize some variables
    face_locations = []
    face_encodings = []
    count = 0

    print("Press 'q' to stop capturing and register the face.")

    while True:
        # Capture each frame
        ret, frame = video_capture.read()

        # Find all face locations and face encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Draw a rectangle around the face
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Capture a frame every 100 milliseconds
        if cv2.waitKey(100) & 0xFF == ord('q'):
            # Save the captured face to the person's directory
            face_image = os.path.join(person_name, f"face_{count}.jpg")
            cv2.imwrite(face_image, frame)
            count += 1

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the window
    video_capture.release()
    cv2.destroyAllWindows()
def save_to_firebase(form_data):
    
    db.child("myForm").push(form_data)


if __name__ == '__main__':
    app.run(debug=True)
