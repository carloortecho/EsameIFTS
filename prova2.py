import PySimpleGUI as sg
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

loaded_data = None
database_file = 'user_database.db'
trained_classifier = None
logged_in = False

def create_user_table():
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

def welcomeLayout():
    welcome_layout = [
        [sg.Text("Benvenuto! Selezionare l'opzione per iniziare...")],
        [sg.Button("Login")],
        [sg.Button("Registrati")]
    ]

    welcome_window = sg.Window('Benvenuto', welcome_layout)
    while True:
        event, values = welcome_window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == 'Login':
            login, user, password = doLogin()
            if login:
                welcome_window.close()
                doDashboard(user, password)
                break
        elif event == 'Registrati':
            register()
            break

    welcome_window.close()

def loadCSV(file_path):
    global loaded_data
    loaded_data = pd.read_csv(file_path, sep=";")
    print("CSV data loaded successfully.")

def makePredictions():
    global loaded_data, trained_classifier
    if loaded_data is None:
        print("Error: Load CSV data first.")
        return

    data = loaded_data.copy()
    # Preprocess the data similar to the training data
    X = data.drop('QualityTest', axis=1)
    X_encoded = pd.get_dummies(X)

    # Make predictions using the trained classifier
    y_pred = trained_classifier.predict(X_encoded)

    # Create a new DataFrame with the predicted column
    predicted_data = data.copy()
    predicted_data['QualityTest_Predicted'] = y_pred

    print("Predicted data:")
    print(predicted_data)

    return predicted_data

def addPredictedColumn(file_path):
    global loaded_data
    if loaded_data is None:
        print("Error: Load CSV data first.")
        return

    predicted_data = makePredictions()

    new_data = pd.read_csv(file_path, sep=";")
    if 'QualityTest_Predicted' in new_data.columns:
        predicted_values = predicted_data['QualityTest_Predicted'].map({0: "fallito", 1: "passato"})
        new_data.loc[new_data['QualityTest_Predicted'] == " ", 'QualityTest_Predicted'] = predicted_values[new_data['QualityTest_Predicted'] == " "]
    else:
        new_data.insert(new_data.shape[1], 'QualityTest_Predicted', predicted_data['QualityTest_Predicted'].map({0: "fallito", 1: "passato"}))

    
    print (new_data)
    
    new_data.to_csv(file_path, index=False)
    print("Predicted column added to the CSV.")




def runMachineLearning():
    global loaded_data, trained_classifier
    if loaded_data is None:
        print("Error: Load CSV data first.")
        return

    data = loaded_data.copy()

    # Divide the dataset into attributes (features) and target (QualityTest column)
    X = data.drop('QualityTest', axis=1)  # features
    y = data['QualityTest']  # target

    # Encode the target labels
    le = LabelEncoder()
    y = le.fit_transform(y)

    # Apply one-hot encoding to categorical columns
    X_encoded = pd.get_dummies(X)

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

    # Train the Decision Tree classifier
    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train)

    # Perform predictions on the test set
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)

    # Store the trained classifier for later use
    trained_classifier = clf

    plt.figure()
    plt.plot(y_test, label='Actual')
    plt.plot(y_pred, label='Predicted')
    plt.xlabel('Sample')
    plt.ylabel('QualityTest')
    plt.legend()
    plt.show()

def showData():
    global loaded_data
    if loaded_data is None:
        print("Error: Load CSV data first.")
        return

    data = loaded_data.copy()
    print("Loaded data:")
    print(data)

def doLogin():
    layout = [
        [sg.Text("Username")], [sg.InputText(key="-username-")],
        [sg.Text("Password")], [sg.InputText(key="-password-", password_char="*")],
        [sg.Button("Accedi")]
    ]

    login_window = sg.Window("Login", layout)
    login = False
    username, password = None, None

    while True:
        event, values = login_window.read()

        if event == sg.WINDOW_CLOSED:
            login_window.close()
            return False, None, None
        if event == "Accedi":
            username = values["-username-"]
            password = values["-password-"]

            conn = sqlite3.connect(database_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
            result = cursor.fetchone()
            conn.close()

            if result is not None:
                login = True
                login_window.close()
                return login, username, password
            else:
                sg.popup("Credenziali non valide. Riprova.")

def register():
    layout = [
        [sg.Text("Username")], [sg.InputText(key="-username-")],
        [sg.Text("Password")], [sg.InputText(key="-password-", password_char="*")],
        [sg.Text("Email")], [sg.InputText(key="-email-")],
        [sg.Button("Registrati")]
    ]

    register_window = sg.Window("Registrazione", layout)

    while True:
        event, values = register_window.read()

        if event == sg.WINDOW_CLOSED:
            register_window.close()
            return
        if event == "Registrati":
            username = values["-username-"]
            password = values["-password-"]
            email = values["-email-"]

            conn = sqlite3.connect(database_file)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, password, email))
            conn.commit()
            conn.close()

            sg.popup("Registrazione completata con successo!")
            register_window.close()
            return

def doDashboard(usr, pwd):
    sg.theme("Default1")

    layout = [
        [sg.Text(f"Benvenuto {usr}", key="-zzz-")],
        [sg.Text("Benvenuto nella dashboard!")],
        [sg.Button("Carica dati CSV")],
        [sg.Button("Visualizza dati CSV")],
        [sg.Button("Esegui machine learning")],
        [sg.Button("Prevedi su nuovo CSV")],
        [sg.Button("Logout")],
        [sg.Button("Refresh")]
    ]

    winDashboard = sg.Window("Dashboard", layout)

    while True:
        event, values = winDashboard.read()

        winDashboard["-zzz-"].update(usr)

        if event == sg.WINDOW_CLOSED:
            break
        if event == "Logout":
            winDashboard.close()
            main()
            break
        if event == "Carica dati CSV":
            file_path = sg.popup_get_file("Seleziona il file CSV", file_types=(("CSV Files", "*.csv"),))
            if file_path:
                loadCSV(file_path)
        if event == "Visualizza dati CSV":
            showData()
        if event == "Esegui machine learning":
            runMachineLearning()
        if event == "Prevedi su nuovo CSV":
            file_path = sg.popup_get_file("Seleziona il file CSV", file_types=(("CSV Files", "*.csv"),))
            if file_path:
                addPredictedColumn(file_path)
        if event == "Refresh":
            winDashboard["-zzz-"].update(usr)

    winDashboard.close()

def main():
    create_user_table()
    welcomeLayout()
    login, user, password = doLogin()
    if login:
        logged_in = True
        doDashboard(user, password)

# --- MAIN ---
if __name__ == "__main__":
    clf = None  # Initialize clf as None
    main()
