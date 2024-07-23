from flask_server import app,socketio,main

if __name__ == "__main__":
    main()
    socketio.run(app)
    #app.run()
