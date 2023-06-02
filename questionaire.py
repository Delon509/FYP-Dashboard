from dash import Dash, dash_table, dcc, html,ctx,no_update
from dash.dependencies import Input, Output
import pandas as pd
from app import  app
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import glob
import random
import plotly.express as px
get_colors = lambda n: ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(n)]
def getFiles():
    files = glob.glob(glob.escape("./store/") + "*.csv")
    for i in range(len(files)):
        files[i] = files[i].replace('./store\\', '', 1)
    return files
df = pd.read_csv('./store/origin.csv')
df["createdTime"]= pd.DatetimeIndex(df["createdTime"]).year
df.loc[((df["age"] >= 18) & (df["age"] <=24)),  'AgeGroup'] = '18-24'
df.loc[((df["age"] >= 25) & (df["age"] <=34)),  'AgeGroup'] = '25-34'
df.loc[((df["age"] >= 35) & (df["age"] <=50)),  'AgeGroup'] = '35-50'
df.loc[(df["age"] >50),  'AgeGroup'] = '>50'

questionaire_layout = html.Div([
    html.H4("Choose file",
            style={"textAlign": "center"}),
        dbc.Row([
        dbc.Col([
            dcc.Dropdown(getFiles(),'origin.csv' ,id='selectedFile'),
        ], width=12),
        dbc.Col([
            html.Button('Refresh', id='btn-refresh', n_clicks=0),
    ]),
        ]),

    html.H4("Choose year",
            style={"textAlign": "center"}),
    dcc.Dropdown(df["createdTime"].drop_duplicates().sort_values().append(pd.Series(["All"])), max(df["createdTime"].drop_duplicates()), id='yearFilter'),
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
    ),
    html.H1("Analysis on single question",
                            style={"textAlign": "center"}),
    html.H4("Question",
                            style={"textAlign": "center"}),
    dcc.Dropdown(df.columns.values.tolist(), "age", id='single_question'),
    html.H4("Graph Type",
                            style={"textAlign": "center"}),
    dcc.Dropdown(["box","pie"], "box", id='single_graph_type'),
    html.Div(id='single-container'),
    html.H1("Analysis on relationship",
                            style={"textAlign": "center"}),
    html.H4("Group By / X axis",
                            style={"textAlign": "center"}),
    dcc.Dropdown(df.columns.values.tolist(), "age", id='xAxis'),
    html.H4("Value / Y axis",
                            style={"textAlign": "center"}),
    dcc.Dropdown(df.columns.values.tolist(), "age", id='yAxis'),
    html.H4("Chart / Graph",
                            style={"textAlign": "center"}),
    dcc.Dropdown(["pie","histogram"], "histogram", id='graph_type'),
    html.Div(id='datatable-interactivity-container'),
])

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    Output('single-container','children'),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"),
    Input('xAxis', 'value'),
    Input('yAxis', 'value'),
    Input('yearFilter', 'value'),
    Input('graph_type', 'value'),
    Input('single_question','value'),
    Input('single_graph_type','value')
)
def update_graphs(rows, derived_virtual_selected_rows,xAxis,yAxis,year,graph_type,single_question,single_graph_type):
    yearList = []
    if year == "All":
        yearList = df["createdTime"].drop_duplicates().sort_values().tolist()
    else:
        yearList.append(year)
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]
    single_graph_list = []
    multi_graph_list = []
    if single_graph_type == "pie":

        for column in yearList:
            labels = dff.query("createdTime ==" + str(column))[single_question].unique()
            if dff.query("createdTime ==" + str(column))[single_question].isnull().values.any():
                single_graph_list.append(dcc.Graph(id=single_question + str(column),
                figure={
                    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No matching data found in year"+str(column),
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 28
                }
            }
        ]
    }
                }))
            else:
                values = []
                colors = get_colors(len(labels))
                temp_dict_single = dff.query("createdTime ==" + str(column))[single_question].value_counts()
                for label in labels:
                    if label in temp_dict_single:
                        values.append(temp_dict_single[label])
                    else:
                        values.append(0)
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, title=str(single_question) + str(column))])
                fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                                  marker=dict(colors=colors, line=dict(color='#000000', width=2)))
                temp = dcc.Graph(id=single_question + str(column), figure=fig)
                single_graph_list.append(temp)
    else:
        for column in yearList:
            temp = dcc.Graph(
                id=single_question + str(column),
                figure={
                    "data": [
                        {
                            "y": dff.query("createdTime ==" + str(column))[single_question],
                            "type": single_graph_type,
                            "marker": {"color": colors},
                        }
                    ],
                    "layout": {
                        "yaxis": {
                            "automargin": True,
                            "title": {"text": single_question + str(column)}
                        },
                        "height": 250,
                        "margin": {"t": 10, "l": 10, "r": 10},
                    },
                },
            )
            single_graph_list.append(temp)
    if graph_type== "pie":
        for column in yearList:
            labels = dff.query("createdTime ==" + str(column))[yAxis].unique()
            objects = []
            if dff.query("createdTime ==" + str(column))[xAxis].isnull().values.any()|dff.query("createdTime ==" + str(column))[yAxis].isnull().values.any():
                single_graph_list.append(dcc.Graph(id=single_question + str(column),
                                                   figure={
                                                       "layout": {
                                                           "xaxis": {
                                                               "visible": False
                                                           },
                                                           "yaxis": {
                                                               "visible": False
                                                           },
                                                           "annotations": [
                                                               {
                                                                   "text": "No matching data found in year" + str(
                                                                       column),
                                                                   "xref": "paper",
                                                                   "yref": "paper",
                                                                   "showarrow": False,
                                                                   "font": {
                                                                       "size": 28
                                                                   }
                                                               }
                                                           ]
                                                       }
                                                   }))
            else:
                objects = dff.query("createdTime ==" + str(column))[xAxis].unique()
                for eachObject in objects:
                    values = []

                    temp_dict = dff.query("createdTime ==" + str(column)).query(str(xAxis) +'== "%s"' %eachObject)[yAxis].value_counts()
                    for label in labels:
                        if label in temp_dict:
                            values.append(temp_dict[label])
                        else:
                            values.append(0)


                    fig = go.Figure(
                        data=[go.Pie(labels=labels, values=values, title=str(xAxis)+" "+ str(eachObject) +" year " +str(column))])
                    temp = dcc.Graph(id=single_question + str(column), figure=fig)
                    multi_graph_list.append(temp)

    else:
        for column in yearList:
            if (dff.query("createdTime ==" + str(column))[xAxis].isnull().values.any() | dff.query("createdTime ==" + str(column))[yAxis].isnull().values.any()):
                multi_graph_list.append(dcc.Graph(id=single_question + str(column),
                                                   figure={
                                                       "layout": {
                                                           "xaxis": {
                                                               "visible": False
                                                           },
                                                           "yaxis": {
                                                               "visible": False
                                                           },
                                                           "annotations": [
                                                               {
                                                                   "text": "No matching data found in year" + str(
                                                                       column),
                                                                   "xref": "paper",
                                                                   "yref": "paper",
                                                                   "showarrow": False,
                                                                   "font": {
                                                                       "size": 28
                                                                   }
                                                               }
                                                           ]
                                                       }
                                                   }))
            else:
                fig = px.histogram(dff.query("createdTime ==" + str(column)), x=yAxis, color=xAxis, text_auto=True, marginal="box",
                                   hover_data=dff.columns,title=str(yAxis)+" Group By "+str(xAxis) +" In year "+str(column))
                multi_graph_list.append(dcc.Graph(
                    id=yAxis,
                    figure=fig
                ))

    return multi_graph_list,single_graph_list
@app.callback(
    Output('datatable-interactivity', 'data'),
    Input('yearFilter', 'value'),
    Input('selectedFile', 'value'),
)
def display_table(year,file):
    df = pd.read_csv('./store/'+file)
    df["createdTime"] = pd.DatetimeIndex(df["createdTime"]).year
    df.loc[((df["age"] >= 18) & (df["age"] <= 24)), 'AgeGroup'] = '18-24'
    df.loc[((df["age"] >= 25) & (df["age"] <= 34)), 'AgeGroup'] = '25-34'
    df.loc[((df["age"] >= 35) & (df["age"] <= 50)), 'AgeGroup'] = '35-50'
    df.loc[(df["age"] > 50), 'AgeGroup'] = '>50'
    if year == "All":
        result = df
    else:
        result = df[df["createdTime"] == year]
    return result.to_dict("records")
@app.callback(
    Output('selectedFile','options'),
    Input('btn-refresh','n_clicks')
)
def refreshFunction(btn):
    if "btn-refresh" == ctx.triggered_id:
        return getFiles()
    else:
        return no_update

@app.callback(Output('btn-refresh', 'style'), [Input('btn-refresh', 'n_clicks')])
def change_button_style(n_clicks):

    if n_clicks > 0:
        return {'background-color': 'red',
                    'color': 'white'}

    else:

        return dict()

