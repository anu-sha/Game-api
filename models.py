"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()

class Position(ndb.Model):
    """Represents board position"""
    user=ndb.KeyProperty(required=True, kind='User')
    index=  ndb.IntegerProperty(required=True)  


class Game(ndb.Model):
    """Game object"""
   
    game_over = ndb.BooleanProperty(required=True, default=False)
    player_one = ndb.KeyProperty(required=True, kind='User')
    player_two = ndb.KeyProperty(required=True, kind='User')
    winner = ndb.KeyProperty(required=True, kind='User')
    player_one_moves = ndb.IntegerProperty(repeated=True)
    player_two_moves = ndb.IntegerProperty(repeated=True)
    current_status= ndb.KeyProperty(kind='Position', repeated=True)

    @classmethod
    def new_game(cls, player1,player2):
        """Creates and returns a new game"""
        
        game = Game(player_one= player1,
                    player_two=player2,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player1_name = self.player_one.get().name
        form.player2_name = self.player_two.get().name
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    moves = ndb.IntegerProperty(required=True, repeated=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), moves=self.guesses)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    player1_name = messages.StringField(2, required=True)
    player2_name = messages.StringField(3, required=True)
    current_game=messages.IntegerField(4, repeated=True)
    game_over = messages.BooleanField(5, required=True)
    message = messages.StringField(6, required=True)
    


class NewGameForm(messages.Message):
    """Used to create a new game"""
    player1_name = messages.StringField(1, required=True)
    player2_name = messages.StringField(2, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    player = messages.StringField(1, required=True)
    move = messages.IntegerField(2, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    moves = messages.IntegerField(4, required=True, repeated=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
