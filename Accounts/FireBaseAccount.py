import firebase_admin
from firebase_admin import db, credentials

cred = credentials.Certificate("crendentials.json")
firebase_admin.initialize_app(cred, {"databaseURL":"https://players-7df06-default-rtdb.europe-west1.firebasedatabase.app/"})

# creating reference to root node
ref = db.reference("/")
# retrieving data from root node
ref.get()

db.reference("/name").get()
# set operation
db.reference("/videos").set(3)
ref.get()

# update operation (update existing value)
db.reference("/").update({"language": "python"})
ref.get()

# update operation (add new key value)
db.reference("/").update({"subscribed": True})
ref.get()

# push operation
db.reference("/titles").push().set("create modern ui in python")
ref.get()

# transaction
def increment_transaction(current_val):
    return current_val + 1

db.reference("/title_count").transaction(increment_transaction)
ref.get()

print(ref.key)