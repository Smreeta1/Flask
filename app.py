from flask import Flask 

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World! Welcome to home page!'

@app.route('/other route')
def hello():
    return 'this is other route!'


if __name__ == '__main__':
    app.run(debug=True)
