import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_core_components as dcc
import dash
import pandas as pd
from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
from app import app
import plotly.graph_objects as go
import plotly.express as px
import  random
import mysql.connector
from decouple import config

get_colors = lambda n: ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(n)]
mydb = mysql.connector.connect(
        host=config('host'),
        user=config('user'),
        password=config('password'),
        database=config('database'),
        port=config('port')
    )
query = config('queryInMinigame')
df = pd.read_sql(query, mydb)
df.loc[df['url'].str.contains(pat="snakegame") , 'game'] = "Snake"
df.loc[df['url'].str.contains(pat="snakegame") , 'theme'] = "Science"
df.loc[df['url'].str.contains(pat="wordcrush") , 'game'] = "Crush"
df.loc[df['url'].str.contains(pat="wordcrush") , 'theme'] = "Chinese Culture"
queryForTreasure = config('queryTreasureInMinigame')
dfForTreasure = pd.read_sql(queryForTreasure, mydb)
dfForTreasure['game'] = "Treasure Hunt"
dfForTreasure['theme'] = "School"
mydb.close()
df = pd.concat([df,dfForTreasure])
df.loc[df['user_id'] < 0, 'role'] = "Anonymous"
df.loc[df['user_id'] >= 0, 'role'] = "User"
df.loc[( (df["time_in_second"] <= 60)), 'stayTimeGroup'] = 'Short'
df.loc[((df["time_in_second"] >= 61) & (df["time_in_second"] <= 120)), 'stayTimeGroup'] = 'Normal'
df.loc[( (df["time_in_second"] > 120)), 'stayTimeGroup'] = 'Long'
df.loc[((df["role"] == "Anonymous"), 'sex')] = "Unknown"
df["sex"].fillna("No Provided", inplace = True)
df.drop(['url'], axis=1, inplace=True)
df['date'] = pd.to_datetime(df['update_time'])
minigame_layout = html.Div([
    html.H3("Choose Date Range",
                            style={"textAlign": "center"}),
    dcc.DatePickerRange(
            id="game_date_filter",
            start_date=df["date"].min(),
            end_date=df["date"].max(),
            min_date_allowed=df["date"].min(),
            max_date_allowed=df["date"].max(),
        ),
    dmc.Group(
        spacing=50,
        children=[
            dmc.TimeInput(id="time_start",label="Start Time" , value=df["date"].min()),
            dmc.TimeInput(id="time_end",
                label="End Time", value=df["date"].max()
            ),

        ],
    ),
    # graph type
    html.H4("Graph Type",
                            style={"textAlign": "center"}),
    dcc.Dropdown(["pie","histogram"], "histogram", id='game_graph_type'),
    # function
    html.Div([
    html.H4("Function",
                            style={"textAlign": "center"}),
    dcc.Dropdown(["count","sum","avg",'min','max'], "count", id='game_histogram_function'),
    html.H4("Categorical-axes",
                            style={"textAlign": "center"}),
    dcc.Dropdown(["role","sex",'game','theme','stayTimeGroup'], "role", id='game_categorical-axes'),
    html.H4("Marginal",
                            style={"textAlign": "center"}),
    dcc.Dropdown(["rug","box",'violin'], "rug", id='game_marginal'),
    ], style = dict(),id='game_histogramDiv'),
    html.Div([
    html.H4("Value",
                            style={"textAlign": "center"}),
    dcc.Dropdown(["role","sex","game",'stayTimeGroup','theme'], "role", id='game_pie_column')
    ], style = dict(display='none'),id='game_pieDiv'),


    dash_table.DataTable(
        id='game_datatable-interactivity',
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
        page_current=0,
        page_size=10,
    ),
    html.Div(id='game_datatable-interactivity-container'),
])


@app.callback(
    Output('game_datatable-interactivity', 'style_data_conditional'),
    Input('game_datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@app.callback(
    Output('game_datatable-interactivity-container', "children"),
    Output('game_histogramDiv', 'style'),
    Output('game_pieDiv', 'style'),
    Input('game_datatable-interactivity', "derived_virtual_data"),
    Input('game_datatable-interactivity', "derived_virtual_selected_rows"),
    Input("game_graph_type",'value'),
    Input("game_histogram_function",'value'),
    Input("game_categorical-axes",'value'),
    Input("game_marginal",'value'),
    Input("game_pie_column",'value')
)
def update_graphs(rows, derived_virtual_selected_rows,game_graph_type,histogram_function,axes,margin,pie_column,):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]
    if game_graph_type == "histogram":
        fig = px.histogram(dff, x="date", color=axes, text_auto=True, marginal=margin, hover_data=dff.columns)
        if histogram_function!= "count":
            fig = px.histogram(dff, x="date", color=axes, text_auto=True, marginal=margin, hover_data=dff.columns , histfunc= histogram_function,
                               y="time_in_second")
        return dcc.Graph(
            id="test",
            figure=fig
        ),dict(),dict(display='none')
    #"role","gender","game",'stayTimeGroup'
    elif game_graph_type == "pie":

        labels = dff[pie_column].unique()
        values = []
        temp_dict_single = dff[pie_column].value_counts()
        for label in labels:
            if label in temp_dict_single:
                values.append(temp_dict_single[label])
            else:
                values.append(0)
        colors = get_colors(len(labels))
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, title=str(pie_column) +" from "+ str(dff["date"].min()) +" to "+str(dff["date"].max()))])
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                          marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        return dcc.Graph(id=str(pie_column), figure=fig),dict(display='none'),dict()

@app.callback(
    Output('game_datatable-interactivity', 'data'),
    Input('game_date_filter', 'start_date'),
    Input('game_date_filter', 'end_date'),
    Input('time_start','value'),
    Input('time_end','value')
)
def display_table(start_date,end_date,start_time,end_time):
    #df = pd.read_csv('./csv/game.csv')
    mydb = mysql.connector.connect(
        host=config('host'),
        user=config('user'),
        password=config('password'),
        database=config('database'),
        port=config('port')
    )
    query = config('queryInMinigame')
    df = pd.read_sql(query, mydb)
    df.loc[df['url'].str.contains(pat="snakegame"), 'game'] = "Snake"
    df.loc[df['url'].str.contains(pat="snakegame"), 'theme'] = "Science"
    df.loc[df['url'].str.contains(pat="wordcrush"), 'game'] = "Crush"
    df.loc[df['url'].str.contains(pat="wordcrush"), 'theme'] = "Chinese Culture"
    queryForTreasure = config('queryTreasureInMinigame')
    dfForTreasure = pd.read_sql(queryForTreasure, mydb)
    dfForTreasure['game'] = "Treasure Hunt"
    dfForTreasure['theme'] = "School"
    mydb.close()
    df = pd.concat([df, dfForTreasure])
    df.loc[df['user_id'] < 0, 'role'] = "Anonymous"
    df.loc[df['user_id'] >= 0, 'role'] = "User"
    df.loc[((df["time_in_second"] <= 60)), 'stayTimeGroup'] = 'Short'
    df.loc[((df["time_in_second"] >= 61) & (df["time_in_second"] <= 120)), 'stayTimeGroup'] = 'Normal'
    df.loc[((df["time_in_second"] > 120)), 'stayTimeGroup'] = 'Long'
    df.loc[((df["role"] == "Anonymous"), 'sex')] = "Unknown"
    df["sex"].fillna("No Provided", inplace=True)
    df.drop(['url'], axis=1, inplace=True)
    df['date'] = pd.to_datetime(df['update_time'])
    if not start_date or not end_date:
        raise dash.exceptions.PreventUpdate
    print("start_date is")
    print(str(start_date))
    print("start_date type is")
    print(type(start_date))
    print("start_time  is")
    print(str(start_time))
    print("start_time type is")
    print(type(start_time))
    start = start_date.split("T")[0] +"T" + start_time.split("T")[1]
    end = end_date.split("T")[0] +"T" + end_time.split("T")[1]
    print("start is ")
    print(str(start))
    print("end is ")
    print(str(end))
    df = df.loc[df["date"].between(pd.to_datetime(start), pd.to_datetime(end))]
    return df.to_dict("records")



if __name__=='__main__':
    print("Hello Game")