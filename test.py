# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'ACdea0805bb097bfa14996578eef1f4215'
auth_token = '926acf3be655d1a37f03dbd2908de53e'
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         body='This is the ship that made the Kessel Run in fourteen parsecs?',
         from_='+15167013095',
         to='+17186665451'
     )

print(message.sid)
