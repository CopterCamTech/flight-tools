import os
from flask import Flask
from webapp.routes.bin_routes import bin_bp
from webapp.routes.ulg_routes import ulg_bp  # ✅ Add this line

app = Flask(__name__)

# Ensure the upload folder is correctly resolved
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

app.register_blueprint(bin_bp)
app.register_blueprint(ulg_bp)  # ✅ Register the PX4 route

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
