from app import createApp
from app.extensions import db


# start the app only from this file
if __name__ == "__main__" :
    app = createApp()
    with app.app_context() :
        db.create_all()
    app.logger.info("SERVER STARTED SUCCESSFULLY")    
    app.run(
        debug=True,
        host="0.0.0.0",
        port="8080"
    )