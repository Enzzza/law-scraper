import sqlite3
import json
import uuid



def connect_to_db(dbName):
    global conn
    global c
    conn = sqlite3.connect(f"{dbName}.db")
    c = conn.cursor()

def create_table():
    c.execute("""CREATE TABLE lawyers (
            id text UNIQUE,
            name text,
            email text,
            sent integer
            )""")

def insert_lawyer(name, email):
    id = str(uuid.uuid4())
    with conn:
        c.execute("INSERT INTO lawyers VALUES (:id, :name, :email, :sent)", {'id':id, 'name': name, 'email': email, 'sent': False})

def insert_from_json():
    with open('lawyers.json') as json_file:
        data = json.load(json_file)
        for l in data['lawyers']:
            insert_lawyer(l["name"],l["email"])

def print_database():
    c.execute("SELECT * FROM lawyers")
    print(c.fetchall())


def main():
    connect_to_db("lawyers")
    create_table()
    insert_from_json()
    print_database()
    

if __name__ == "__main__":
    main()