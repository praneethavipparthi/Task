from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello! Flask is working!</h1><a href="/test">Test Link</a>'

@app.route('/test')
def test():
    return '<h1>Test page works!</h1><a href="/">Back to Home</a>'

if __name__ == '__main__':
    app.run(debug=True)