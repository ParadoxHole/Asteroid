import firebase_admin
from firebase_admin import credentials, db
import time

# Initialize Firebase Realtime Database
cred = credentials.Certificate("crendentials.json")
firebase_admin.initialize_app(cred, {"databaseURL":"https://forfourplayers-default-rtdb.europe-west1.firebasedatabase.app/"})


# Function to handle login event in your Python game
def handle_login(event):
    # Extract relevant information from the login event
    user_id = event['data']['userId']
    timestamp = event['data']['timestamp']

    # Log in the user in your game
    # Example: Perform authentication logic here using the user ID
    print(f"User {user_id} logged in at {timestamp}")

# Set up a listener for login events in the Firebase Realtime Database
ref = db.reference('loginEvents')

# Loop to continuously listen for login events
while True:
    # Start listening for changes in the database
    listener = ref.listen(handle_login)

    # Wait for some time (e.g., 10 seconds) before checking again
    time.sleep(10)

    # Stop listening to prevent memory leaks
    listener.close()
