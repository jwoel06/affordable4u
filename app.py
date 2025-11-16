from flask import Flask, render_template, jsonify, request
from counselor import MyCounselor

app = Flask(__name__)

chatbot = MyCounselor()

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data['message']
    degree = data.get('degree_type', '4year')

    chatbot.set_degree_preference(degree)

    response = chatbot.counselor_chat(message)

    return jsonify({"reply": response})


@app.route("/faq")
def faq():
    return render_template('faq.html')

@app.route("/about")
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)