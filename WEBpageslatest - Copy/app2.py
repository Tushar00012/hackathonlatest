# # app.py
# from flask import Flask, render_template, redirect, request, session, url_for
# from werkzeug.utils import secure_filename
# import cv2
# import face_recognition
# import os
# from firebase_admin import initialize_app
# from firebase_admin import credentials,storage
# from firebase_admin import db as firebase_db

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'
# app.secret_key = 'your_secret_key'
# cred = credentials.Certificate(r"C:\Users\Lenovo\Downloads\WEBpageslatest - Copy\faces-38f82-firebase-adminsdk-xi7we-811250424f.json")

# firebase = initialize_app(cred, {"storageBucket": "gs://faces-38f82.appspot.com"})
# # firebase_db = initialize_app(cred, {'databaseURL': 'https://faces-38f82-default-rtdb.firebaseio.com/'})
# firebase_db = initialize_app(cred, {'databaseURL': 'https://faces-38f82-default-rtdb.firebaseio.com/'})

# def upload_file_to_storage(file, filename):
#     blob = storage.bucket().blob(filename)
#     blob.upload_from_file(file)
# app.py
# app.py
from flask import Flask, render_template, redirect, request, session, url_for
from werkzeug.utils import secure_filename
import cv2
import face_recognition
import os
import pyrebase
from flask import session

# Other imports...
# Other imports...
import firebase_admin
from firebase_admin import initialize_app, credentials, storage, db as firebase_db

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

# cred = credentials.Certificate(r"C:\Users\Lenovo\Downloads\WEBpageslatest - Copy\faces-38f82-firebase-adminsdk-xi7we-811250424f.json")

# # Check if the app is not already initialized before initializing




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
    registration_success = request.args.get('registration_success')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        person_name = request.form['person_name']
        
        # Assuming you have a 'users' node in your Realtime Database
        # users_ref = firebase_db.reference('users')
        users_ref = db.child('users')

        users = users_ref.get()

        if users:
            for user_key, user_data in users.items():
                if user_data['email'] == email and user_data['password'] == password:
                    session['user_id'] = user_key
                    register_faces(person_name)
                    return redirect(url_for('result'))
                else:
            # User details not matched, handle accordingly (redirect or show an error message)
                    return render_template('login2.html', error='Invalid credentials. Please try again.')

        
        return redirect(url_for('index'))

    return render_template('login2.html', registration_success=registration_success)

@app.route('/register', methods=['GET', 'POST'])
def page3():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        date = request.form['date']
        address = request.form['address']
        password = request.form['password']
        check1 = request.form.get('check1')
        gender = request.form['gender']
        person_name = request.form['person_name']

        # Handle file upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                # Save the file to the 'uploads' folder
                filename = secure_filename(image_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(file_path)

                # Upload the image to Firebase Storage
                upload_file_to_storage(file_path, filename)

                # Remove the file from the local 'uploads' folder
                os.remove(file_path)

                # Get the download URL of the uploaded image
                image_url = storage.bucket().blob(filename).public_url

                # Save user data to Realtime Database
                users_ref = db.child('users')
                new_user_ref = users_ref.push()
                new_user_ref.set({
                    'name': name,
                    'email': email,
                    'gender': gender,
                    'date': date,
                    'address': address,
                    'password': password,
                    'check1': check1,
                    'person_name': person_name,
                    'image': image_url  # Updated key name
                })


                return redirect(url_for('page2', registration_success=True))

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
    
def register_faces(person_name, output_dir='faces'):
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










if __name__ == '__main__':
    app.run(debug=True)
