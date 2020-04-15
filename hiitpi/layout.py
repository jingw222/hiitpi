import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html

from .workout import WORKOUTS


COLORS = {"graph_bg": "#1E1E1E", "text": "#696969"}


def layout_config_panel(current_user):
    """The Dash app layout for the user config panel"""

    title = html.Div([html.H5(f"Welcome, {current_user}!")], className="app__header")
    dropdown_options = [{"label": "Random", "value": "random"}] + [
        {"label": v.name, "value": k} for k, v in WORKOUTS.items()
    ]
    dropdown_menu = html.Div(
        [
            html.Div(
                [
                    dcc.Dropdown(
                        id="workout-dropdown",
                        options=dropdown_options,
                        placeholder="Select a workout",
                        searchable=True,
                        clearable=False,
                    )
                ],
                className="six columns flex-display",
            ),
            html.Div(
                [
                    html.Button(
                        id="workout-stop-btn",
                        n_clicks=0,
                        children="Done!",
                        className="button",
                    ),
                    html.A(
                        id="user-logout-btn",
                        n_clicks=0,
                        children="Exit?",
                        className="button",
                        href="/user_logout",
                    ),
                ],
                className="six columns flex-display",
            ),
        ],
        className="row app__dropdown flex-display",
    )

    lines_graph = html.Div(
        [
            dcc.Graph(
                id="live-update-graph",
                figure={
                    "data": [
                        {
                            "name": "Inference Time",
                            "type": "scatter",
                            "y": [],
                            "mode": "lines",
                            "line": {"color": "#e6af19"},
                        },
                        {
                            "name": "Pose Score",
                            "type": "scatter",
                            "y": [],
                            "yaxis": "y2",
                            "mode": "lines",
                            "line": {"color": "#6145bf"},
                        },
                    ],
                    "layout": {
                        "margin": {"l": 60, "r": 60, "b": 10, "t": 20},
                        "height": 180,
                        "autosize": True,
                        "font": {
                            "family": "Comfortaa",
                            "color": COLORS["text"],
                            "size": 10,
                        },
                        "plot_bgcolor": COLORS["graph_bg"],
                        "paper_bgcolor": COLORS["graph_bg"],
                        "xaxis": {
                            "ticks": "",
                            "showticklabels": False,
                            "showgrid": False,
                        },
                        "yaxis": {
                            # "autorange": True,
                            "range": [18, 30],
                            "title": "Inference Time (ms)",
                        },
                        "yaxis2": {
                            # "autorange": True,
                            "range": [0, 1],
                            "title": "Pose Score",
                            "overlaying": "y",
                            "side": "right",
                        },
                        "legend": {
                            "x": 0.5,
                            "y": -0.2,
                            "xanchor": "center",
                            "yanchor": "middle",
                            "orientation": "h",
                        },
                    },
                },
                config={
                    "displayModeBar": False,
                    "responsive": True,
                    "scrollZoom": True,
                },
            ),
        ],
    )

    workout_name = html.Div([html.P(id="workout_name")], className="app__header",)

    def indicator(id_value, text):
        return html.Div(
            [
                html.P(id=id_value, className="indicator_value"),
                html.P(text, className="twelve columns indicator_text"),
            ],
            className="six columns indicator pretty_container",
        )

    indicators = html.Div(
        [
            indicator("indicator-reps", "REPS"),
            indicator("indicator-pace", "PACE (/30s)"),
        ],
        className="row indicators flex-display",
    )

    live_update_graph = html.Div(
        [
            lines_graph,
            dcc.Interval(id="live-update-interval", interval=50, n_intervals=0),
        ]
    )

    bars_graph = html.Div(
        [
            html.Button(
                id="update-leaderboard-btn",
                n_clicks=0,
                children="Leaderboard",
                className="button",
            ),
            dcc.Graph(
                id="leaderboard-graph",
                config={
                    "displayModeBar": False,
                    "responsive": True,
                    "scrollZoom": True,
                },
            ),
        ]
    )

    return html.Div(
        [title, live_update_graph, dropdown_menu, workout_name, indicators, bars_graph],
        className="four columns app__config_panel",
    )


def layout_videostream():
    """The Dash app layout for the video stream"""
    videostream = html.Img(id="videostream")
    return html.Div([videostream], className="eight columns app__video_image")


def layout_homepage(current_user):
    """The Dash app home page layout"""
    return html.Div(
        [layout_videostream(), layout_config_panel(current_user)],
        className="row app__container",
    )


def layout_login():
    """The Dash app login oage layout"""
    header = html.Div(
        [
            html.H2("HIIT PI"),
            dcc.Markdown(
                id="welcome-intro-md",
                children="""
            A workout trainer [Dash](https://dash.plot.ly/) app 
            that helps track your [HIIT](https://en.wikipedia.org/wiki/High-intensity_interval_training) workouts 
            by analyzing real-time video streaming from your sweet [Pi](https://www.raspberrypi.org/).  
            """,
            ),
            dcc.Markdown(
                id="welcome-intro-sub-md",
                children="Powered by [TensorFlow Lite](https://www.tensorflow.org/lite) and [Edge TPU](https://cloud.google.com/edge-tpu) with ❤️.",
            ),
        ],
        className="app__header",
    )

    login_form = html.Div(
        [
            html.Form(
                [
                    dcc.Input(
                        id="user_name_input",
                        name="user_name_form",
                        type="text",
                        placeholder="PLAYER NAME",
                        maxLength=20,
                        minLength=1,
                        required=True,
                    ),
                    html.Button(
                        id="user-login-btn",
                        children="ENTER",
                        type="submit",
                        n_clicks=0,
                        className="button",
                    ),
                ],
                action="/user_login",
                method="POST",
                autoComplete="off",
                className="form-inline",
                title="Enter your player name.",
            )
        ],
        className="flex-display",
        style={"margin-top": "4rem"},
    )

    welcome_jumbotron = html.Div([header, login_form], className="header_container")
    return html.Div(
        [welcome_jumbotron],
        className="welcome_login_form page-background-image flex-display",
    )


def layout():
    return html.Div(
        [dcc.Location(id="url", refresh=True), html.Div(id="page-content"),]
    )
