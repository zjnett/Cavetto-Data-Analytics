import os
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import cv2
import pandas as pd
import db
import stats
import ast

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 10000)

static_image_path = "assets/"

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

LABELS = {"value": "Value (ppm)",
          "time": "Date and time collected (UTC, hh:mm)"}
METHANE_LABELS = {"value": "Methane (ppm)",
                  "time": "Date and time collected (UTC, hh:mm)"}
AMMONIA_LABELS = {"value": "Ammonia (ppm)",
                  "time": "Date and time collected (UTC, hh:mm)"}
CO2_LABELS = {"value": "CO2 (ppm)",
              "time": "Date and time collected (UTC, hh:mm)"}


def serve_layout():
    df1 = db.database('methane_data')
    df2 = db.database('ammonia_data')
    df3 = db.database('co2_data')
    df1['gas'] = 'methane'
    df2['gas'] = 'ammonia'
    df3['gas'] = 'co2'
    df = pd.concat([df1, df2, df3])
    df = df.sort_values(by="time")

    fig1 = px.line(df, x="time", y="value", color="gas",
                   markers=True, labels=LABELS)

    df_methane = db.database('methane_data')
    fig2 = px.line(df_methane, x="time", y="value",
                   markers=True, labels=METHANE_LABELS)

    df_ammonia = db.database('ammonia_data')
    fig3 = px.line(df_ammonia, x="time", y="value",
                   markers=True, labels=AMMONIA_LABELS)

    df_carbon_dioxide = db.database('co2_data')
    fig4 = px.line(df_carbon_dioxide, x="time", y="value",
                   markers=True, labels=CO2_LABELS)

    # Download images if they do not exist
    max_temp, min_temp = db.save_last_thermal_image()
    rgb_time = db.save_last_rgb_image()

    # Import thermal image as numpy array
    thermal_image = cv2.imread(
        static_image_path + "thermal_image.jpg", 0)  # grayscale
    # Reduce temperatures by factor of TLinear (0.01 for Lepton)
    thermal_image = np.interp(thermal_image, [0, 255], [
                              (min_temp*0.01), (max_temp*0.01)])
    # Convert image from Kelvin to Celsius
    thermal_image = thermal_image - 273.15
    # Convert image from Kelvin to Fahrenheit
    # thermal_image = (thermal_image * 9/5) - 459.67
    # Flip image vertically
    thermal_image = np.flip(thermal_image, 0)

    hovertext = list()
    for i in range(thermal_image.shape[0]):
        hovertext.append(list())
        for j in range(thermal_image.shape[1]):
            hovertext[-1].append('y: {}<br />x: {}<br />temp: {}°C'.format(i,
                                 j, thermal_image[i][j]))

    # Import RGB image as numpy array
    rgb_image = cv2.imread(static_image_path + "rgb_image.jpg")
    # Set colorspace of numpy array to sRGB
    rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)

    fig5 = go.Figure(data=go.Heatmap(
        z=thermal_image, colorbar={"title": 'Temperature (°C)'}, hoverinfo='text', hovertext=hovertext))
    # fig5.update_layout(coloraxis_showscale=True)
    fig6 = go.Figure(go.Image(z=rgb_image))

    # Read boxes as str from database
    box_time, boxes = db.read_boxes()
    boxes_l = None
    if boxes:
        boxes_l = ast.literal_eval(boxes)

    # Check if time is the same for rgb and boxes
    # If so, draw boxes onto fig6
    if rgb_time == box_time:
        for box in boxes_l:
            fig6.add_shape(
                type="rect",
                x0=round(box[0]),
                y0=round(box[1]),
                x1=round(box[0]+box[2]),
                y1=round(box[1]+box[3]),
                line=dict(
                    color="red",
                    width=2
                )
            )

    """
    # Create graph figure for thermal image
    fig5 = go.Figure()
    # Add images
    fig5.add_layout_image(
        dict(
            source="assets/thermal_image.jpg",
            xref="x",
            yref="y",
            x=-1,
            y=-1,
            sizex=1,
            sizey=1,
            sizing="fill",
            opacity=1.0,
            layer="below")
)

    # Create graph figure for RGB image
    fig6 = go.Figure()
    fig6.add_layout_image(
        dict(
            source="assets/rgb_image.jpg",
                        xref="x",
            yref="y",
            x=-1,
            y=-1,
            sizex=1,
            sizey=1,
            sizing="fill",
            opacity=1.0,
            layer="below")
    )
    """

    # df_methane_24hr = stats.compile_24hr_dataframe(df_methane)
    # df_methane_stats = stats.compute_statistics(df_methane_24hr)

    # df_ammonia_24hr = stats.compile_24hr_dataframe(df_ammonia)
    # df_ammonia_stats = stats.compute_statistics(df_ammonia_24hr)

    # df_co2_24hr = stats.compile_24hr_dataframe(df_carbon_dioxide)
    # df_co2_stats = stats.compute_statistics(df_co2_24hr)

    github = dbc.Button(
        "View code on GitHub",
        href="https://github.com/zjnett/Cavetto-Data-Analytics/"
    )

    header = dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        # Logo image
                        dbc.Col(
                            html.Img(
                                src="assets/cavetto-logo.png",
                                # size="auto",
                                style={"height": "100px"}
                            ),
                            md="auto",
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H3("Cavetto Data Analytics"),
                                    html.P(
                                        "A data dashboard for the IoT Calf Health Sensor project."),
                                ],
                                id="app-title",
                            ),
                            md="auto",
                        ),
                    ],
                    align="center",
                ),

                dbc.Row(
                    github
                )
            ],
        ),
    )

    return dbc.Container(
        children=[
            header,
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Row(dbc.Card(
                                        [
                                            html.H4("Aggregate Gas Readings",
                                                    className="card-title"),
                                            html.P(
                                                "This pane contains the volatile gas readings collected from sensor nodes."
                                            ),

                                            html.H5(
                                                "Summary", className="card-subtitle"),
                                            html.Div([

                                                dcc.Graph(
                                                    id='graph1',
                                                    figure=fig1
                                                ),

                                                dcc.Interval(
                                                    id='summary-graph-update',
                                                    interval=GRAPH_INTERVAL,
                                                ),
                                            ]),

                                            html.H5(
                                                "Methane", className="card-subtitle"),
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

                                            html.H5(
                                                "Ammonia", className="card-subtitle"),
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

                                            html.H5("Carbon Dioxide",
                                                    className="card-subtitle"),
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
                                        ]
                                    ))
                                ],
                                width=7,
                                style={"margin-right": "10px"}
                            ),
                            dbc.Col(
                                [
                                    dbc.Row(dbc.Card(
                                        [
                                            html.H4("Statistics",
                                                    className="card-title"),
                                            html.P(
                                                "This pane contains relevant statistics for each gas within the last 24 hours."),
                                            dbc.Row(
                                                [
                                                    html.H5("Methane",
                                                            className="card-subtitle"),
                                                    html.Div("Loading...",
                                                             id="methane-stats"),
                                                    dcc.Interval(
                                                        id='methane-stats-update',
                                                        interval=GRAPH_INTERVAL
                                                    ),
                                                ],
                                                id="methane-stats-row",
                                            ),
                                            dbc.Row(
                                                [
                                                    html.H5("Ammonia",
                                                            className="card-subtitle"),
                                                    html.Div("Loading...",
                                                             id="ammonia-stats"),
                                                    dcc.Interval(
                                                        id='ammonia-stats-update',
                                                        interval=GRAPH_INTERVAL
                                                    ),
                                                ],
                                                id="ammonia-stats-row",
                                            ),
                                            dbc.Row(
                                                [
                                                    html.Div(children=[
                                                        html.H5("Carbon Dioxide",
                                                                className="card-subtitle"),
                                                        html.Div("Loading...",
                                                                 id="co2-stats"),
                                                        dcc.Interval(
                                                            id='co2-stats-update',
                                                            interval=GRAPH_INTERVAL
                                                        ), ])
                                                ],
                                                id="co2-stats-row",
                                            ),
                                        ]
                                    ))
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            html.H4("Thermal Images",
                                                    className="card-title"),
                                            html.P(
                                                "The most recent thermal image collected from the camera node."
                                            ),
                                            html.Div(children=[
                                                dcc.Graph(
                                                    id='graph5',
                                                    figure=fig5
                                                ),
                                                dcc.Interval(
                                                    id='thermal-image-update',
                                                    interval=GRAPH_INTERVAL
                                                ),
                                            ])
                                        ]
                                    )
                                ],
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            html.H4("RGB Images",
                                                    className="card-title"),
                                            html.P(
                                                "The most recent RGB image collected from the camera node."
                                            ),
                                            html.Div(children=[
                                                dcc.Graph(
                                                    id='graph6',
                                                    figure=fig6
                                                ),
                                                dcc.Interval(
                                                    id='rgb-image-update',
                                                    interval=GRAPH_INTERVAL
                                                ),
                                            ])
                                        ]
                                    )
                                ],
                            )
                        ],
                        style={"margin-top": "15px"}
                    )
                ],
                style={"margin-top": "25px"}
            ),
            html.Div(id='hidden-div1', style={'display': 'none'}),
            html.Div(id='hidden-div2', style={'display': 'none'})
        ],
        className="p-5",
        fluid=True,
    )


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
                  title="Volatile gas readings over time",
                  labels=LABELS)
    # print(f"updating {interval}")
    return fig


@app.callback(Output('graph2', 'figure'),
              Input('methane-graph-update', 'n_intervals'))
def update_methane_figure(interval):
    df = db.database('methane_data')
    df = df.sort_values(by="time")
    fig = px.line(df, x="time", y="value", markers=True,
                  title="Aggregate CH4 data vs. time",
                  labels=METHANE_LABELS)
    # print(f"updating {interval}")
    return fig


@app.callback(Output('graph3', 'figure'),
              Input('ammonia-graph-update', 'n_intervals'))
def update_ammonia_figure(interval):
    df = db.database('ammonia_data')
    df = df.sort_values(by="time")
    fig = px.line(df, x="time", y="value", markers=True,
                  title="Aggregate NH3 data vs. time",
                  labels=AMMONIA_LABELS)
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
                  title="Aggregate CO2 data vs. time",
                  labels=CO2_LABELS)
    # Set color to green
    fig.data[0].line.color = 'rgb(0, 204, 150)'
    # fig.data[0].line.color = "#00ff00"
    # print(f"updating {interval}")
    return fig


@app.callback(Output('methane-stats', 'children'),
              Input('methane-stats-update', 'n_intervals'))
def update_methane_stats(interval):
    df = db.database('methane_data')
    df = df.sort_values(by="time")
    df_24hr = stats.compile_24hr_dataframe(df)
    df_stats = stats.compute_statistics(df_24hr)
    update = html.Div(
        [
            dcc.Markdown(
                "**# of Datapoints:** {}\n".format(df_stats['count'])
                + "**Mean:** {} ppm\n".format(df_stats['mean'])
                + "**Std. Dev.:** {} ppm\n".format(df_stats['std'])
                + "**Min:** {} ppm\n".format(df_stats['min'])
                + "**Q1:** {} ppm\n".format(df_stats['25%'])
                + "**Q2/Median:** {} ppm\n".format(df_stats['50%'])
                + "**Q3:** {} ppm\n".format(df_stats['75%'])
                + "**Max:** {} ppm\n".format(df_stats['max']),
                style={"white-space": "pre"}
            )
        ]
    )
    return update


@app.callback(Output('ammonia-stats', 'children'),
              Input('ammonia-stats-update', 'n_intervals'))
def update_ammonia_stats(interval):
    df = db.database('ammonia_data')
    df = df.sort_values(by="time")
    df_24hr = stats.compile_24hr_dataframe(df)
    df_stats = stats.compute_statistics(df_24hr)
    update = html.Div(
        [
            dcc.Markdown(
                "**# of Datapoints:** {}\n".format(df_stats['count'])
                + "**Mean:** {} ppm\n".format(df_stats['mean'])
                + "**Std. Dev.:** {} ppm\n".format(df_stats['std'])
                + "**Min:** {} ppm\n".format(df_stats['min'])
                + "**Q1:** {} ppm\n".format(df_stats['25%'])
                + "**Q2/Median:** {} ppm\n".format(df_stats['50%'])
                + "**Q3:** {} ppm\n".format(df_stats['75%'])
                + "**Max:** {} ppm\n".format(df_stats['max']),
                style={"white-space": "pre"}
            )
        ]
    )
    return update


@app.callback(Output('co2-stats', 'children'),
              Input('co2-stats-update', 'n_intervals'))
def update_co2_stats(interval):
    df = db.database('co2_data')
    df = df.sort_values(by="time")
    df_24hr = stats.compile_24hr_dataframe(df)
    df_stats = stats.compute_statistics(df_24hr)
    update = html.Div(
        [
            dcc.Markdown(
                "**# of Datapoints:** {}\n".format(df_stats['count'])
                + "**Mean:** {} ppm\n".format(df_stats['mean'])
                + "**Std. Dev.:** {} ppm\n".format(df_stats['std'])
                + "**Min:** {} ppm\n".format(df_stats['min'])
                + "**Q1:** {} ppm\n".format(df_stats['25%'])
                + "**Q2/Median:** {} ppm\n".format(df_stats['50%'])
                + "**Q3:** {} ppm\n".format(df_stats['75%'])
                + "**Max:** {} ppm\n".format(df_stats['max']),
                style={"white-space": "pre"}
            )
        ]
    )
    # update = html.P("{}".format(df_stats))
    return update


"""
@app.callback(Output('hidden-div1', 'children'),
              Input('thermal-image-update', 'n_intervals'))
def update_thermal_image(interval):
    db.save_last_thermal_image()
    return None


@app.callback(Output('hidden-div2', 'children'),
              Input('rgb-image-update', 'n_intervals'))
def update_rgb_image(interval):
    db.save_last_rgb_image()
    return None
"""

if __name__ == "__main__":
    app.run_server(debug=True)
