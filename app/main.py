from flask import Flask, render_template, redirect
APP = Flask(__name__)

#home page
@APP.route("/", methods=['GET', 'POST'])
def home_page():
    return render_template("home_page.html")

#new job page
@APP.route("/new_job", methods=["GET","POST"])
def new_job():
   return render_template("new_job.html")

#new job page
@APP.route("/jobs", methods=["GET","POST"])
def current_jobs():
   return render_template("current_jobs.html")