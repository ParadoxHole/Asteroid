import firebase_admin
from firebase_admin import db, credentials, auth
import threading

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL":"https://forfourplayers-default-rtdb.europe-west1.firebasedatabase.app/"})

# Reference to the loginEvents node
login_events_ref = db.reference('loginEvents')

class FirebaseListener:
    def __init__(self, game):
        self.game = game
        self.listener = login_events_ref.listen(self.handle_new_entry)

    def handle_new_entry(self, event):
        print("New entry detected!")
        data = event.data
        user_id = data.get('userId')
        if user_id:
            try:
                # Fetch the user's email using the userId from Firebase Authentication
                user = auth.get_user(user_id)
                email = user.email
                arcade_id = data.get('arcadeId')
                player_seat = data.get('playerSeat')

                print(f'Client ID: {user_id}, Email: {email}, ArcadeID: {arcade_id}, PlayerSeat: {player_seat}')
                self.game.add_player(user_id, player_seat, email)
            except auth.AuthError as e:
                print(f'Error retrieving user data: {e}')
            except Exception as e:
                print(f'An unexpected error occurred: {e}')

    def stop(self):
        self.listener.close()

def start_listener(game):
    listener = FirebaseListener(game)
    return listener

def stop_listener(listener):
    listener.stop()
    
def save_score(user_id, new_score):
    score_ref = db.reference(f'users/{user_id}/scores')
    
    # Fetch current scores
    scores = score_ref.get() or []

    # Add the new score
    scores.append(round(new_score))

    # Sort scores in descending order and keep only the top 10
    scores = sorted(scores, reverse=True)[:10]

    # Update the scores in the database
    score_ref.set(scores)