import mysql.connector as sqltor
import uuid
from flask import Flask, request, jsonify, redirect, render_template
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
mycon = sqltor.connect(
    host="your-host",
    user="your-user",
    passwd="your-mysql-password",
    database="url_shortener"
)

if mycon.is_connected():
    print("Success")
    
mycursor = mycon.cursor()

mycursor.execute("""
CREATE TABLE IF NOT EXISTS url(
    url VARCHAR(255) , 
    short_code VARCHAR(20) 
)
""")

mycon.commit()
def generate_code():
    return str(uuid.uuid4())[:7]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/link/<path:url>", methods=["POST"])
def insert(url):
    if not str(url).startswith('https://'):
        with open('short.txt', 'w') as s:
            s.write("Invalid URL")
        return 'Invalid Url', 400

    query = "SELECT short_code FROM url WHERE url=%s"
    mycursor.execute(query, (url,))
    result = mycursor.fetchall()

    if result:
        short_code = result[0][0]
        short_url = f'http://127.0.0.1:5000/{short_code}'
        with open('short.txt', 'w') as s:
            s.write(short_url)
        return jsonify({'short_url': short_url}), 200
    else:
        short_code = generate_code()
        query = "INSERT INTO url (url, short_code) VALUES (%s, %s)"
        mycursor.execute(query, (url, short_code))
        mycon.commit()
        short_url = f'http://127.0.0.1:5000/{short_code}'
        print(short_url)
        with open('short.txt', 'w') as s:
            s.write(short_url)
        return jsonify({'short_url': short_url}), 200
    
@app.get("/<string:short_code>") 
def redirect_url(short_code):
    query = "SELECT url FROM url WHERE short_code = %s"
    mycursor.execute(query, (short_code,))
    url = mycursor.fetchone()
    return redirect(url[0],code=301)
        
if __name__ == '__main__':
    app.run(debug=True)