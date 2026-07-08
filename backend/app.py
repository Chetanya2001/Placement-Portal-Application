# app.py
#
# CHANGE FROM YOUR ORIGINAL FILE:
# Your original app.py built the Flask `app` at import time as a bare module-level
# object. That's fine for Flask alone, but Celery workers ALSO need `app.config`
# (for the Redis URL, mail settings, etc.) and need to push an app_context()
# before every task runs (so db.session / models work inside a task).
#
# Wrapping the setup in create_app() lets both `flask run` and the Celery
# worker entrypoint (celery_worker.py) build the exact same configured app
# without duplicating code or triggering circular imports.
#
# Everything else (blueprints, db.create_all, admin bootstrap) is unchanged
# from what you had - just moved inside the function.

from flask import Flask
from config import Config
from flask_cors import CORS
from extensions import db, jwt
from models import *
from models.user import User
from routes import all_blueprints
from celery_app import celery

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin_user = User(
                name="Admin",
                email="admin@placement.com",
                password="admin@123",
                role="admin",
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin Created!")
        print("Database Created 200")

    # --- Wire Celery to this Flask app's config (Redis URL, mail creds, etc.) ---
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Every task runs inside a Flask app_context so db/models work normally."""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return app


# Keep module-level `app` so `flask run` / `python app.py` still works exactly
# as before.
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)