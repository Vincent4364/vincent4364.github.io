from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# New route to receive data from ESP32
@app.route('/submit', methods=['POST'])
def submit():
    time = request.form.get('time')
    if time:
        print(f"Received reaction time: {time} ms")  # Debug print
        # Later, you can save it to a database here
        return "OK", 200
    return "Missing time", 400

if __name__ == '__main__':
    # host='0.0.0.0' makes Flask listen on your local network
    app.run(debug=True, host='0.0.0.0', port=5000)
