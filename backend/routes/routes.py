from flask import send_from_directory
from services.services import generate_outfit

def setup_routes(app):
    @app.route('/')
    def serve_frontend():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/generate-outfit', methods=['POST'])
    def generate_outfit_route():
        return generate_outfit()