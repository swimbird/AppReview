#!/usr/bin/python
# -*- encoding:utf8 -*-
from flask import Flask, redirect, render_template, request, url_for
application = Flask(__name__)

from pymongo import Connection
conn = Connection("localhost")
ul = conn["myapp"]["userlist"]

@application.route("/add_user", methods=['POST'])
def add_user():
    name = request.form['name']
    ul.insert({"name":name})
    return redirect(url_for("index"))

@application.route("/")
def index():
    users = [i["name"] for i in ul.find()]
    return render_template("index.html", items =users)

if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True)
