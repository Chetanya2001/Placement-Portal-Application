from flask import Flask  #imports the framework
from config import Config #import all the config
from extensions import db #import ORM object
from models import * #load all the database tables
from models.user import User
app = Flask(__name__) #it creates the backend server
app.config.from_object(Config) #load the configuration to the app
db.init_app(app) # connect flask to the ORM
with app.app_context(): #give flask access to app config database application state
    db.create_all()  # creates all the table in the database
    admin = User.query.filter_by(role="admin").first()

    if not admin:

        admin_user = User(
            name="Admin",
            email="admin@placement.com",
            password="admin@123",
            role="admin"
        )

        db.session.add(admin_user)

        db.session.commit()

        print("Admin Created!")
    print("Database Created 200")
if __name__ == "__main__":  #Run the flask server
    app.run(debug=True)      # start server debug true with debug error