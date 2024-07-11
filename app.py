from flask import Flask, request, render_template, redirect, url_for # type: ignore
import pymysql # type: ignore
import string
import random
from flask_mail import Mail, Message # type: ignore

app = Flask(__name__)
mail = Mail(app)

loginUser = False
# Database connection
connection = pymysql.connect(host="localhost", user="root", passwd="", database="MPL", cursorclass=pymysql.cursors.DictCursor)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'Enter your mail'
app.config['MAIL_PASSWORD'] = 'generate a pass key for you mail'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def execute_query(query, params=None, fetchone=False):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if fetchone:
            return cursor.fetchone()
        else:
            return cursor.fetchall()

def send_email(recipient, subject, body):
    try:
        msg = Message(subject, sender='Enter the same mail', recipients=[recipient])
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email to {recipient}: {str(e)}")
        return False

@app.route("/")
def index():
    if (loginUser == False):
        name = None
        return render_template('home.html')
    else:
        return render_template('home1.html')


@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method == 'POST':
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        execute_query("INSERT INTO logindata(fname, lname, email, username, password) VALUES (%s, %s, %s, %s, %s)", (fname, lname, email, username, password))
        connection.commit()
        return redirect(url_for('index'))
    return render_template("signup.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        if execute_query("SELECT username,password FROM logindata WHERE username = %s and password = %s", (username, password)):
            print("Login successful")
            global loginUser;
            loginUser = True
            global name 
            name = execute_query("SELECT fname FROM logindata WHERE username = username and password = password")
        else:
            print("Login failed")

        return redirect(url_for('index'))
    return render_template("login.html")

@app.route('/forgetPass0', methods=['POST', 'GET'])
def forgetPass0():
    if request.method == 'POST':
        email = request.form["email"]
        user = execute_query("SELECT email FROM logindata WHERE email = %s", (email,), fetchone=True)

        if user:
            print("Email exists in the database")

            otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            if execute_query("UPDATE logindata SET verify = %s WHERE email = %s", (otp, email)):
                execute_query("UPDATE logindata SET verify = %s WHERE email = %s", (otp, email))
                print("OTP send successfully")
            else:
                execute_query("INSERT INTO logindata (email, verify) VALUES (%s, %s) ON DUPLICATE KEY UPDATE verify = VALUES(verify)", (email, otp))
            connection.commit()


            if send_email(email, 'Password Reset OTP', f"Your OTP for resetting your password is {otp}. OTP is valid for the next 10 minutes."):
                print("OTP send")
                return redirect(url_for('forgetPass1'))
            else:
                print("Error while sending OTP")
                return redirect(url_for('index'))
    
    return render_template('forgetPass0.html')

@app.route('/forgetPass1' , methods=['POST', 'GET'])
def forgetPass1():        
    if request.method == 'POST':

        email = request.form["email"]
        otp_entered = request.form["otp"]

        otp_verified = execute_query("SELECT email,verify FROM logindata WHERE email = %s and verify = %s", (email, otp_entered))

        if otp_verified:
            print("OTP entered successfully")
            password = request.form["password"]
            password1 = request.form["password1"]
            if password1 == password:
                execute_query("UPDATE logindata SET password = %s WHERE email = %s", (password, email))
                connection.commit()
                print("Password reset successfully")
            else:
                print("Please enter same password")
        else:
            print("OTP incorrect")

        password = request.form["password"]
        password1 = request.form["password1"]
        
        return redirect(url_for('index'))
    return render_template('forgetPass1.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/screener')
def screener():
    return render_template('screener.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(debug=True)
