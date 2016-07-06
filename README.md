#Tic Tac Toe Game Api

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
Tic Tac Toe is a two player game played on a 3X3 grid. On each turn, users choose an index. 
The game is won when the user chooses indexes such that all line up in a row or a column or diagnolly. 
'Moves' are sent to the `make_move` endpoint which will reply
with either: 'next player turn', 'you win', or 'game over' (if all the indexes are filled.)
Many different Tic Tac Toe games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: player1_name, playe2_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game with the two playerd provided. Player names 
      provided must correspond to an existing user - will raise a NotFoundException if not.

     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, position, player
    - Returns: GameForm with current game state.
    - Description: Accepts the player and position(1 to 9) and returns the updated state 
      of the game. If this causes a game to end or win, a corresponding Score entity will be created.


 - **get_user_rankings**
    - Path: 'games/ranking'
    - Method: GET
    - Parameters: None
    - Returns: RankForms
    - Description: Returns all users and their number of wins (unordered). 
      The ranking criteria used is the win ratio - games won/games played
      
 - **get_game_history**
    - Path: 'game/history/{urlsafe_game_key'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForm
    - Description: Returns all the moves and the result messages of a game
      Throws a Game not Found exception if game is not found
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **cancel_game**
    - Path:'games/{urlsafe_game_key}
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameForm
    - Description: Cancels a game if it is not over yet
      Throws a Game Not Found exception if game is not found
      Throws a bad request exception if the game is already over
   
 - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms
    - Description: Returns all games played by the user.
      Throws a user not found exception if user is not a valid user

 

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
     
 - **Position**
    - Records the user at an index. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, player1_name, player2_name, 
             history, game_over, game_cancelled, message ).
 - **GameForms**
    - Representation of multiple game forms
 
 - **HistoryForm**
    - Representation of each move in the game (plater, position, result)
    
 - **RankForm**
    - Representation of a user's wins (user, wins)
    
 - **NewGameForm**
    - Used to create a new game (player1_name, player2_name)
    
 - **MakeMoveForm**
    - Inbound make move form (player, move).
    
 - **RankForms**
    - Multiple Rank forms container.

 - **StringMessage**
    - General purpose String container.
