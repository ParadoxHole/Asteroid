import firebase_admin
from firebase_admin import db, credentials, auth

cred = credentials.Certificate("crendentials.json")
firebase_admin.initialize_app(cred, {"databaseURL":"https://forfourplayers-default-rtdb.europe-west1.firebasedatabase.app/"})

# Reference to the loginEvents node
login_events_ref = db.reference('loginEvents')

# Function to handle new entries
def handle_new_entry(event):
    print("New entry detected!")
    data = event.data
    user_id = data.get('userId')
    if user_id:
        try:
            # Fetch the user's email using the userId from Firebase Authentication
            user = auth.get_user(user_id)
            email = user.email
            name = user.display_name
            print(f'Client ID: {user_id}, Email: {email}, Name: {name}')
        except auth.AuthError as e:
            print(f'Error retrieving user data: {e}')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
        if listener:
            listener.close()
            print("Stopped listening for new login events.")
            

# Listen for new entries in the loginEvents node
listener = login_events_ref.listen(handle_new_entry)
