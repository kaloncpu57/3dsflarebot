import requests
import random
import time
from bs4 import BeautifulSoup
from cfg import *
import atexit
import sys
import os
sys.path.insert(0, os.path.dirname(".."))
import predictor
import lipsum
from chatterbot import ChatterBotFactory, ChatterBotType

factory = ChatterBotFactory()
chatters = {}
magic8 = ["I think so Kappa", "Probably not 4Head", "No way MrDestructoid", "Absolutely MrDestructoid", "Why would you ask that? BibleThump", "I don't know MrDestructoid", "If you believe hard enough MrDestructoid", "What does that have to do with anything? DansGame", "No. Plain and simple. MrDestructoid", "Only twice on Tuesdays. Kappa", "That's as true as I'm standing here in front of you. MrDestructoid", "Does Dante love strawberry sundaes? (The answer is yes.)", "If pigs currently fly, which is statistically impossible. MrDestructoid"]
thrusters = ["https://uproxx.files.wordpress.com/2013/08/robot-hip-thrust.gif?w=650", "http://media.giphy.com/media/ZtjDLH1aWhcdi/giphy.gif", "http://i1017.photobucket.com/albums/af294/armargeddon/Star%20Wars/storm-trooper-pelvic-thrust.gif"]

def makeid(n):
  return ''.join((random.choice("abcdefghijklmnopqrstuvwxyz1234567890") for i in range(n)))

def newshout(msg):
  s.post(add_shout, data={'d_token': makeid(20), 'text': msg, 'submit': 'Submit'})

def popup(usr, msg):
    s.post(popups_url, data={'t': 'new', 'usr_name': usr, 'popup_txt': msg, 'submit': 'Send message'})

def respond(usr, msg, rtype):
    if rtype == "shout":
        newshout(msg)
    elif rtype == "popup":
        popup(usr, msg)

def exithandle():
    print("Powering down...")

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
        if len(j.findAll('div', {'class': 'quote'})) == 0:
            shout = Shout('', '', '')
            shout.user = i.a.get_text()
            shout.msg = j.find_all('div', {'class': 'shout_msg'})[0].get_text().strip('\r\n').strip('-')
            shout.date = j.small.get_text()
            shouts.append(shout)
    return shouts

def getPopups():
    soup = BeautifulSoup(s.get(popups_url).text)
    new_shouts = soup.findAll('div', {'class': 'WhiteAndBlack'})
    cmds = []
    for i in new_shouts:
        cmd = Shout('', '', '')
        cmd.user = i.a.text
        cmd.msg = i.find('span', {'class': 'msg_txt'}).text
        cmd.date = i.find('small').text.strip('/[()]/')
        cmds.append(cmd)
    return cmds

def getUsers():
    global USERS
    shouts = getShouts()
    with open(sys.argv[0] + "/shoutcache.txt") as f:
        shout_cache = f.read().splitlines()
    new_cache = open(sys.argv[0] + "/shoutcache.txt", "w+")
    for i in shouts:
        new_cache.write(str([i.user, i.msg, i.date]) + "\n")
    new_cache.close()
    for i in range(len(shout_cache)):
        shout_cache[i] = eval(shout_cache[i])
        names = []
        for i in shout_cache:
            if i[0] not in names and i[0] != BOT:
                names.append(i[0])
    soup = BeautifulSoup(s.get("http://3dsflare.wapka.mobi/site_2.xhtml").text, 'html.parser')
    for i in soup.find("table", {'class': 'blackAndRed'}).find_all("a"):
        try:
            if i.text not in names and i.text != BOT:
                names.append(str(i.text))
        except UnicodeEncodeError:
            pass
    USERS = names

def chat(user, msg):
    if user in chatters:
        return chatters[user].think(msg)
    else:
        chatters[user] = factory.create(ChatterBotType.CLEVERBOT).create_session()
        return chatters[user].think(msg)

def cmdParse(cmd, user, rtype):
    if cmd.strip() != "":
        cmds = cmd.strip().lower().split()
    else:
        cmds = [cmd]
    reply = "[quote=" + user + "]" + cmd + "[/quote]"
    if cmds[0] == "!quote":
        try:
            respond(user, reply + s.get("http://kaloncpu57.comyr.com/quotes/getquote").text, rtype)
        except requests.exceptions.ConnectionError:
            respond(user, reply + "Sorry.. Quotes cannot currently be accessed.", rtype)
    elif cmds[0] == "!twerk":
        images = eval(s.get("https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=twerking%20gif").text.replace
("null", "\"\""))
        respond(user, reply + "[img]%s[/img]" % (random.choice(images["responseData"]["results"])["unescapedUrl"]), rtype)
    elif cmds[0] == "!rtd":
        try:
            dice = int(cmds[1])
            sides = int(cmds[2])
            if dice > 1000 or dice < 1 or sides > 30 or sides < 3:
                respond(user, "Max dice: 1000; Min dice: 1; Max sides: 30; Min sides: 3", rtype)
            else:
                result = 0
                for i in range(dice):
                    result += random.randint(1, sides)
                respond(user, reply + "You rolled %s dice with %s sides and got %s." % (dice, sides, result), rtype)
        except (ValueError, IndexError) as err:
            respond(user, reply + "Sorry, please check how to use this command. [url]http://pastebin.com/mhT7FXX0[/url]", rtype)
    elif cmds[0] == "!ftc":
        respond(user, reply + "You flipped a coin and got %s." % ("heads" if random.randint(0, 1) == 0 else "tails"), rtype)
    elif cmd[0] == "cpu57," and "?" in cmd[7:]:
        #elif (rtype == "shout" and cmds[0] == "cpu57," and "?" in cmd[7:]) or (rtype == "popup" and "?" in cmd):
        if "who" in cmd.lower():
            getUsers()
            respond(user, "%s [user]%s[/user]" % (reply, random.choice(USERS)), rtype)
        else:
            respond(user, reply + random.choice(magic8), rtype)
    elif cmds[0] == "!hug":
        cmds = cmd.split()
        getUsers()
        levels = ["soft", "medium", "tight"]
        level = random.choice(levels)
        users = [x.lower() for x in USERS]
        try:
            usr2hug = cmds[1]
            if cmds[1].lower() in users:
                try:
                    if cmds[2].lower() in levels:
                        level = cmds[2].lower()
                except IndexError:
                    pass
                if rtype == "shout":
                    respond(user, "/hug request_from=%s destination=%s level=%s" % (user, USERS[users.index(cmds[1].lower())], level), rtype)
                elif rtype == "popup":
                    respond(user, "%s Gave a hug to %s." % (reply, USERS[users.index(cmds[1].lower())]), rtype)
                    respond(USERS[users.index(cmds[1].lower())], "/hug request_from=%s level=%s" % (user, level), rtype)
            else:
                respond(user, "%s /respond type=hug destination=%s level=%s (don't forget to spell your friend's username correctly)" % (reply, user, level), rtype)
        except IndexError:
            respond(user, "%s /respond type=hug destination=%s level=%s" % (reply, user, level), rtype)
    elif cmds[0] == "!daisybell":
        respond(user, "%s Daisy, Daisy, give me your answer, do[br]I'm half crazy all for the love of you[br]It won't be a stylish marriage[br]I can't afford a carriage[br]But you'll look sweet upon the seat[br]Of a bicycle built for two" % reply, rtype)
    elif cmds[0] == "!thrust":
        respond(user, "%s [img]%s[/img]" % (reply, random.choice(thrusters)), rtype)
    elif cmds[0] == "!lipsum" and rtype == "popup":
        try:
            p = int(cmds[1])
            if p > 30 or p < 1:
                respond(user, reply + "max/min paragraphs: 30/1", rtype)
            else:
                respond(user, lipsum.main(p), rtype)
        except (TypeError, ValueError, IndexError):
            respond(user, reply + "Sorry, please check how to use this command. [url]http://pastebin.com/mhT7FXX0[/url]", rtype)
    elif cmds[0] == "@cpu57" or rtype == "popup":
        if cmds[0] == "@cpu57":
            cmd = cmd[7:]
        respond(user, reply + chat(user, cmd), rtype)
    """
    Make sure the cleverbot command
    is last so other commands can still
    be used in popups
    """
    if user == ADMIN:
        if cmds[0] == "!power":
            respond(user, "Powering down...", rtype)
            exit()
        if "cpu57, say hi" in cmd.lower():
            """
            for i in range(len(shout_cache)):
                shout_cache[i] = eval(shout_cache[i])
            names = ""
            for i in shout_cache:
                if i[0] not in names and i[0] != "CPU 57":
                    names += i[0] + ", "
            """
            getUsers()
            respond(user, "Hello %s, I am CPU57" % ", ".join(USERS), rtype)
        if cmds[0] == "!predict":
            mons = cmd[9:].strip("\r\n").split(", ")
            winner = predictor.main(mons)
            if winner[0] == "either":
                winner[0] = random.choice(["red", "blue"])
                if winner[0] == "red":
                    winner[2] = winner[3]
            if winner == "fail":
                respond(user, reply + "Failed... please try again.", rtype)
            else:
                respond(user, reply + "%s team (%s) will win with a %s chance MrDestructoid" % (winner[0], winner[2], "{0:.2f}".format(round(winner[1], 2)) + "%"), rtype)
        if cmds[0] == "!post":
            if cmds[1] == "shout":
                respond(user, cmd[12:], "shout")
            elif cmds[1] == "popup":
                respond(user, cmd[12:], "popup")
    

url = "http://3dsflare.wapka.mobi"
login = url + "/login_site.xhtml"
login_data = {'wu_login': BOT, 'wu_heslo': PASS, 'log_submit': 'Log in'}
shouts_url = url + "/forum_110501539.xhtml"
add_shout = url + "/forum_add_110501539.xhtml"
popups_url = url + "/popup_1.xhtml"
s = requests.Session()
s.headers.update({'user-agent': 'Mozilla'})
s.get(login, params=login_data)
atexit.register(exithandle)

try:
    if sys.argv[1] == "y":
        shouts = getShouts()
        new_cache = open(sys.argv[0] + "/shoutcache.txt", "w+")
        for i in shouts:
            new_cache.write(str([i.user, i.msg, i.date]) + "\n")
        new_cache.close()
        with open(sys.argv[0] + "/shoutcache.txt") as f:
            shout_cache = f.read().splitlines()
        for i in range(len(shout_cache)):
            shout_cache[i] = eval(shout_cache[i])
            names = ""
            for i in shout_cache:
                if i[0] not in names and i[0] != "CPU 57":
                    names += i[0] + ", "
        newshout("Hello %sI am CPU57" % names)
    else:
        print("Did not say hi.")
except IndexError:
    pass
    
while True:
    shouts = getShouts()
    popups = getPopups()
    with open(sys.argv[0] + "/shoutcache.txt") as f:
        shout_cache = f.read().splitlines()
    for i in reversed(shouts):
        if i.user != BOT and str([i.user, i.msg, i.date]) not in shout_cache:
            try:
                cmdParse(i.msg, i.user, "shout")
            except (IndexError, UnicodeEncodeError):
                pass
    new_cache = open(sys.argv[0] + "/shoutcache.txt", "w+")
    for i in shouts:
        new_cache.write(str([i.user, i.msg, i.date]) + "\n")
    new_cache.close()
    for i in popups:
        try:
            cmdParse(i.msg, i.user, "popup")
        except (IndexError, UnicodeEncodeError):
            pass
    time.sleep(1 / 2)
