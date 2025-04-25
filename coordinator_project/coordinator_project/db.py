from mongoengine import connect

def connect_db():
    connect(
        db="volunteer_coordinator_db",
        host="localhost",
        port=27017
    )