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

REDDIT = "http://www.reddit.com"
SUBREDDIT = "casualpokemontrades"
CREDENTIALS = {'user': "CPTFlairBot", 'passwd': "???"}
USER_AGENT = "Scheduled Casual Pokemon Trades Flair Bot 1.0 by /u/richi3f"
VALID_CLASSES = []

def parse_xml():
    global VALID_CLASSES
    def get_classes(parent):
        # Returns all the classes of a <Pkmn /> element
        def get_class(parent):
            # Returns the CSS class of a <Pkmn /> or <Form /> element
            css_class = pkmn.find('Class')
            if css_class == None:
                css_class = pkmn.find('Name').text.lower()
            else:
                css_class = css_class.text
            return css_class
        
        classes = [get_class(parent)]
        
        for child in parent.findall('Form'):
            classes.append(get_class(child))
        
        return classes
    
    xml = urllib2.urlopen("http://cptflairbot.appspot.com/set.xml").read()
    root = etree.fromstring(xml)
    for gen in root:
        for pkmn in gen.findall('Pkmn'):
            VALID_CLASSES += get_classes(pkmn)

def reddit_api(action, params=None):
    if params:
        req = urllib2.Request(REDDIT + action, urllib.urlencode(params))
    else:
        req = urllib2.Request(REDDIT + action)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

class CptFlairBot(webapp2.RequestHandler):   
    def get(self):
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
            print "Login failure"
            exit(1)
        # Obtain unread messages
        unread = reddit_api("/message/unread/.json")
        modhash = unread['data']['modhash']
        read = []
        csv = ""
        # Iterate though messages
        messages = unread['data']['children']
        cmp_by_time = lambda x, y: cmp(x['data']['created'], y['data']['created'])
        for message in sorted(messages, cmp_by_time):
            read.append(message['data']['name'])
            # Determine if valid flair
            if message['data']['subject'].lower() != "flair":
                continue
            user = message['data']['author']
            body = message['data']['body']
            regex = re.compile('^(.+(?= \| \d)) \| (\d{4}-\d{4}-\d{4}) \| ([a-z-]+)')
            match = regex.match(body)
            if match:
                in_game_name, friend_code, css_class = match.group(1,2,3)
                if len(in_game_name) <= 12 and css_class in VALID_CLASSES:
                    csv += "%s,%s,%s\n" % (user, ' | '.join([friend_code, in_game_name]), css_class)
        # Update flairs
        if csv != "":
            reddit_api("/api/flaircsv.json", {'r': SUBREDDIT, 'flair_csv': csv, 'uh': modhash})
        # Mark messages as read
        if len(read) > 0:
            reddit_api("/api/read_message", {'id': ','.join(read), 'uh': modhash})
        self.response.write(csv.replace('\n', '<br>'))

app = webapp2.WSGIApplication([
    ('/cptflairbot', CptFlairBot)
], debug=False)
