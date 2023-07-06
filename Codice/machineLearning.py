import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

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