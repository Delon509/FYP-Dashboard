import os

from dash import Dash, dash_table, dcc, html , no_update,ctx
from dash.exceptions import PreventUpdate
from datetime import datetime
import time
from dash.dependencies import Input, Output
import pandas as pd
from app import  app
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from neuralFunction import predict
df = pd.read_csv('./store/origin.csv')
clone_df = df.copy()
clone_df["createdTime"]= pd.DatetimeIndex(clone_df["createdTime"]).year
predicted_df = pd.DataFrame();
allYear = clone_df["createdTime"].drop_duplicates().sort_values().tolist()
AI_layout = html.Div([
html.H1("AI predict Parents' choice",
                            style={"textAlign": "center"}),
    html.H4("Choose Years you want to predict",
                            style={"textAlign": "center"}),
    dcc.Dropdown(clone_df["createdTime"].drop_duplicates().sort_values().append(pd.Series(["All"])), id='year',multi=True),
    html.Button('Predict', id='btn-predict', n_clicks=0),
    dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id='before-after-container')
        ),
    html.Div([
        dbc.Row([
        dbc.Col([
            html.H4("Input the file name for saving the predicted dataframe",style={"textAlign": "center"})
        ], width=12),
        dbc.Col([
            dcc.Input(id='filename',value="predictedAt"+datetime.now().strftime('%m-%d-%Y'), type='text'),
        ])
    ]),
dbc.Row([
    html.Div(id='generate-message')
    ]),
dbc.Row([
    html.Button('Save', id='btn-save', n_clicks=0),
    ]),
    ], style = dict(display='none'),id='saveDiv')
]),


@app.callback(
    Output('before-after-container', 'children'),
    Output('saveDiv', 'style'),
    [Input('year', 'value')],
    Input('btn-predict','n_clicks'),
    prevent_initial_call=True
)
def Test(listofyear,btn_predict):
    if len(listofyear) == 0:
        return no_update, no_update
    if "All" in listofyear:
        listofyear = allYear
    if "btn-predict" == ctx.triggered_id:
        if os.path.exists("./store/new.pkl"):
            os.remove("./store/new.pkl")
        labels = ["Yes","No","No Comment"]
        IntlistofYear = []
        for i in range(0, len(listofyear)):
            IntlistofYear.append(int(listofyear[i]))
        predicted_df = predict(df,IntlistofYear)
        predicted_df.to_pickle('./store/new.pkl')
        print("This is the predicted_df in AI callback")
        print(predicted_df.head())
        clone_predicted_df = predicted_df.copy()
        clone_predicted_df["createdTime"] = pd.DatetimeIndex(clone_predicted_df["createdTime"]).year
        Graphs = []
        for column in listofyear:
            values = []
            #Generate Before Graph
            temp_dict_single = clone_df.query("createdTime ==" + str(column))["choose"].value_counts()
            for label in labels:
                if label in temp_dict_single:
                    values.append(temp_dict_single[label])
                else:
                    values.append(0)
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, title="Year "+ str(column) +" Before Using AI Prediction")])
            temp = dcc.Graph(id="Year "+ str(column) +" Before Using AI Prediction", figure=fig)
            Graphs.append(temp)
            #Generate After Graph
            values = []
            temp_dict_single = clone_predicted_df.query("createdTime ==" + str(column))["choose"].value_counts()
            for label in labels:
                if label in temp_dict_single:
                    values.append(temp_dict_single[label])
                else:
                    values.append(0)
            fig = go.Figure(data=[
                go.Pie(labels=labels, values=values, title="Year " + str(column) + " After Using AI Prediction")])
            temp = dcc.Graph(id="Year " + str(column) + " After Using AI Prediction", figure=fig)
            Graphs.append(temp)
        return Graphs,dict()
    else:
        return no_update, no_update
@app.callback(
    Output('generate-message', 'children'),
    Input('btn-save','n_clicks'),
    Input('filename','value'),
    prevent_initial_call=True
)
def save(btn, filname):
    if"btn-save" == ctx.triggered_id:
        saveName = filname
        predicted_dataframe = pd.read_pickle('./store/new.pkl')
        predicted_dataframe.to_csv("./store/"+saveName+".csv" , index=False)

        return html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Saved, The file name is "+saveName +".csv")
        ], width=12)
    ])
])