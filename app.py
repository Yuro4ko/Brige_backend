from flask import Flask, json, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brige.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    import models
    import routes


@app.route('/')
def status():
    return 'OK', 200


if __name__ == '__main__':
    print("Binding...")
    app.run(debug=False, host='0.0.0.0')
