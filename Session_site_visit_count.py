from flask import Flask, session

app = Flask(__name__)
app.secret_key = 'secret_key' 

@app.route('/')
def home():
    if 'counter' in session:
        session['counter'] += 1
    else:
        session['counter'] = 1
    return f'You visited this site {session["counter"]} times.'

if __name__ == '__main__':
    app.run(debug=True)
