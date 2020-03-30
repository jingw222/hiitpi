import os
from hiitpi import create_app


app = create_app(os.getenv("FLASK_CONFIG") or "default")
server = app.server

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050, use_reloader=False)
