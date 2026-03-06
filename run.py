from app import createApp


# start the app only from this file
if __name__ == "__main__" :
    app = createApp()
    
    app.run(
        debug=True,
        host="0.0.0.0",
        port="8080"
    )