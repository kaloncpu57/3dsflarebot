#!python3
import requests
import random
import time
from bs4 import BeautifulSoup

BOT = input("Username of BOT: ")
PASS = input("Password for BOT: ")

def makeid(n):
    return ''.join((random.choice("abcdefghijklmnopqrstuvwxyz1234567890") for i in range(n)))

def newshout(msg):
    s.post(add_shout, data={'d_token': makeid(20), 'text': msg, 'submit': 'Submit'})

class Shout:
    def __init__(self, user, msg, date):
        self.user = user
        self.msg = msg
        self.date = date

def getShouts():
    new_shouts = s.get(shouts_url).text
    #set shouts page as parsable object
    soup = BeautifulSoup(new_shouts)
    shouts = []
    shout_heads = soup.find_all("h2", {'class': 'A'})
    shout_feet = soup.find_all("h2", {'class': 'B'})
    for i, j in zip(shout_heads, shout_feet):
        shout = Shout('', '', '')
        shout.user = i.a.get_text()
        shout.msg = j.find_all('div', {'class': 'shout_msg'})[0].get_text().strip('\r\n').strip('-')
        shout.date = j.small.get_text()
        shouts.append(shout)
    return shouts

def cmdParse(cmd, user):
    cmds = cmd.strip().lower().split()
    reply = "[quote=" + user + "]" + cmd + "[/quote]"
    if cmd.lower().strip() == "!quote":
        newshout(reply + s.get("http://kaloncpu57.comyr.com/quotes/getquote").text)
    elif cmds[0] == "!rtd":
        try:
            dice = int(cmds[1])
            sides = int(cmds[2])
            if dice > 1000 or dice < 1 or sides > 30 or sides < 3:
                newshout("Max dice: 1000; Min dice: 1; Max sides: 30; Min sides: 3")
            else:
                result = 0
                for i in range(dice):
                    result += random.randint(1, sides)
                newshout(reply + "You rolled %s dice with %s sides and got %s." % (dice, sides, result))
        except ValueError:
            newshout("Sorry, please check how to use this command.")
    elif cmds[0] == "!ftc":
        newshout(reply + "You flipped a coin and got %s." % ("heads" if random.randint(0, 1) == 0 else "tails"))

url = "http://3dsflare.wapka.mobi"
login = url + "/login_site.xhtml"
login_data = {'wu_login': BOT, 'wu_heslo': PASS, 'log_submit': 'Log in'}
shouts_url = url + "/forum_110501539.xhtml"
add_shout = url + "/forum_add_110501539.xhtml"
s = requests.Session()
s.headers.update({'user-agent': 'Mozilla'})
s.get(login, params=login_data)

while True:
    shouts = getShouts()
    with open("shoutcache.txt") as f:
        shout_cache = f.readlines()
    for i in reversed(shouts):
        if i.user != BOT and str([i.user, i.msg, i.date]) + "\n" not in shout_cache:
            cmdParse(i.msg, i.user)
    new_cache = open("shoutcache.txt", "w+")
    for i in shouts:
        new_cache.write(str([i.user, i.msg, i.date]) + "\n")
    new_cache.close()
    time.sleep(1 / 2)
