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
    df1 = db.database('methane_data')
    df2 = db.database('ammonia_data')
    df3 = db.database('co2_data')
    df1['gas'] = 'methane'
    df2['gas'] = 'ammonia'
    df3['gas'] = 'co2'
    df = pd.concat([df1, df2, df3])
    df = df.sort_values(by="time")

    fig1= px.line(df, x="time", y="value", color="gas", markers=True)

    df = db.database('methane_data')
    fig2= px.line(df, x="time", y="value", markers=True)

    df = db.database('ammonia_data')
    fig3 = px.line(df, x="time", y="value", markers=True)

    df = db.database('co2_data')
    fig4 = px.line(df, x="time", y="value", markers=True)

    return html.Div(
    style={'padding': '25px 25px 25px 25px'},    
    children=[
    # All elements from the top of the page
        html.Div([
            html.H1(children='Cavetto Data Visualization'),

            html.Div(children='''
                Aggregated sensor data.
            '''),

            dcc.Graph(
                id='graph1',
                figure=fig1
            ),

            dcc.Interval(
                id='summary-graph-update',
                interval=GRAPH_INTERVAL,
            ),
        ]),

        html.Div([

            dcc.Graph(
                id='graph2',
                figure=fig2
            ), 

            dcc.Interval(
                id='methane-graph-update',
                interval=GRAPH_INTERVAL
            ),
        ]),

        html.Div([

            dcc.Graph(
                id='graph3',
                figure=fig3
            ), 

            dcc.Interval(
                id='ammonia-graph-update',
                interval=GRAPH_INTERVAL
            ),
        ]),

        html.Div([

            dcc.Graph(
                id='graph4',
                figure=fig4
            ), 

            dcc.Interval(
                id='co2-graph-update',
                interval=GRAPH_INTERVAL
            ),
        ]),
    ])

app.layout = serve_layout

@app.callback(Output('graph1', 'figure'), 
        Input('summary-graph-update', 'n_intervals'))
def update_summary_figure(interval):
    df1 = db.database('methane_data')
    df2 = db.database('ammonia_data')
    df3 = db.database('co2_data')
    df1['gas'] = 'methane'
    df2['gas'] = 'ammonia'
    df3['gas'] = 'co2'
    df = pd.concat([df1, df2, df3])
    df = df.sort_values(by="time")
    fig = px.line(df, x="time", y="value", color="gas", markers=True,
            title="Volatile gas readings over time")
    # print(f"updating {interval}")
    return fig

@app.callback(Output('graph2', 'figure'), 
        Input('methane-graph-update', 'n_intervals'))
def update_methane_figure(interval):
    df = db.database('methane_data')
    df = df.sort_values(by="time")
    fig = px.line(df, x="time", y="value", markers=True,
            title="Aggregate CH4 data vs. time")
    # print(f"updating {interval}")
    return fig

@app.callback(Output('graph3', 'figure'), 
        Input('ammonia-graph-update', 'n_intervals'))
def update_ammonia_figure(interval):
    df = db.database('ammonia_data')
    df = df.sort_values(by="time")
    fig = px.line(df, x="time", y="value", markers=True,
                title="Aggregate NH3 data vs. time")
    # Set color to red
    fig.data[0].line.color = 'rgb(239, 85, 59)'
    # print(f"updating {interval}")
    return fig

@app.callback(Output('graph4', 'figure'), 
        Input('co2-graph-update', 'n_intervals'))
def update_co2_figure(interval):
    df = db.database('co2_data')
    df = df.sort_values(by="time")
    fig = px.line(df, x="time", y="value", markers=True,
                title="Aggregate CO2 data vs. time")
    # Set color to green
    fig.data[0].line.color = 'rgb(0, 204, 150)'
    #fig.data[0].line.color = "#00ff00"
    # print(f"updating {interval}")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)