from pathlib import Path
from sklearn.exceptions import InconsistentVersionWarning
import warnings
import os
import pickle
import pandas as pd
 
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

def prepOneHotEncoder(df, col, pathPackages):
    path = pathPackages / f'prep{col}.pkl'
    # print(f"Loading OneHotEncoder from {path}")

    oneHotEncoder = pickle.load(open(path, 'rb'))
    dfOneHotEncoder = pd.DataFrame(oneHotEncoder.transform(df[[col]]).toarray(),
                                   columns=[col + "_" + str(i+1) for i in range(len(oneHotEncoder.categories_[0]))])
    df = pd.concat([df.drop(col, axis=1), dfOneHotEncoder], axis=1)
    return df

def prepStandardScaler(df, col, pathPackages):
    path = pathPackages / f'prep{col}.pkl'
    # print(f"Loading StandardScaler from {path}")

    scaler = pickle.load(open(path, 'rb'))
    df[col] = scaler.transform(df[[col]])
    return df

def runModel(data, path):
    pathPackages = Path(path) / 'stream_pack' /'modelib' /'packages'
    pathPackages = pathPackages.resolve()
    # print(f"Path to packages: {pathPackages}")

    col_path = pathPackages / 'columnModelling.pkl'
    # print(f"Loading columns from {col_path}")

    col = pickle.load(open(col_path, 'rb'))

    df = pd.DataFrame(data, index=[0])
    df = df[col]

    df = prepOneHotEncoder(df, 'type', pathPackages)

    cols_to_scale = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
    for col in cols_to_scale:
        df = prepStandardScaler(df, col, pathPackages)

    X = df.values
    model_path = pathPackages / 'modelFraud.pkl'
    # print(f"Loading model from {model_path}")
    
    model = pickle.load(open(model_path, 'rb'))

    y = model.predict(X)[0]
    if y == 0:
        return "White List"
    else:
        return "Fraud"
