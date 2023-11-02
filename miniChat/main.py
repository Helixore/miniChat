from flask import Flask, render_template, request, redirect, url_for, make_response, session
import sqlite3 as s
from os import urandom
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
        return 500

@app.route("/chat", methods=["GET", "POST"])
def chat():
    conn = s.connect("text.db")
    cur = conn.cursor()
    if request.method == "GET":
        sql = "SELECT uname, text FROM chats"
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return render_template("chat.html", rows=rows)
    elif request.method == "POST":
        if request.form["text"] != "":
            try:
                uname = session['username']
                sql = "INSERT INTO chats(uname,text) VALUES (?, ?)"
                cur.execute(sql, (uname, request.form["text"]))
                conn.commit()
                cur.execute("SELECT uname, text FROM chats")
                query_result = cur.fetchall()
                conn.close()
                socketio.emit("new message", query_result, broadcast=True)
                return "", 204
            except:
                return redirect(url_for("register"))
        else:
            return redirect(url_for("chat"))


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
