from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import db

app = Dash(__name__)

df, cx = db.database()
print(cx)
cx.close()

fig = px.scatter(df, x="time", y="value")

app.layout = html.Div(children=[
    html.H1(children='Cavetto Data Visualization'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == "__main__":
    df, cx = db.database()
    app.run_server(debug=True)
    cx.close()