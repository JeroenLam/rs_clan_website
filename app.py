from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', title='Game Tools & Overviews')

@app.route('/tools')
def tools():
    return render_template('tools.html', title='Game Tools')

@app.route('/overview')
def overview():
    return render_template('overview.html', title='Game Overview')

@app.route('/stats')
def stats():
    return render_template('stats.html', title='Game Stats')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
