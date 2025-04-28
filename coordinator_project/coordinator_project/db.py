from mongoengine import connect, disconnect

def connect_db():
    disconnect()
    connect(
        db="coordinator_db",
        host="localhost",
        port=27017
    )
