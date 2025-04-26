from mongoengine import connect, disconnect

def connect_db():
    disconnect()
    connect(
        db="volunteer_coordinator_db",
        host="localhost",
        port=27017
    )
def connect_db2():
    disconnect()
    connect(
        db="manager_coordinator_db",
        host="localhost",
        port=27017,
        username=None,
        password=None,
    )