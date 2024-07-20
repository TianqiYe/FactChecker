import os
from flask import (
    Flask,
    request,
    render_template,
    make_response,
    jsonify,
)
from flask_cors import CORS
from routing import backend

def create_app():
    app = Flask(__name__)
    app.register_blueprint(backend, url_prefix='/')
    return app

app = create_app()
CORS(app)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 7860)),use_reloader=False)