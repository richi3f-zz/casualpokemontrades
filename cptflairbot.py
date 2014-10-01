#!/usr/bin/env python
#
# Adapted from https://gist.github.com/EricJ2190/1240200
#
import cookielib
import jinja2
import json
import os
import re
import urllib
import urllib2
import webapp2
import time
from google.appengine.api import oauth
from xml.etree import ElementTree as etree

REDDIT = "http://www.reddit.com"
SUBREDDIT = "casualpokemontrades"
CREDENTIALS = {'user': "", 'passwd': ""}
USER_AGENT = "Casual Pokemon Trades Flair Bot 14.10.1.2 by /u/richi3f"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def reddit_api(action, params=None):
    if params:
        req = urllib2.Request(REDDIT + action, urllib.urlencode(params))
    else:
        req = urllib2.Request(REDDIT + action)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def update_flair(css_class, name, text):
    cookies = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
    opener.addheaders = [('User-agent', USER_AGENT)]
    urllib2.install_opener(opener)
    # Login to Reddit API
    reddit_api("/api/login", CREDENTIALS)
    successful = False
    for cookie in cookies:
        if cookie.name == 'reddit_session':
            successful = True
    if not successful:
        return 4 # login failure
    # Obtain modhash
    modhash = reddit_api("/api/me.json")['data']['modhash']
    # Update flairs
    listing = reddit_api("/r/" + SUBREDDIT + "/api/flairlist.json?name=" + name)
    for user in listing['users']:
        if user['user'] == name and user['flair_text'] == '':
            reddit_api("/api/flair", {'r': SUBREDDIT, 'css_class': css_class, 'name': name, 'text': text, 'uh': modhash})
            return 0 # success
    return 5 # tried to override someone's flair (temp fix)

class MainPage(webapp2.RequestHandler):
    VALID_CLASSES = []
    
    def get(self):
        #
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write(urllib2.urlopen("http://cptflairbot.appspot.com/set.xml").read())
    
    def post(self, ):
        self.parse_xml()
        friend_code = self.request.get("fc")
        in_game_name = self.request.get("ign")
        css_class = self.request.get("pkmn")
        username = self.request.get("name")
        if friend_code == '' or in_game_name == '' or css_class == '' or username == '':
            code = 1 # empty field
        else:
            regex = re.compile("^\d{4}-\d{4}-\d{4}$")
            if regex.match(friend_code):
                if css_class in MainPage.VALID_CLASSES:
                    code = 0 # success
                else:
                    code = 3 # invalid CSS class
            else:
                code = 2 # invalid FC
        if code == 0:
            code = update_flair(css_class, username, friend_code + ' | ' + in_game_name)
        
        template_values = {
            'code': code,
            'username': username
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
    
    def parse_xml(self):
        import urllib2
        
        xml = urllib2.urlopen("http://cptflairbot.appspot.com/set.xml").read()
        root = etree.fromstring(xml)
        for gen in root:
            for pkmn in gen.findall('Pkmn'):
                css_class = pkmn.find('Class')
                if css_class == None:
                    css_class = pkmn.find('Name').text.lower()
                else:
                    css_class = css_class.text
                MainPage.VALID_CLASSES.append(css_class)
                for form in pkmn.findall('Form'):
                    css_class = form.find('Class')
                    if css_class != None:
                        MainPage.VALID_CLASSES.append(css_class.text)

app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
