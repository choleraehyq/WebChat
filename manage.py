from flask.ext.script import Manager, Server
from application import app, socketio

manager = Manager(app)

@manager.command
def runserver():
    socketio.run(app)
# manager.add_command("runserver", 
#     Server(host="127.0.0.1", port=1234, use_debugger=True))

if __name__ == '__main__':
    manager.run()