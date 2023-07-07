import sqlite3 as sql
import os

# Create DB to CSV
path = os.getcwd()
db_name = 'dbGlasses.db'
db_path = path + f'\\Database\\{db_name}'

def createDB():
    try:
        conn = sql.connect(db_path)
        cursor = conn.cursor()

        createDB_query = '''CREATE TABLE IF NOT EXISTS Glasses
                            (
                            id INTEGER PRIMARY KEY NOT NULL UNIQUE,
                            marca varchar(20) NOT NULL,
                            modello varchar(20) NOT NULL,
                            colore varchar(20) NOT NULL,
                            materiale varchar(20) NOT NULL,
                            dimensione varchar(20) NOT NULL,
                            prezzo integer NOT NULL,
                            tipo varchar(20) NOT NULL,
                            protezioneuv varchar(20) NOT NULL
                            )'''

        cursor.execute(createDB_query)
        print('Database created successful...')

    except sql.Error as e:
        print(f'Error to create Database. Reason: {e}')

    finally:
        conn.close()
        print('Connection to database closed...')

def countRows(cursor, queryToCheck):
    cursor.execute(queryToCheck)
    count_result = cursor.fetchone()
    record_count = count_result[0]

    return record_count
    

def insertDataFromCSV(csvFile):
    try:
       conn = sql.connect(db_path)
       cursor = conn.cursor()

       with open(csvFile, 'r') as file:
              lines = file.readlines()

              for line in lines[1:]:
                     # Split the line into values
                     values = line.strip().split(';')
                     insert_query = 'INSERT INTO Glasses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
                     cursor.execute(insert_query, values)

       conn.commit()

       count_query = 'SELECT COUNT(*) from Glasses'
       record_count = countRows(cursor, count_query)
       print(f'Fields added: {record_count}')

    except (sql.Error or FileNotFoundError) as e:
        print(f'Error catch... Reason: {e}')
    
    finally:
        conn.close()

def showDataFromCSV():
     try:
       conn = sql.connect(db_path)
       cursor = conn.cursor()

       queryData = '''SELECT *
                      FROM Glasses
                      ORDER BY Glasses.id'''
       
       cursor.execute(queryData)

       rows = cursor.fetchall()
      
     except sql.Error as e:
        print(f'Error catch... Reason: {e}')
    
     finally:
        conn.close()

     return rows

def deleteData_FromDB():
     try:
       conn = sql.connect(db_path)
       cursor = conn.cursor()

       count_query = 'SELECT COUNT(*) from Glasses'
       record_count = countRows(cursor, count_query)

       queryData = 'DELETE FROM Glasses'
       cursor.execute(queryData)

       conn.commit()

       print(f'{record_count} fields deleted....')
      
     except sql.Error as e:
        print(f'Error catch... Reason: {e}')
    
     finally:
        conn.close()