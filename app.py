from flask import Flask, render_template, jsonify, request


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/ping', methods=['GET'])
    def ping():
        return jsonify({'pong': True})

    # Example POST endpoint
    @app.route('/api/echo', methods=['POST'])
    def echo():
        data = request.get_json() or {}
        return jsonify({'you_sent': data})

    return app
