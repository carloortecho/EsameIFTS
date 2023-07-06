import hashlib
import PySimpleGUI as sg
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from tkinter import filedialog
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import matplotlib.pyplot as plt
import sqlite3

# Configurazione database
conn = sqlite3.connect('users.db')
conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
conn.close()

# Variabili globali per la codifica delle caratteristiche categoriche
label_encoders = []
onehot_encoders = []
model = None

# Funzione per l'hash della password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registrazione di un nuovo utente
def register_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()
        return False
    
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))
    conn.commit()
    conn.close()
    return True

# Login dell'utente
def login_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

# Caricare e leggere il file CSV
def load_csv(file_path):
    df = pd.read_csv(file_path, delimiter=';')
    return df

# Addestramento modello
def train_model(data):
    x = data.drop('QualityTest', axis=1)
    y = data['QualityTest']

    # Codifica delle caratteristiche categoriche
    global label_encoders, onehot_encoders
    label_encoders = []
    onehot_encoders = []
    for col in x.columns:
        if x[col].dtype == 'object':
            label_encoder = LabelEncoder()
            x[col] = label_encoder.fit_transform(x[col])
            label_encoders.append((col, label_encoder))

            onehot_encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
            x_encoded = onehot_encoder.fit_transform(x[col].values.reshape(-1, 1))
            onehot_encoders.append((col, onehot_encoder))

            # Aggiunta delle nuove colonne
            for i in range(x_encoded.shape[1]):
                x[col + '_' + str(i)] = x_encoded[:, i]

    # Rimozione delle colonne originali
    x = x.drop(columns=[col for col, _ in label_encoders])

    # Aggiunta di global model
    global model
    model = RandomForestClassifier()
    model.fit(x, y)
    return model

# Testing del modello
def test_model(data):
    x = data.copy()  # Crea una copia del DF di test
    x= data.drop("QualityTest", axis=1)

    

    # Codifica delle caratteristiche categoriche
    for col, label_encoder in label_encoders:
        if col in x.columns:
            x[col] = label_encoder.transform(x[col])

    for col, onehot_encoder in onehot_encoders:
        if col in x.columns:
            x_encoded = onehot_encoder.transform(x[col].values.reshape(-1, 1))
            for i in range(x_encoded.shape[1]):
                x[col + '_' + str(i)] = x_encoded[:, i]

    # Rimozione delle colonne originali
    x = x.drop(columns=[col for col, _ in label_encoders])

    y_pred = model.predict(x)
    accuracy = accuracy_score(data['QualityTest'], y_pred)
    return accuracy, y_pred

def plot_quality_test(df, y_pred):
    plt.figure(figsize=(8, 6))
    material_values = df['Materiale'].unique()
    uv_filter_values = df['ProtezioneUV'].unique()
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
    markers = ['o', 's', 'v', 'P', 'X', '*', '+']
    for material, color, marker in zip(material_values, colors, markers):
        for uv_filter in uv_filter_values:
            mask = (df['Materiale'] == material) & (df['ProtezioneUV'] == uv_filter)
            plt.scatter(df.loc[mask, 'Materiale'], df.loc[mask, 'ProtezioneUV'], color=color, marker=marker, label=f"{material} - {uv_filter}")

    plt.xlabel('Materiale')
    plt.ylabel('ProtezioneUV')
    plt.title('Risultati Quality Test')
    plt.legend()
    plt.show()


def open_file_dialog(window):
    root = sg.tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
    if file_path:
        df = load_csv(file_path)
        conn = sqlite3.connect('users.db')
        df.to_sql('data', conn, if_exists='replace', index=False)
        conn.close()
        sg.popup('File caricato e salvato nel database con successo!')
    else:
        sg.popup('Nessun file selezionato')

def open_file_dialog_prediction(window):
    root = sg.tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
    if file_path:
        df = load_csv(file_path)
        conn = sqlite3.connect('users.db')
        df_test = pd.read_sql_query('SELECT * FROM data', conn)
        conn.close()
        accuracy, y_pred = test_model(df_test)
        sg.popup(f"Accuracy: {accuracy}")
        plot_quality_test(df_test, y_pred)
    else:
        sg.popup('Nessun file selezionato')

def login_layout():
    sg.theme('DefaultNoMoreNagging')
    layout = [
        [sg.Text('Username')],
        [sg.Input(key='username')],
        [sg.Text('Password')],
        [sg.Input(key='password', password_char='*')],
        [sg.Button('Login'), sg.Button('Registrati')]
    ]
    return sg.Window('Login', layout, finalize=True)

def dashboard_layout(username):
    sg.theme('DefaultNoMoreNagging')
    layout = [
        [sg.Text(f'Utente connesso: {username}')],
        [sg.Button('Carica File')],
        [sg.Button('Inizia analisi')],
        [sg.Button('Predizione')],
        [sg.Button('Visualizza tutto')],
        [sg.Button('Logout')]
    ]
    return sg.Window('Dashboard', layout, finalize=True)

def main():
    login_window = login_layout()
    dashboard_window = None
    df_train = None

    while True:
        window, event, values = sg.read_all_windows()

        if window == login_window and event == sg.WINDOW_CLOSED:
            break

        if window == login_window and event == 'Login':
            username = values['username']
            password = values['password']
            user = login_user(username, password)
            if user:
                login_window.hide()
                dashboard_window = dashboard_layout(username)
            else:
                sg.popup('Username o password errati')

        if window == login_window and event == 'Registrati':
            username = values['username']
            password = values['password']
            registered = register_user(username, password)
            if registered:
                sg.popup('Registrazione completata con successo. Prego, acceda.')
            else:
                sg.popup("L'username esiste già. Per favore, scelga un username diverso.")

        if window == dashboard_window and event == sg.WINDOW_CLOSED:
            break

        if window == dashboard_window and event == 'Carica File':
            open_file_dialog(window)

        if window == dashboard_window and event == 'Inizia analisi':
            conn = sqlite3.connect('users.db')
            df_train = pd.read_sql_query('SELECT * FROM data', conn)
            conn.close()
            train_model(df_train)
            sg.popup('Modello addestrato con successo!')

        if window == dashboard_window and event == 'Predizione':
            if df_train is None:
                sg.popup('Per favore, prima caricare il file e addestrare il modello!')
            else:
                open_file_dialog_prediction(window)

        if window == dashboard_window and event == 'Visualizza tutto':
            conn = sqlite3.connect('users.db')
            df = pd.read_sql_query('SELECT * FROM data', conn)
            conn.close()
            plot_quality_test(df, None)

        if window == dashboard_window and event == 'Logout':
            dashboard_window.hide()
            login_window.un_hide()

    login_window.close()
    if dashboard_window:
        dashboard_window.close()

if __name__ == '__main__':
    main()
