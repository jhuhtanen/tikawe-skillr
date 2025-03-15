import os

from flask import Flask, render_template

from flaskr import config

app = Flask(__name__)
#app.secret_key = config.secret_key

#@app.route("/")
#def index():
#    return "Skillr WIP"


@app.route("/")
def home():
    return "Flask is running!"


'''@app.route("/register")
def register():
    print("Looking for template in:", os.path.join(app.template_folder, "register.html"))
    return render_template("register.html")'''


@app.route("/index")
def index():
    return render_template("index.html")



@app.route("/foobar")
def foobar():
    print("Looking for template in:", os.path.join(app.template_folder, "foobar.html"))
    return render_template("foobar.html")

'''if __name__ == "__main__":
    print("Registered routes:", app.url_map)  # Prints all routes
    app.run(debug=True)'''