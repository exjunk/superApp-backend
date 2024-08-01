from flask_server import app,socketio,main

def create_app():
    main()
    return app

application = create_app()

if __name__ == "__main__":
    socketio.run(application)
    #app.run()
