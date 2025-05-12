from pymongo import MongoClient
import os

mongoClient = MongoClient(os.environ['MONGO_URL'])
dbClient = mongoClient["sanji"]