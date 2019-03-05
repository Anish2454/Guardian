from flask import Flask, render_template, request, session, redirect, flash, url_for
from util import db
from datetime import datetime
from threading import Thread
import time
import os, cgi, hashlib, sys
from twilio.twiml.messaging_response import MessagingResponse
from time import sleep
import sched
from twilio.rest import Client
####replace localtime()[3] with 6 to hardcode 6am

if sys.platform != 'win32':			# Windows does not support SIGPIPE
	from signal import signal, SIGPIPE, SIG_DFL
	signal(SIGPIPE, SIG_DFL)


app = Flask(__name__)
app.secret_key = os.urandom(32)

# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'ACdea0805bb097bfa14996578eef1f4215'
auth_token = '926acf3be655d1a37f03dbd2908de53e'
client = Client(account_sid, auth_token)

def check_if_danger(username):
	sleep(5)
	if(db.get_user_pref(username, "expecting")[0] == "True"):
		#User is in danger
		contacts = db.get_contacts(username)
		for contact in contacts:
			number = str(contacts[contact][0])
			print number
			msg = str(contacts[contact][1])
			message = client.messages \
			    .create(
			         body=msg,
			         from_='+15167013095',
			         to=number
			     )
			print(message.sid)
	else:
		print "Not in dager"

@app.route("/sms", methods=['GET', 'POST'])
def respond():
	body = request.values.get('Body', None)
	number = str(request.values.get('From', None))
	username = db.get_username_by_phone(number)
	print db.get_user_pref(username, "expecting")[0]
	if(db.get_user_pref(username, "expecting")[0] == "True"):
		db.edit_user_pref(username, "expecting", "False")
		resp = MessagingResponse()
		resp.message("Thanks for letting us know!")
		return str(resp)
	else:
		"""Send a dynamic reply to an incoming text message"""
	    # Get the message the user sent our Twilio number

		print username
		print db.get_contacts(username)

		time = int(body)
		sleep(time)

	    # Start our TwiML response
		db.edit_user_pref(username, "expecting", "True")
		resp = MessagingResponse()
		resp.message("Is everything alright?")
		thread = Thread(target = check_if_danger, args=(username, ))
		thread.start()
		#print(db.get_user_pref(username, "expecting"))
		return str(resp)


    # Determine the right reply for this message

@app.route("/")
def hello_world():
    '''
	If session has a record of the correct username and password input, the user is logged in
	Otherwise, the login page is displayed
	'''
    if "username" in session.keys():
		return render_template("user_home", name=session["username"].title())
    return render_template("home.html")


@app.route("/createaccount")
def display_signup():
	if "username" in session.keys():
		return render_template("schedule.html", name=session["username"].title())
	return render_template("createaccount2.html")


@app.route("/signup")
def create_account():
	if "username" in session.keys():
		return redirect(url_for("welcome"))
	user = request.args["username"]
	if request.args["pwd1"] == request.args["pwd2"]:
		if db.check_account_exist(user):
			flash("Username is already taken")
			return redirect(url_for("display_signup"))
		db.create_account(request.args)
		flash("User created")
		return redirect(url_for("display_login"))
	else:
		flash("Passwords do not match :(")
		return redirect(url_for("display_signup"))


@app.route("/auth")
def login():
	if "username" not in request.args:
		flash("Not logged in")
		return redirect(url_for("display_login"))
	auth = db.check_account(request.args["username"], request.args["pwd"])
	if auth:
		session["username"] = request.args["username"]
		flash("Logged in!")
		return redirect(url_for("user_home"))
	flash("Credentials invalid")
	return redirect(url_for("display_login"))


@app.route("/login")
def display_login():
	return render_template("login2.html")


@app.route("/logout")
def logged_out():
	if "username" not in session.keys():
		return redirect(url_for("hello_world"))
	session.clear()  # Ends session
	return redirect("/")  # Redirecting to login


@app.route("/add_contact", methods=['POST'])
def add_contact():
	name = request.form["name"]
	number = request.form["number"]
	msg = request.form["msg"]

	print request.form

	db.add_contact(session["username"], name, number, msg)
	print "Added"
	return ""

@app.route("/userhome")
def user_home():
	session["phone"] = str(db.get_user_pref(session["username"], "phone")[0])
	return render_template("user_home.html", phone=session["phone"], name=str(session["username"]).title(), contacts=db.get_contacts(session["username"]))


if __name__ == "__main__":
	app.run(debug=True)
