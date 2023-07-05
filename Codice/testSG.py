import PySimpleGUI as sg
import testSqlite3 as sql

# --- INTRO LAYOUT ---
def welcomeLayout():
    welcome_layout = [
        [sg.Text("Benvenuto! Selezionare l'opzione per iniziare...")],
        [sg.Button("Login")],
        [sg.Button("Registrati")], [sg.Button("Esci")]
    ]

    welcome_layout = sg.Window('Benvenuto', welcome_layout)
    while True:
        event, values = welcome_layout.read()
        if event == sg.WINDOW_CLOSED:
            exit()
        if event == 'Login':
            welcome_layout.close()
            #doLogin()
            user, password = doLogin()
            doDashboard(user,password)
            break
        elif event == 'Registrati':
            welcome_layout.close()
            registraUtente()
            break
        elif event == 'Esci':
            print('Programma terminato')
            exit()

# --- LOGIN ---
def doLogin():

    layout = [
        [sg.Text("Username")], [sg.InputText(key='-username-')],
        [sg.Text("Password")], [sg.InputText(key="-password-", password_char="*")],
        [sg.Button("Accedi")], [sg.Button("Menu")]
    ]


    login_window = sg.Window("Login username", layout)

    login = False

    while True:
        event, values = login_window.read()

        if event == sg.WINDOW_CLOSED:
            main()
            break
        elif event == "Accedi":
            # Verifica delle credenziali inserite
            username = values["-username-"]
            password = values["-password-"]
            
            isLogged = sql.loginUser(username, password)
            if (isLogged):
                login_window.close()
                return username, password
            else:
                sg.popup("Credenziali non valide. Riprova.")
                
        elif event == 'Menu':
            login_window.close()
            main()
            break
        
        
        
# --- REGISTRAZIONE ---
def registraUtente():

    registra_layout = [
        [sg.Text("Username")], [sg.InputText(key='reg_username')],
        [sg.Text("Password")], [sg.InputText(key="reg_password", password_char="*")],
        [sg.Text("Conferma password")], [sg.InputText(key="passwordconf", password_char="*")],
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
        elif event == "Registrati":
            username = values['reg_username']
            
            if (values['reg_password'] == values['passwordconf']):
                password = values['reg_password']
                registeredUser, reasons = sql.registerUser(username, password)
                
                if (registeredUser):
                    sg.popup("User registered successfull...")
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
def doDashboard(usr, pwd):
    dashboard_layout = [
        [sg.Text(f'Benvenuto {usr}', key='-zzz-')],
        [sg.Text("Benvenuto nella dashboard!")],
        [sg.Button("Carica dati CSV")],
        [sg.Button("Esegui machine learning")],
        [sg.Button("Logout")]
    ]

    winDashboard = sg.Window('Dashboard', dashboard_layout)

    while True:

        event, values = winDashboard.read()
       
        if event == sg.WINDOW_CLOSED:
            winDashboard.close()
            break
        if event == "Logout":
            winDashboard.close()
            main()
            break

def showErrorMessage(error):
    if (error == 'BadLogin'):
        print('No data found')

# --- REGISTRAZIONE ---
def registratiLayout():
    registerLayout = [
        [sg.Text("Username")], [sg.InputText(key='-username-')],
        [sg.Text("Password")], [sg.InputText(key="-password-", password_char="*")],
        [sg.Button("Accedi")]
    ]

# --- MAIN ---

def main():
    welcomeLayout()


if (__name__ == '__main__'):
    main()