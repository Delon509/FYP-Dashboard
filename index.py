import dash_bootstrap_components as dbc
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
import pandas as pd
from app import app
import  random
# Connect to the layout and callbacks of each tab
from questionaire import questionaire_layout
from minigame import minigame_layout
from website import website_layout
from AI import AI_layout

server = app.server
# our app's Tabs *********************************************************
app_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Questionaire", tab_id="tab-questionaire", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                dbc.Tab(label="Mini-game", tab_id="tab-minigame", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                dbc.Tab(label="Website", tab_id="tab-website", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                dbc.Tab(label="AI", tab_id="tab-ai", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
            ],
            id="tabs",
            active_tab="tab-questionaire",
        ),
    ], className="mt-3"
)

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("ABC School Open Day Dashboard",
                            style={"textAlign": "center"}), width=12)),
    html.Hr(),
    dbc.Row(dbc.Col(app_tabs, width=12), className="mb-3"),
    html.Div(id='content', children=[])

])

@app.callback(
    Output("content", "children"),
    [Input("tabs", "active_tab")]
)
def switch_tab(tab_chosen):
    if tab_chosen == "tab-questionaire":
        return questionaire_layout
    elif tab_chosen == "tab-minigame":
        return minigame_layout
    elif tab_chosen == "tab-website":
        return website_layout
    elif tab_chosen == "tab-ai":
        return AI_layout
    return html.P("This shouldn't be displayed for now...")



if __name__=='__main__':
    app.run_server(debug=True)

