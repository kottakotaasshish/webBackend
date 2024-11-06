# File Management Web Application

This project is a web-based application that allows users to sign up, log in, and manage files by uploading, deleting, and renaming them. It includes a public information page accessible to all visitors, while authenticated features require user login. The application is built using Flask for the backend and MySQL as the database.

## Team Members
- **Tarun Sai Vuppala, cwid 82778861**
- **Ashish Kottakota, cwid 878640879**

## Features
1. **User Signup**: Register a new user with a username and password.
2. **User Login**: Log in to access file management features.
3. **File Upload**: Upload files to the server.
4. **File Deletion**: Remove files from the server.
5. **File Renaming**: Update the names of uploaded files.
6. **Public Information Page**: Access general information without logging in.

## Prerequisites
- **Python** (version 3.6 or higher)
- **Flask**: Install Flask and related dependencies.
- **MySQL**: A MySQL database for storing user and file data.

## Installation and Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repository-name.git
   cd your-repository-name

2. **Install Python Packages: Run the following command to install all required Python libraries.**
pip install -r requirements.txt

3. **Database Configuration:**
    Create a MySQL database named file_management.
    Run the SQL commands provided in schema.sql to create the necessary tables.
    Update the app.py file with your MySQL database credentials.

4. **Environment Variables: Configure environment variables for your MySQL database connection. You can add them to a .env file:**
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=your_password
    DB_NAME=file_management

5. **Run the Application: Start the Flask server by running:**
   python app.py
   The application will be available at http://127.0.0.1:5000.

6. **Usage**
    Signup: Access http://127.0.0.1:5000 and create a new user account.
    Login: Log in using your account credentials.
    Upload Files: Use the file upload feature to add files to your account.
    Manage Files: Delete or rename files as needed.
    View Public Information: Visit the public information section on the home page without logging in.
    
7. **API Endpoints**

    Endpoint	        Method	Description
    /signup 	         POST	Create a new user account
    /login	             POST	Log in an existing user
    /upload	             POST	Upload a file
    /uploads	         GET	Retrieve list of uploaded files
    /delete-file/<name>	 DELETE	Delete a specified file
    /update-file-name	 PATCH	Update the name of a specified file
    /public-items	     GET	Retrieve public information

8. **File Structure**

    app.py:                 The main application logic.
    templates/index.html:   The HTML file containing the user interface.
    README.md:              This documentation file.
    requirements.txt:       List of required Python packages.
    

