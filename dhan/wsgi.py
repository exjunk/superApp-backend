from flask_server import app,socketio,init_super_app,start_dhan_feed

def create_app():
    init_super_app()
    start_dhan_feed()
    return app

application = create_app()

if __name__ == "__main__":
    #main()
    socketio.run(application)
    #app.run()
