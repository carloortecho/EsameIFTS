import PySimpleGUI as sg
import userManager as sql
from machineLearning import loadCSV, addPredictedColumn, runMachineLearning, showData
import pandas as pd

# --- INTRO LAYOUT ---
def welcomeLayout():
    sg.theme('Topanga')

    welcome_layout = [
        [sg.Text("Benvenuto! Selezionare l'opzione per iniziare...")],
        [sg.Button("Login")],
        [sg.Button("Registrati")], 
        [sg.Button("Esci")]
    ]

    welcome_layout = sg.Window('Benvenuto', welcome_layout)
    while True:
        event, values = welcome_layout.read()
        # Lettura eventi dashboard iniziale
        if event == sg.WINDOW_CLOSED or event == 'Esci':
            print('Programma terminato')
            exit()
        if event == 'Login':
            welcome_layout.close()
            user = doLogin()
            if user:
                doDashboard(user)
            else:
                sg.popup('Login failed...')
            break

        if event == 'Registrati':
            welcome_layout.close()
            registraUtente()
            break

# --- LOGIN ---
def doLogin():

    layout = [
        [sg.Text("Username")], [sg.InputText(key='-username-')],
        [sg.Text("Password")], [sg.InputText(key="-password-", password_char="*")],
        [sg.Button("Accedi")], [sg.Button("Menu")]
    ]


    login_window = sg.Window("Login username", layout)

    while True:
        event, values = login_window.read()

        if event == sg.WINDOW_CLOSED:
            main()
            break

        if event == "Accedi":
            # Verifica delle credenziali inserite
            username = values["-username-"]
            password = values["-password-"]
            
            isLogged = sql.loginUser(username, password)
            if (isLogged):
                login_window.close()
                return username
            else:
                sg.popup("Credenziali non valide. Riprova.")
                
        if event == 'Menu':
            login_window.close()
            main()
            break
        
        
        
# --- REGISTRAZIONE ---
def registraUtente():

    registra_layout = [
        [sg.Text("Username")], [sg.InputText(key='reg_username')],
        [sg.Text("Password")], [sg.InputText(key="reg_password", password_char="*")],
        [sg.Text("Conferma password")], [sg.InputText(key="passwordconf", password_char="*")],
        [sg.Text('La password deve avere le seguenti caratteristiche:\n • Lunghezza minima: 8 caratteri\n • Almeno una lettera maiuscola\n • Almeno un numero \n • Almeno un carattere speciale: ' + r'[!@#$%^&/()+\-*/]')],
        [sg.Button("Registrati")],
        [sg.Text(size=(40,1), key='-OUTPUT-', text_color='red')],
        [sg.Button("Menu")]
    ]
    
    registra_window = sg.Window("Registra utente", registra_layout)
    
    while True:
        event, values = registra_window.read()

        if event == sg.WINDOW_CLOSED:
            registra_window.close()
            main()
            break

        if event == "Registrati":

            username = values['reg_username']
            
            if (values['reg_password'] == values['passwordconf']):
                password = values['reg_password']
                registeredUser, reasons = sql.registerUser(username, password)
                
                if (registeredUser):
                    sg.popup("User registered successful...")
                    registra_window.close()
                    main()
                    break
                else:
                    error_message = '\n'.join(reasons)
                    registra_window['-OUTPUT-'].update(error_message)
            else:
                sg.popup("La password non coincide.")
                
        elif event == 'Menu':
            registra_window.close()
            main()
            break

# --- DASHBOARD ---
def doDashboard(usr):
    dashboard_layout = [
        [sg.Text(f'Benvenuto {usr[0].upper() + usr[1:]}')],
        [sg.Button("Carica dati CSV")],
        [sg.Button('Visualizza dati CSV')],
        [sg.Button("Esegui machine learning")],
        [sg.Button("Prevedi su nuovo CSV")],
        [sg.Button("Cerca dati CSV")],
        [sg.Button("Logout")],
        [sg.Text("File CSV non caricato...", text_color='red', key='-statusCSV-')]
    ]

    winDashboard = sg.Window('Dashboard', dashboard_layout)

    while True:

        event, values = winDashboard.read()
       
        if event == sg.WINDOW_CLOSED:
            exit()

        if event == 'Carica dati CSV':
            file_path = sg.popup_get_file("Seleziona il file CSV", file_types=(("CSV Files", "*.csv"),))
            if file_path:
                loadCSV(file_path)
                winDashboard['-statusCSV-'].update('File CSV caricato', text_color='green')
            
        if event == "Visualizza dati CSV":
            showData()
            
        if event == "Esegui machine learning":
            runMachineLearning()
            
        if event == "Prevedi su nuovo CSV":
            file_path = sg.popup_get_file("Seleziona il file CSV", file_types=(("CSV Files", "*.csv"),))
                
            if file_path:
                addPredictedColumn(file_path)
                
        if event == "Cerca dati CSV":
            csvToCheck = sg.popup_get_file("Seleziona il file CSV", file_types=(("CSV Files", "*.csv"),))
            if csvToCheck:
                searchCSV(csvToCheck)

        if event == "Logout":
            winDashboard.close()
            main()
            break

# --- CERCA CSV ---
def searchCSV(csvToCheck):

    operators = ['==', '!=', '>', '>=', '<', '<=']

    search_layout = [
        [sg.Text('Marca:')], [sg.InputText(key='-Marca-')],
        [sg.Text('Modello:')], [sg.InputText(key='-Modello-')],
        [sg.Text('Colore:')], [sg.InputText(key='-Colore-')],
        [sg.Text('Materiale:')], [sg.InputText(key='-Materiale-')],
        [sg.Text('Dimensione:')], [sg.InputText(key='-Dimensione-')],
        [sg.Text('Prezzo:')], [sg.InputText(key='-Prezzo-')],
        [sg.Text("Seleziona un operatore:")], [sg.Combo(operators, key="-OPERATOR-", default_value=operators[0], enable_events=True)],
        [sg.Text('Tipo:')], [sg.InputText(key='-Tipo-')],
        [sg.Text('ProtezioneUV:')], [sg.InputText(key='-Protezioneuv-')],
        [sg.Button("Cerca")],
        [sg.Button("Back")],
        [sg.Text(f'Search CSV: {csvToCheck}', text_color='green')]
    ]

    winSearchDashboard = sg.Window('Dashboard', search_layout)
    
    while True:

        event, values = winSearchDashboard.read()
       
        if event == sg.WINDOW_CLOSED or event == 'Back':
            winSearchDashboard.close()
            break

        if event == 'Cerca':
            # Load the CSV data into a DataFrame
            data = pd.read_csv(csvToCheck)

            # Extract the operator selected for the price
            operator = values['-OPERATOR-']

            # Preprocess the input values and handle empty inputs
            filters = {}
            for key, value in values.items():
                if (key != '-OPERATOR-'):
                    if key.startswith('-') and key.endswith('-'):
                        field = key[1:-1]  # Remove the leading and trailing '-' characters
                        if value:  # Handle empty inputs
                            filters[field] = value

            # Filter the data based on the user input
            if filters:
                filtered_data = data.copy()
                for field, value in filters.items():
                    if field == 'Prezzo':
                        price = int(value)
                        if operator == '==':
                            filtered_data = filtered_data[filtered_data[field] == price]
                        elif operator == '!=':
                            filtered_data = filtered_data[filtered_data[field] != price]
                        elif operator == '>':
                            filtered_data = filtered_data[filtered_data[field] > price]
                        elif operator == '>=':
                            filtered_data = filtered_data[filtered_data[field] >= price]
                        elif operator == '<':
                            filtered_data = filtered_data[filtered_data[field] < price]
                        elif operator == '<=':
                            filtered_data = filtered_data[filtered_data[field] <= price]
                    else:
                        filtered_data = filtered_data[filtered_data[field].astype(str).str.contains(value, case=False, na=False)]
            else:
                filtered_data = data.copy()

            # Display the filtered data
            sg.popup_scrolled(filtered_data.to_string(), title='Risultati Ricerca')


# --- MAIN ---

def main():
    welcomeLayout()


if (__name__ == '__main__'):
    main()