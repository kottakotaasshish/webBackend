from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import mysql.connector
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)
CORS(app, origins="http://127.0.0.1:5500")






# Configuration
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_api_db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Initialize JWT
jwt = JWTManager(app)

# Connect to MySQL
def get_db_connection():
    try:
        return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    except mysql.connector.Error as err:
        raise


# Error Handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request"}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

# Public Route: Accessible without authentication
@app.route('/public-items', methods=['GET'])
def public_items():
    public_data = [
        {"id": 1, "title": "Welcome Guide", "description": "Learn how to use the app effectively"},
        {"id": 2, "title": "Allowed File Types", "description": "You can upload PNG, JPG, JPEG, and PDF files."},
        {"id": 3, "title": "File Upload Tips", "description": "Ensure files are under 16MB in size to upload successfully."},
    ]
    return jsonify({"public_items": public_data}), 200

# Delete Specific File - Protected route
@app.route('/delete-file/<filename>', methods=['DELETE'])
@jwt_required()
def delete_specific_file(filename):
    try:
        # Get the current user identity from the JWT token
        current_user = get_jwt_identity()
        
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch the user ID from the users2 table based on the current user
        cursor.execute("SELECT id FROM users2 WHERE username = %s", (current_user,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        
        # Check if the file exists for the current user in the user_files table
        cursor.execute("""
            SELECT filename, upload_path FROM user_files 
            WHERE filename = %s AND user_id = %s
        """, (filename, user_id))
        file_record = cursor.fetchone()
        
        if not file_record:
            return jsonify({"error": "File not found"}), 404

        # Get the file path from the record
        file_path = file_record['upload_path']
        
        # Delete the file from the filesystem
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            return jsonify({"error": "File not found on server"}), 404

        # Delete the file record from the user_files table
        cursor.execute("""
            DELETE FROM user_files WHERE filename = %s AND user_id = %s
        """, (filename, user_id))
        
        # Commit the changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": f"File '{filename}' deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#update a specific file name - Protected route
@app.route('/update-file/<filename>', methods=['PUT'])
@jwt_required()
def update_file_name(filename):
    # ---changes---
    new_filename = request.json.get('new_filename')
    if not new_filename:
        return jsonify({"error": "New filename is required"}), 400

    try:
        # Get the current user identity from the JWT token
        current_user = get_jwt_identity()

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch the user ID from the users2 table based on the current user
        cursor.execute("SELECT id FROM users2 WHERE username = %s", (current_user,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = user['id']

        # Check if the file exists for the current user in the user_files table
        cursor.execute("""
            SELECT filename, upload_path FROM user_files 
            WHERE filename = %s AND user_id = %s
        """, (filename, user_id))
        file_record = cursor.fetchone()

        if not file_record:
            return jsonify({"error": "File not found"}), 404

        # Update the filename in the database
        cursor.execute("""
            UPDATE user_files SET filename = %s 
            WHERE filename = %s AND user_id = %s
        """, (new_filename, filename, user_id))
        
        # Commit the changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": f"File '{filename}' renamed to '{new_filename}' successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    # ---changes---



# Authentication
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users2 WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user is None:
        return False  # No user found
    
    print("user: ", user['password'], " ", password)
    
    stored_password = user['password']
    if check_password_hash(stored_password, password):
        return True
    elif stored_password == password:  # Plain-text password for testing purposes
        return True
    
    return False



# User Signup
@app.route('/signup', methods=['POST'])
def signup():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    print("before getting user")
    cursor.execute("SELECT * FROM users2 WHERE username = %s", [username])

    existing_user = cursor.fetchone()
    
    if existing_user:
        return jsonify({"error": "Username already taken"}), 409
    
    hashed_password = generate_password_hash(password)  
    print("hashed passwro: ",len(hashed_password))


    cursor.execute("INSERT INTO users2 (username, password) VALUES (%s, %s)", (username, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User registered successfully"}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if authenticate_user(username, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401




# File Handling
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload File - Protected route
@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users2 WHERE username = %s", (current_user,))
    user = cursor.fetchone()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user_id = user['id']
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)
        
        # Update the users2 table with file details
        # cursor.execute(
        #     "UPDATE users2 SET filename = %s, upload_path = %s, upload_date = CURRENT_TIMESTAMP WHERE id = %s",
        #     (filename, file_path, user_id)
        # )

        cursor.execute(
            "INSERT INTO user_files (user_id, filename, upload_path) VALUES (%s, %s, %s)",
            (user_id, filename, file_path)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400


# Get User-Specific Uploads - Protected route
@app.route('/uploads', methods=['GET'])
@jwt_required()
def get_user_uploads():
    current_user = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # cursor.execute("SELECT filename, upload_path, upload_date FROM users2 WHERE username = %s", (current_user,))
    # user_upload = cursor.fetchone()
    
   
    cursor.execute("""
        SELECT filename, upload_path, upload_date 
        FROM user_files 
        WHERE user_id = (SELECT id FROM users2 WHERE username = %s) """, (current_user,))
    user_uploads = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"uploads": user_uploads}), 200
    # if user_upload and user_upload['filename']:
    #     return jsonify({"uploads": [user_upload]}), 200
    # else:
    #     return jsonify({"uploads": []}), 200


if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
