from flask import Flask, render_template, redirect, request, jsonify
import cv2
import face_recognition
import os
import pyrebase
from werkzeug.utils import secure_filename
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

# Set the path where you want to store the uploaded images
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def page1():
    return render_template('index.html')

@app.route('/login2', methods=['GET', 'POST'])
def page2():
    if request.method == 'POST':
        person_name = request.form['person_name']
        register_faces(person_name)
        save_to_firebase(person_name)
        return redirect('/result')
    return render_template('login2.html')
    #  if request.method == 'POST':
    #     # Get the user data from the AJAX request
    #     data = request.get_json()

    #     customer_id = data.get('person_name')
    #     password = data.get('password')

    #     try:
    #         # Sign in with Firebase Authentication
    #         user = auth.sign_in_with_email_and_password(customer_id, password)

    #         # Add any additional logic you need for successful login
    #         # For example, you can retrieve user data from Firebase Realtime Database
    #         # user_data = db.child("myForm").child(user['localId']).get().val()

    #         # Run the register_faces function after successful login
    #         register_faces(customer_id)

    #         # Return a JSON response indicating success
    #         return jsonify({"status": "success", "message": "Login successful"})

    #     except Exception as e:
    #         # Handle login failure and return an error response
    #         print(f"Login failed: {str(e)}")
    #         return jsonify({"status": "error", "message": "Invalid login details"})
    # if request.method == 'POST':
    #     # Get the user data from the AJAX request
    #     data = request.get_json()
    #     person_name = request.form['person_name']
    #     email = data.get('email')

    #     password = data.get('password')

    #     try:
    #         # Sign in with Firebase Authentication
    #         user = auth.sign_in_with_email_and_password(email, password)

    #         # Add any additional logic you need for successful login
    #         # For example, you can retrieve user data from Firebase Realtime Database
    #         # user_data = db.child("myForm").child(user['localId']).get().val()

    #         # Run the register_faces function after successful login
    #         register_faces(person_name)

    #         # Return a JSON response indicating success
    #         return jsonify({"status": "success", "message": "Login successful"})

    #     except Exception as e:
    #         # Handle login failure and return an error response
    #         print(f"Login failed: {str(e)}")
    #         return jsonify({"status": "error", "message": "Invalid login details"})

    # # If the request method is not POST, return a response or render a template
    # return render_template('login2.html')  # Adjust this line based on your needs    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
    #     person_name = request.form['person_name']
    #     # register_faces(person_name)
    #     save_to_firebase(person_name)
        
    #     return redirect('/login2')
    # elif request.method == 'GET':
    #     return render_template('register.html')
    #not needed above 
    #needed below
    
    #     person_name = request.form['person_name']
    #     save_to_firebase(request.form)
    #     return redirect('/login2')
    # elif request.method == 'GET':
    #     return render_template('register.html')
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
            "pass": request.form.get('pass', ''),
            "date": request.form.get('date', ''),
            "gender": request.form.get('gender', ''),
            "email": request.form.get('email', ''),
            "address": request.form.get('address', ''),
            "image_url": image_url
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
    return render_template('result.html')

def register_faces(person_name):
    if not os.path.exists(person_name):
        os.makedirs(person_name)

    video_capture = cv2.VideoCapture(0)
    face_locations = []
    face_encodings = []
    count = 0

    print("Press 'q' to stop capturing and register the face.")

    while True:
        ret, frame = video_capture.read()
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.imshow('Video', frame)

        if cv2.waitKey(100) & 0xFF == ord('q'):
            face_image = os.path.join(person_name, f"face_{count}.jpg")
            cv2.imwrite(face_image, frame)
            count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

def save_to_firebase(form_data):
    
    db.child("myForm").push(form_data)

if __name__ == '__main__':
    app.run(debug=True)
