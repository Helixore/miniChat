from flask import Flask, render_template, request, redirect, url_for, make_response, session
import sqlite3 as s
from os import urandom, _exit
from flask_socketio import SocketIO, emit

conn = s.connect("text.db")
cur = conn.cursor()
#cur.execute("CREATE DATABASE chat")
#cur.execute("USE chat")
cur.execute("CREATE TABLE IF NOT EXISTS chats(id integer primary key autoincrement, uname varchar(60), text varchar(255))")
conn.close()

app = Flask(__name__)
app.secret_key = urandom(256)

socketio = SocketIO(app)

def get_messages():
    data = None
    conn = s.connect("text.db")
    cur = conn.cursor()
    sql = "SELECT uname, text FROM chats"
    cur.execute(sql)
    data = cur.fetchall()
    conn.close()
    return data

@socketio.on("message sent")
def message_sent(data):
    if session.get('username'):
        conn = s.connect("text.db")
        cur = conn.cursor()
        uname = session['username']
        sql = "INSERT INTO chats(uname,text) VALUES (?, ?)"
        cur.execute(sql, (uname, data['data']))
        conn.commit()
        conn.close()
        data = get_messages()
        print(data)
        socketio.emit("messages_load", data)
    else:
        socketio.emit("redirect", {"url": "/"})

@socketio.on("connection made")
def connected(data):
    print("Connection made")

@app.get("/stop")
def stop():
    conn = s.connect("text.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM chats")
    conn.commit()
    conn.close()
    _exit(0)
    return "That\'s it folks..."

@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        try:
            if 'username' in session:
                return redirect(url_for("chat"))
            else:
                return render_template("index.html")
        except:
            return render_template("index.html")
        
    elif request.method == "POST":
        if request.form['uname'] != "":
            resp = make_response(redirect(url_for("chat")))
            session['username'] = request.form['uname']
            return resp
    else:
        return make_response(redirect(url_for("register")))

@app.route("/chat", methods=["GET"])
def chat():
    if request.method == "GET":
        if session.get("username"):
            socketio.emit("messages_load", get_messages())
            return render_template("chat.html")
        else:
            return redirect(url_for("register"))


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=False)
