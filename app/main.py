from flask import Flask, render_template
APP = Flask(__name__)

#home page (1)
@APP.route("/", methods=['GET', 'POST'])
def home_page():
    return render_template("home_page3.html")

#new job page (5)
@APP.route("/new_job", methods=["GET","POST"])
def new_job():

   # if request.form['yamlFilename'] == "":
    #    return "Must specify .yaml filename."

   # yaml_Filename=request.form['yamlFilemname']
   # print(yaml_Filename)

   # return render_template("new_job.html",
   # yaml_Filename = yamlFilename)
   return render_template("new_job.html")
