import sqlite3
from os.path import isfile
import hashlib

path = "data/data.db"

def get_db(): #returns connection to database
    return sqlite3.connect(path)

def get_cursor(db): #returns cursor to database
    return db.cursor()

def close(db): #commits to and closes database
    db.commit()
    db.close()

#============================================================#
#============================Users=========================#
#============================================================#


'''
    takes in dictionary of:
        username
        password
        phone
'''
def create_account(userinfo):
    print "Creating Account...\n"
    db = get_db()
    c = get_cursor(db)

    #Add User Properties
    command1 = "INSERT INTO accounts VALUES(?, ?, ?, ?)"
    username = userinfo["username"]
    password = userinfo["pwd1"]
    password = hashlib.sha224(password)
    password = password.hexdigest()
    phone = userinfo["phone"]
    last_accessed = 0
    #print "Error. Account not created\n"
    #return ""
    c.execute(command1, (username, password, phone, "False"))

    #Create Emergency Contacts
    command2 = "CREATE TABLE " + username + "(name TEXT, number TEXT, message TEXT);"
    c.execute(command2)

    print "Created emergency contact table table\n"
    close(db)


def check_account_exist(username):
    db = get_db()
    c = get_cursor(db)
    command = "SELECT username FROM accounts WHERE username = ?"
    usernames = c.execute(command, (username,))
    for list_username in usernames:
        return list_username != None
    close(db)
    return False

'''
Autheticates Account
'''
def check_account(username, password):
    db = get_db()
    c = get_cursor(db)
    password = hashlib.sha224(password)
    password = password.hexdigest()
    if(check_account_exist(username)):
        command = "SELECT password FROM accounts WHERE username = ? "
        passdb = c.execute(command, (username, )).fetchone()
        close(db)
        return passdb[0] == password
    close(db)
    return False

'''
Returns a dictionary of all the users preferences except last_accessed
Takes in a username
'''
def get_all_user_preferences(username):
    db = get_db()
    c = get_cursor(db)
    if check_account_exist(username):
        pref_names = ["music", "address"]
        command = "SELECT {} FROM accounts WHERE username = ?".format(", ".join(pref_names))
        #print command
        prefs_tup = c.execute(command, (username, )).fetchone()
        db.commit()
        close(db)
        #print prefs_tup
        prefs_dict = {}
        for pref in range(len(pref_names)):
            #print pref
            prefs_dict[pref_names[pref]] = prefs_tup[pref]
        return prefs_dict
    else:
        print "Username Not Found - Unable to get preferences"
    close(db)

'''
Returns the value of a user's preference
Takes in a username and one preference
preference can be one of: "emergen"
'''
def get_user_pref(username, preference):
    db = get_db()
    c = get_cursor(db)
    pref_names = ["expecting", "phone"]
    if check_account_exist(username):
        if preference in pref_names:
            command = "SELECT " + preference + " FROM accounts WHERE username = ?"
            pref = c.execute(command, (username, )).fetchone()
            db.commit()
            close(db)
            return pref
        else:
            print "Preference DNE"
    else:
        print "Username Not Found - Unable to get preference"
    close(db)
'''
Edits one of the user's attributes
Takes in a username, the preference to change, and the new value
preference can be one of: "age", "height", "weight", "pfplink", "music", "excercise", "address", "email"
Returns the original value
'''

def edit_user_pref(username, preference, new_val):
    db = get_db()
    c = get_cursor(db)
    pref_names = ["expecting"]
    if check_account_exist(username):
        if preference in pref_names:
            old_val = get_user_pref(username, preference)
            command = "UPDATE accounts SET " + preference + " = ? WHERE username = ?"
            c.execute(command, (new_val, username))
            db.commit()
            close(db)
            return old_val
        else:
            print "Preference DNE"
    else:
        print "Username not found - Cannot Edit Preference"
    close(db)

def edit_all_user_pref(username, pref_dict):
    db = get_db()
    c = get_cursor(db)
    #print (pref_dict)
    pref_names = ["music", "excercise", "address"]
    if check_account_exist(username):
        for pref in pref_dict:
            if pref in pref_names:
                command = "UPDATE accounts SET " + pref + " = ? WHERE username = ?"
                c.execute(command, (pref_dict[pref], username))
            else:
                print ("Pref: " + pref + " Not a preference")
    else:
        print "Username not found - Cannot Edit All Preferences"
    db.commit()
    close(db)

#============================================================#
#============================Schedules=========================#
#============================================================#

'''
Returns the entire contact list as dictionary:
{"name": [phone#, message]}
'''
def get_contacts(username):
    print username
    db = get_db()
    c = get_cursor(db)
    if(check_account_exist(username)):
        command = "SELECT * FROM " + username + ";"
        sched = c.execute(command).fetchall()
        close(db)
        d = {}
        for line in sched:
            print line
            d[line[0]] = [line[1], line[2]]
        return d
    else:
        print "Username not found - Could not get contact list"
    close(db)

'''
Takes in Dict in format:
  {time: {"activity": "ex_activity", "music": "ex_song"}, time: {"activity": "ex_activity2", "music": "ex_song2"}, ...}
  "time" is a single int representing the start time (each hour has a section in the table)
  ex: if time = 4 then the activities corresponding to that time go on from 4am-5am
'''
def reset_contacts(username, contacts):
    db = get_db()
    c = get_cursor(db)
    if(check_account_exist(username)):
        delcom = "DROP TABLE " + username
        c.execute(delcom)
        db.commit()
        crecommand = "CREATE TABLE " + username + "(name TEXT, number TEXT, message TEXT);"
        c.execute(crecommand)
        db.commit()
        for contact in contacts:
            name = contact
            print name
            number = contacts[name][0]
            msg = contacts[name][1]
            '''
            print("Inserting: ")
            print("Time: " + str(time))
            print("Activity: " + activity)
            print("Song: " + song)
            '''
            command = "INSERT INTO " + username + "(name, number, message) VALUES(?, ?, ?);"
            c.execute(command, (name, number, msg))
    else:
        print "Username Not Found - Cannot Reset Schedule"
    close(db)

def add_contact(username, name, number, msg):
    contacts = get_contacts(username)
    print "Before: "
    print contacts
    contacts[name] = [number, msg]
    print "After: "
    print contacts
    reset_contacts(username, contacts)

def remove_contact(username, name):
    contacts = get_contacts(username)
    if(contact in contacts):
        contacts.remove(contact)
    reset_contacts(username, contacts)

def get_username_by_phone(number):
    db = get_db()
    c = get_cursor(db)
    command = "SELECT username FROM accounts WHERE phone = ? "
    username = c.execute(command, (number,)).fetchone()[0]
    close(db)
    return username


'''
TESTS:
userinfo = {"username": "anish2000", "password":"FOURWORDSALLLOWERCASE", "age": 56, "height": 250, "weight": 100, "pfplink": "http://google.com", "music": "rock", "excercise": "cardio", "address": "345 Chambers St", "email": "email@gmail.com"}
create_account(userinfo)
sched = {12: {"activity": "Canned Sardines", "music":"Hey Jude"}, 13:{"activity": "Swimming", "music": "Moon"}}
reset_sched("anish2000", sched)
print(get_schedule("anish2000"))
get_activ_music("anish2000", "2011-05-03 12:45:35.177000")
get_activ_music("anish2000", "2014-23-03 13:45:35.177000")
get_activ_music("anish2000", "2033-05-05 14:45:35.177000")
print(get_all user_preferences("anish2000"))
print(edit_user_pref("anish2000", "email", "bobz2000@stuy.edu"))
print(get_user_pref("anish2000", "email"))
'''
