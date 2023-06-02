import pandas as pd
import numpy as np
import sklearn
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.model_selection import GridSearchCV

def prepocess(origin_df):
    new_df = origin_df.copy()
    new_df["choose"].fillna("No Comment", inplace=True)
    new_df =new_df.drop('createdTime',axis=1)
    new_df = new_df.dropna(axis =1)
    Intcolumns = new_df.select_dtypes(include=[np.number])
    predictors= list(Intcolumns.columns.values.tolist())
    new_df[predictors] = new_df[predictors] / new_df[predictors].max()
    forTrain_df = new_df.copy()
    forTrain_df = forTrain_df[forTrain_df['choose']!="No Comment"]
    forTrain_df['choose'].replace({'Yes':1, 'No':0}, inplace=True)
    forTrain_df =pd.get_dummies(forTrain_df)
    print("forTrain_df looks like")
    print(forTrain_df.head())
    new_df = new_df.drop('choose',axis=1)
    new_df = pd.get_dummies(new_df)
    print("Examine  looks like")
    print(new_df.head())
    return  new_df,forTrain_df

def trainModelandPredict(forTrain_df,Exam_df):
    target_column = ['choose']
    predictors = list(set(list(forTrain_df.columns)) - set(target_column))
    X = forTrain_df[predictors].values
    y = forTrain_df[target_column].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=40)
    cols = len(forTrain_df.axes[1])
    mlp = MLPClassifier()
    # parameter_space = {
    #     'max_iter': [10, 100, 600, 1000],
    #     'hidden_layer_sizes': [(cols, cols, cols), (cols, cols * 2, cols), (cols, cols * 3, cols)],
    #     'activation': ['tanh', 'relu'],
    #     'solver': ['sgd', 'adam'],
    #     'alpha': [0.0001, 0.05, 0.1, 1],
    #     'learning_rate': ['constant', 'adaptive']
    # }
    parameter_space = {
        'max_iter': [10],
        'hidden_layer_sizes': [(cols, cols, cols)],
        'activation': ['tanh'],
        'solver': ['sgd'],
        'alpha': [0.05],
        'learning_rate': ['constant']
    }
    clf = GridSearchCV(mlp, parameter_space, n_jobs=-1, cv=3)
    clf.fit(X_train, y_train)
    results = pd.DataFrame(clf.cv_results_)
    Threashold = 0.9
    results = results.loc[results['mean_test_score']<Threashold]
    results.sort_values(by='rank_test_score', inplace=True)
    params_best = results.loc[0, 'params']
    thirdModel = MLPClassifier(**params_best)
    thirdModel.fit(X_train, y_train)
    predict_train = thirdModel.predict(X_train)
    predict_test = thirdModel.predict(X_test)
    print(confusion_matrix(y_train, predict_train))
    print(classification_report(y_train, predict_train))
    print("=============")
    print(confusion_matrix(y_test, predict_test))
    print(classification_report(y_test, predict_test))
    result = thirdModel.predict(Exam_df)
    print(result.size)
    return result

def predict(df,listofyear):
    normal_df = df.copy()
    a, b = prepocess(normal_df)
    predict_choose=trainModelandPredict(b, a)
    normal_df['year'] = pd.DatetimeIndex(normal_df['createdTime']).year
    print("data type of year is")
    print(normal_df['year'].dtype)
    for i, row in normal_df.iterrows():
        ifor_val = normal_df.at[i, 'choose']
        currentYear = int (normal_df.at[i, 'year'])
        if ifor_val == "No Comment" and listofyear.count(currentYear)>0:
            if predict_choose[i] == 0:
                ifor_val = "No"
            else:
                ifor_val = "Yes"
        normal_df.at[i, 'choose'] = ifor_val
    normal_df = normal_df.drop('year',axis=1)
    print("This is normal_df inside predict")
    print(normal_df.head())
    return normal_df

if __name__=='__main__':
    print("Hello World")
    df2023 = pd.read_csv('./csv/FYPQuestionaire2023.csv')
    df2022 = pd.read_csv('./csv/FYPQuestionaire2022.csv')
    df2021 = pd.read_csv('./csv/FYPQuestionaire2021.csv')
    df2020 = pd.read_csv('./csv/FYPQuestionaire2020.csv')
    df = pd.concat([df2020, df2021, df2022, df2023],
                   ignore_index=True,
                   sort=False)

