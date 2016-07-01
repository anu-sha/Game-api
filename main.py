#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import GuessANumberApi

from models import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games."""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            for game in user.games:
                game_object=game.get()  
                if not game_object.game_over or not game_object.game_cancelled:
                    subject = 'This is a reminder!'
                    body = 'Hello {}, continue the game tic tac toe!'.format(user.name)
                    # This will send test emails, the arguments to send_mail are:
                    # from, to, subject, body
                    mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                                   user.email,
                                   subject,
                                   body)





app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    
], debug=True)
