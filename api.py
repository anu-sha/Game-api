
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score, Position
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, RankForm, GameForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
GET_USER_GAMES=endpoints.ResourceContainer(
        user_name=messages.StringField(1),)



MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'



@endpoints.api(name='tic_tac_toe', version='v1')
class TicTacToeApi(remote.Service):
    """Game API"""

    #method to determine if the game is won
    def _is_game_won(self,positions):
         #game is won when the same user has picked any of these combinations 
         #[1,2,3],[4,5,6],[7,8,9],[1,5,9],[3,5,7],[1,4,7],[2,5,8],[3,6,9]
        user_indexes=positions 
        win_positions=[[1,2,3],[4,5,6],[7,8,9],[1,5,9],[3,5,7],[1,4,7],[2,5,8],[3,6,9]]
        for index in win_positions:
            #check if positions overlaps with any of the win positions
            matches=set(index) & set(user_indexes)
            #if count of overlapped positions is 3, the game is won
            if len(matches)==3:
                return True
        return False   


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User with an unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        player1 = User.query(User.name == request.player1_name).get()
        player2 = User.query(User.name == request.player2_name).get()

        #if the user is not found, throw an error
        if not player1 or not player2:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

        #create the game    
        game = Game.new_game(player1.key,player2.key)
               
        return game.to_form('Good luck with Tic Tac Toe!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        
        if game:
            return game.to_form('Game Status!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""

        #get user from db
        player = User.query(User.name == request.player).get()
        if not player:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        
        #if game not found raise an exception
        if not game:
            raise endpoints.NotFoundException('Game not found!')

        #check if this user is a player of this game or not
        validUser=game.player_one==player.key || game.player_two==player.key
        if not validUser
            raise endpoints.BadRequestException("Not a valid user of the game!!!")
        #if game is over     
        if game.game_over:
            raise endpoints.BadRequestException("Game is already over!!!")

        #if game has been cancelled     
        if game.game_cancelled:
            raise endpoints.BadRequestException("Game Cancelled!")

        #check if previous play was from another user and not this user
        length=len(game.current_status)
        if length!=0:
            last_user=game.current_status[length-1].user

            if last_user==player.key:
                raise endpoints.BadRequestException('Incorrect turn! You cannot have two consecutive turns')

        #check if current_status already has the position filled previously    
        exists=[x for x in game.current_status if x.index == request.move]
        if exists:
            raise endpoints.BadRequestException('Choose a different position! The position you have chosen has already been filled')

        #create position object to add to game_history
        position= Position(user=player.key,
                            index=request.move,result="None") 

        
                  
        #get positions of current player
        current_player_positions=[x.index for x in game.current_status if x.user==player.key]
        current_player_positions.append(request.move)
        if len(current_player_positions)>=3:
            #sort the positions 
            current_player_positions.sort()
            if self._is_game_won(current_player_positions):
                #the current user has won the game
                #update result and add to history
                position.result="You win"
                game.current_status.append(position) 
                #end the game and save
                game.end_game(True,player.key)
                game.put()
                return game.to_form('You win!')
            else:
                #if game is not won and all the positions are filled
                #the game is over
                if len(game.current_status)==9:
                    
                    game.end_game(True)
                    game.put()
                    return game.to_form("Game Over!It's a draw")
                else: 
                    #time for move by next player   
                    position.result="Next players' turn"
                    game.current_status.append(position) 
                    game.put()
                    return game.to_form("Next player's turn")    

        else:
            #the number of filled positions is less than 3
            #no need to check for game won
            position.result="Next players' turn"
            game.current_status.append(position) 
            game.put()
            
            return game.to_form("Next player's turn")

  

    @endpoints.method(request_message=GET_USER_GAMES,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return the users games."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games=User.game    
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='games/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancels the game if it is not already over."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            #game is found-chekc if game is complete
            if not game.game_over:
              #cancel the game
              game.game_cancelled=True
              game.put()
              return game.to_form('Game has been cancelled!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(response_message=ScoreForms,
                      path='games/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all the user rankings."""
        #get all users
        users=User.query().fetch()
        
        rankforms=[]
        #find user in score model and get number of games won
        for winner in users:
          scores=Score.query(Score.user==winner.key).fetch()
          rankforms.append(RankForm(user=winner.name,wins=len(scores)))
        return ScoreForms(items=rankforms)    

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        
        if game:
            return game.to_history()
        else:
            raise endpoints.NotFoundException('Game not found!')


api = endpoints.api_server([TicTacToeApi])
