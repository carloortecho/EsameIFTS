import sqlite3 as sql
import os
import bcrypt as bc

path = os.getcwd()
db_name = 'dbUsers.db'
db_path = path + f'\\Database\\{db_name}'

# --- CREATE DB AND TABLES ---
def createDB():
    try:
        conn = sql.connect(db_path)
        cursor = conn.cursor()

        createDB_query = '''CREATE TABLE IF NOT EXISTS Users
                            (
                            idutente INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                            username varchar(20) NOT NULL UNIQUE,
                            password varchar(20) NOT NULL
                            )'''

        cursor.execute(createDB_query)
        print('Database created successful...')

    except sql.Error as e:
        print(f'Commit failed. Reason: {e}')

    finally:
        conn.close()
        print('Connection to database closed...')

# --- REGISTER USER ---

def registerUser(usr, pwd):
    try:
        conn = sql.connect(db_path)
        cursor = conn.cursor()
        
        # PASSWORD CYPHER
        hashed_pwd = bc.hashpw(pwd.encode('utf-8'), bc.gensalt())

        registerUser_query = '''INSERT INTO Users (username, password) VALUES (?, ?) '''

        cursor.execute(registerUser_query, (usr, hashed_pwd))
        print('User registered successfull...')
        conn.commit()
        registerStatus = True
        
    except sql.Error as e:
        print(f'Commit failed... Reason: {e}')
        registerStatus = False
        
    finally:
        conn.close()
        print('Connection to database closed...')
    
    return registerStatus
        
# --- LOGIN USER ---
def loginUser(usr, pwd):
    try:
        conn = sql.connect(db_path)
        cursor = conn.cursor()
        
        loginUser_query = '''SELECT username, password
                             FROM Users
                             WHERE username = ?'''
        
        cursor.execute(loginUser_query, (usr,))
        row = cursor.fetchone()
        
        # Check if user exists...
        if (row is not None):
            stored_usr, stored_pwd = row
            if (bc.checkpw(pwd.encode('utf-8'), stored_pwd)):
                loginStatus = True
            else:
                loginStatus = False
        else:
            loginStatus = False
        
         #loginStatus = bool(row)
        
    except sql.Error as e:
        print(f'Commit failed... Reason: {e}')
        loginStatus = False
        
    finally:
        conn.close()
        print('Connection to database closed...')
        
    return loginStatus