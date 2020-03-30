import sys
import logging
import datetime
import pandas as pd
from flask import Response, request, redirect, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_session import Session
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash.dependencies import Input, Output, State

from config import REDIS_CONFIG
from .redisclient import RedisClient


logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=" %I:%M:%S ",
    level="INFO",
)

logger = logging.getLogger(__name__)

COLORS = {"graph_bg": "#1E1E1E", "text": "#696969"}

sess = Session()
cache = Cache()
db = SQLAlchemy()
migrate = Migrate()

redis_client = RedisClient(
    host=REDIS_CONFIG["REDIS_HOST"],
    port=REDIS_CONFIG["REDIS_PORT"],
    db=2,
    password=REDIS_CONFIG["REDIS_PASSWORD"],
)


def create_app(config_name):
    from config import config
    from .model import WorkoutSession
    from .pose import PoseEngine
    from .camera import VideoStream
    from .stream import gen
    from .layout import layout_homepage, layout_login, layout

    app = dash.Dash(
        __name__,
        meta_tags=[
            {"name": "charset", "content": "UTF-8"},
            {
                "name": "viewport",
                "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
            },
            {"name": "author", "content": "James Wong"},
            {
                "name": "description",
                "content": "A HIIT Workout Trainer Dash App on Your Raspberry Pi",
            },
        ],
    )
    app.title = "HIIT PI"
    app.config.suppress_callback_exceptions = True

    server = app.server
    server.config.from_object(config[config_name])

    with server.app_context():
        db.init_app(server)
        db.create_all()
        migrate.init_app(server, db)

        sess.init_app(server)

        cache.init_app(server)
        cache.clear()

    model = PoseEngine(model_path=server.config["MODEL_PATH"])
    camera = VideoStream()
    camera.start(model=model)

    app.layout = layout()

    @app.callback(
        Output("videostream", "src"), [Input("workout-dropdown", "value")],
    )
    def update_dropdown_menu(workout):
        return f"/videostream/{workout}"

    @app.callback(
        Output("workout-dropdown", "value"),
        [Input("workout-stop-btn", "n_clicks")],
        [State("workout-dropdown", "value")],
    )
    def stop_workout(n_clicks, workout):
        if workout is not None:
            ws = WorkoutSession(
                user_name=session.get("user_name"),
                workout=workout,
                reps=redis_client.get("reps"),
                pace=redis_client.get("pace"),
            )
            db.session.add(ws)
            db.session.commit()
            logger.info(f"{ws} inserted into db")
        return None

    @app.callback(
        Output("leaderboard-graph", "figure"),
        [Input("update-leaderboard-btn", "n_clicks")],
        [State("workout-dropdown", "value")],
    )
    def update_leaderboard_graph(n_clicks, workout):
        if n_clicks > 0:
            current_time = datetime.datetime.utcnow()
            a_week_ago = current_time - datetime.timedelta(weeks=1)

            query = db.session.query(
                WorkoutSession.user_name,
                WorkoutSession.workout,
                db.func.sum(WorkoutSession.reps).label("reps"),
            ).filter(WorkoutSession.created_date >= a_week_ago)

            if workout is not None:
                query = query.filter_by(workout=workout)

            query = (
                query.group_by(WorkoutSession.user_name, WorkoutSession.workout)
                .order_by(db.func.sum(WorkoutSession.reps).desc())
                .all()
            )

            df = pd.DataFrame(query, columns=["user_name", "workout", "reps"])
            layout = {
                "barmode": "stack",
                "margin": {"l": 0, "r": 0, "b": 0, "t": 40},
                "autosize": True,
                "font": {"family": "Comfortaa", "color": COLORS["text"], "size": 10,},
                "plot_bgcolor": COLORS["graph_bg"],
                "paper_bgcolor": COLORS["graph_bg"],
                "xaxis": {
                    "ticks": "",
                    "showgrid": False,
                    "title": "",
                    "automargin": True,
                    "zeroline": False,
                },
                "yaxis": {
                    "showgrid": False,
                    "title": "",
                    "automargin": True,
                    "categoryorder": "total ascending",
                    "linewidth": 1,
                    "linecolor": "#282828",
                    "zeroline": False,
                },
                "title": {
                    "text": "Last 7 Days",
                    "y": 0.9,
                    "x": 0.5,
                    "xanchor": "center",
                    "yanchor": "top",
                },
                "showlegend": False,
            }
            fig = px.bar(
                df,
                x="reps",
                y="user_name",
                color="workout",
                orientation="h",
                color_discrete_sequence=px.colors.qualitative.Plotly,
            )
            fig.update_layout(layout)
            fig.update_traces(marker_line_width=0, width=0.5)
            return fig
        else:
            return {
                "data": [],
                "layout": {
                    "plot_bgcolor": COLORS["graph_bg"],
                    "paper_bgcolor": COLORS["graph_bg"],
                    "xaxis": {
                        "showgrid": False,
                        "showline": False,
                        "zeroline": False,
                        "showticklabels": False,
                    },
                    "yaxis": {
                        "showgrid": False,
                        "showline": False,
                        "zeroline": False,
                        "showticklabels": False,
                    },
                },
            }

    @server.route("/videostream/<workout>", methods=["GET"])
    def videiostream(workout):
        user_name = session.get("user_name")
        session["workout"] = workout
        logger.info(f"Current player: {user_name}")
        logger.info(f"Current workout: {workout}")
        return Response(
            gen(camera, workout), mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    @app.callback(
        [
            Output("live-update-graph", "extendData"),
            Output("indicator-reps", "children"),
            Output("indicator-pace", "children"),
        ],
        [Input("live-update-interval", "n_intervals")],
    )
    def update_graph(n_intervals):
        inference_time = redis_client.lpop("inference_time")
        pose_score = redis_client.lpop("pose_score")
        data = [{"y": [[inference_time], [pose_score]]}, [0, 1], 200]

        reps = redis_client.get("reps")
        pace = redis_client.get("pace")

        return data, f"{reps:.0f}", f"{pace*30:.1f}" if pace > 0 else "/"

    @server.route("/user_login", methods=["POST"])
    def user_login():
        user_name = request.form.get("user_name_form")
        session["user_name"] = user_name
        logger.info(f"User {user_name} logged in")
        redis_client.set("reps", 0)
        redis_client.set("pace", 0)
        return redirect("/home")

    @server.route("/user_logout")
    def user_logout():
        user_name = session.pop("user_name")
        if user_name is not None:
            session.clear()
        logger.info(f"User {user_name} logged out")
        return redirect("/login")

    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def display_page(pathname):
        if pathname == "/home":
            current_user = session.get("user_name")
            return layout_homepage(current_user)
        elif pathname == "/login":
            return layout_login()
        else:
            return layout_login()

    return app
