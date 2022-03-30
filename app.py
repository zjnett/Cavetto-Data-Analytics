import os
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import db

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

app = Dash(__name__)

# Pre-generate a bunch of dates
# This is temporary (for testing)
g_date = db.generate_random_dates(1000)

def serve_layout():
    df = db.database(g_date)
    fig = px.scatter(df, x="time", y="value")
    return html.Div(children=[
    html.H1(children='Cavetto Data Visualization'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='graph',
        figure=fig
    ),

    dcc.Interval(
        id='graph-update',
        interval=GRAPH_INTERVAL),
    ])

app.layout = serve_layout

@app.callback(Output('graph', 'figure'), 
        Input('graph-update', 'n_intervals'))
def update_figure(interval):
    df = db.database(g_date)
    fig = px.scatter(df, x="time", y="value")
    # print(f"updating {interval}")
    return fig

if __name__ == "__main__":
    df, cx = db.database(g_date)
    app.run_server(debug=True)
    cx.close()