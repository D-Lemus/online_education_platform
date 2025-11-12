#IMPORTS
#   importing os helps us access the environment variables
#   such as DB urls and API keys
import os

#   loads all variables from .env file into the environment
#   meaning that I can call os.getenv(MONGO_URI) and it will find it there
from dotenv import load_dotenv

#   Main entrypoint from Pymongo that allows python to connect to the mongodb database
from pymongo import MongoClient
#--------------------------------------------------------------------------

#FIRST STEP: Loading environment variables...
#   this functions searches the (k,v) pairs from the project
#   (like the name of the database and the url)
load_dotenv()

#--------------------------------------------------------------------------

#SECOND STEP: Connect to the environment
#   os.getenv(key,default_value)
#   try to connect using the key and if not use defaul value(same as the key)
MONGO_URI = os.getenv("MONGO_URI","mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME","online_edu")

#--------------------------------------------------------------------------

#THIRD STEP: Create Mongo Client
#   The mongoclient establishe conection with MongoDB
#   when the first operation is run, the connection opens. not before
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

#--------------------------------------------------------------------------
#FOURTH STEP: Dependency Function for FastAPI
'''
In FastAPI dependencies are small, reusable functions that can be like injected
onto the route handlers automatically by using the function 'Depends'.
This allows each rout to just declare a db = Depends(get_mongo_db) and get access.

In short terms just returns a database but this controls when you connect to
the Mongo db.

'''
def get_mongo_db():

    return db


"""
---IN SUMMARY ---
We imported some libraries to help python connect to mongo db and for the code
to be able to connect to os .env variables so we can be able to search for the db
DB URI and DB name. we made the connection to the db possible including a function
that allows the routing for the MongoDB database
"""
