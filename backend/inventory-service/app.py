from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask
from middleware.error_handler import register_error_handlers
from exceptions.api_exceptions import APIException
from routes.invetory_routes import inventory_bp
from db.db_connection import DBConnection

def create_app() -> Flask:
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    app = Flask(__name__)
    app.config['ENV'] = FLASK_ENV
    register_error_handlers(app)

    app.register_blueprint(inventory_bp)

    return app

if __name__ == '__main__':
    
    app = create_app()
    port = int(os.environ.get('INVENTORY_SERVICE_PORT_HOST', 8000))
    app.run(debug=True, port=port)
