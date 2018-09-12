from flask import Flask, render_template, request, redirect, session, flash, jsonify
from datetime import datetime
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "ThisIsSecret"

myData = connectToMySQL('friendsdb')

emailRegEx = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


@app.route("/")
def home():
    return redirect("/users")


@app.route("/users")
def users():

    session["users"] = myData.query_db("SELECT *, CONCAT(first_name, ' ', last_name) AS name, DATE_FORMAT(created_at, '%M %D, %Y') AS date FROM friends;")

    return render_template("users.html")


@app.route("/users/view/<id>")
def view(id):

    query = "SELECT *, CONCAT(first_name, ' ', last_name) AS name, DATE_FORMAT(created_at, '%M %D, %Y') AS date FROM friends WHERE id = " + id + ";"

    session["user"] = myData.query_db(query)

    return render_template("users_view.html")


@app.route("/users/edit/<id>")
def edit(id):

    session["user"] = myData.query_db("SELECT *, CONCAT(first_name, ' ', last_name) AS name FROM friends WHERE id = %s;" %id)

    return render_template("users_edit.html")


@app.route("/users/new")
def new():

    return render_template("users_new.html")


@app.route("/users/update", methods=["POST"])
def update():

    if len(request.form["first_name"]) <= 1:
        flash("Plese enter a valid first name", "first")
    elif not request.form["first_name"].isalpha():
        flash("Names may only contain letters", "first")

    if len(request.form["last_name"]) <= 1:
        flash("Plese enter a valid last name", "last")
    elif not request.form["last_name"].isalpha():
        flash("Names may only contain letters", "last")

    if len(request.form["email"]) <= 1:
        flash("Please enter a valid Email Address", "email")
    elif not emailRegEx.match(request.form["email"]):
        flash("You must enter a valid Email Address", "email")

    if "_flashes" in session.keys():
        return redirect("/edit/" + str(session["user"][0]["id"])) #failure
    else:
        query = "UPDATE friends SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s, occupation = Null, updated_at = now() WHERE id = %(id)s;"
        data = { 
            "first_name" : request.form["first_name"],
            "last_name" : request.form["last_name"],
            "email" : request.form["email"],
            "id" : request.form["id"]
            }
        myData.query_db(query, data)
        return redirect("/users/view/" + str(request.form["id"]))


@app.route("/users/create", methods=["POST"])
def create():

    if len(request.form["first_name"]) <= 1:
        flash("Plese enter a valid first name", "first")
    elif not request.form["first_name"].isalpha():
        flash("Names may only contain letters", "first")

    if len(request.form["last_name"]) <= 1:
        flash("Plese enter a valid last name", "last")
    elif not request.form["last_name"].isalpha():
        flash("Names may only contain letters", "last")

    if len(request.form["email"]) <= 1:
        flash("Please enter a valid Email Address", "email")
    elif not emailRegEx.match(request.form["email"]):
        flash("You must enter a valid Email Address", "email")

    if "_flashes" in session.keys():
        return redirect("/users/new") #failure
    else:
        query = "INSERT INTO friends (first_name, last_name, email, occupation, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, Null, now(), now());"
        data = { 
            "first_name" : request.form["first_name"],
            "last_name" : request.form["last_name"],
            "email" : request.form["email"],
            }
        newUserId = myData.query_db(query, data)
        return redirect("/users/view/" + str(newUserId))


@app.route("/users/remove/<id>")
def remove(id):

    myData.query_db("DELETE FROM friends WHERE id = %s;" %id)

    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)