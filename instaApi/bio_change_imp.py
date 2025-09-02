from instagrapi import Client

# Had to go into types.py and change str to int for Account object : pk

cl = Client()
cl.login("justin.sapun", "redroom87")
#print(cl.account_info().model_dump())
string = "testing"
dic = {"biography":string}
cl.account_edit(**dic)
