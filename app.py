import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

# Folder to save QR codes
qr_code_root_dir = "qrcodes"
if not os.path.exists(qr_code_root_dir):
    os.makedirs(qr_code_root_dir)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User data for login purposes
users = {
    'kraftit': {'password': 'Kraft@qr'}
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash("Login successful!", 'success')
            return redirect(request.args.get('next') or url_for('home'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    categories_data = {
        'Laptops': [],
        'Desktops': []
    }

    # Read files in each category folder
    for category in categories_data.keys():
        category_dir = os.path.join(qr_code_root_dir, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)  # Create category folder if it doesn't exist
        qr_codes = []
        for qr_file in os.listdir(category_dir):
            if qr_file.endswith('.png'):
                qr_codes.append({
                    'name': qr_file.split('.')[0],
                    'created_at': datetime.fromtimestamp(os.path.getctime(os.path.join(category_dir, qr_file))).strftime('%Y-%m-%d %H:%M:%S')
                })
        categories_data[category] = qr_codes

    # Pass categories_data to the template
    return render_template('index.html', categories_data=categories_data)


@app.route('/generate', methods=['POST'])
@login_required
def generate_qr():
    qr_code_name = request.form['qr_code_name']
    qr_data = {
        'Cubicle Number': request.form['cubicle_number'],
        'Serial Number': request.form['serial_number'],
        'Hostname': request.form['hostname'],
        'MAC ID': request.form['mac_id'],
        'RAM': request.form['ram'],
        'Processor': request.form['processor'],
        'OS': request.form['os'],
        'Storage': request.form['storage'],
        'Brand': request.form['brand']
    }

    category = request.form['category']
    category_dir = os.path.join(qr_code_root_dir, category)

    if os.path.exists(os.path.join(category_dir, f"{qr_code_name}.png")):
        flash(f"A QR code with the name '{qr_code_name}' already exists in the '{category}' category.", 'error')
        return redirect(url_for('home'))

    qr_data_str = "\n".join(f"{key}: {value}" for key, value in qr_data.items())
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(qr_data_str)
    qr.make(fit=True)

    # Create image from QR code and add the QR code name text
    img = qr.make_image(fill='black', back_color='white')
    draw = ImageDraw.Draw(img)
    
    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 20)  # Change to any font you prefer
    except IOError:
        font = ImageFont.load_default()

    text = qr_code_name
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position_x = (img.width - text_width) // 100 # Center horizontally
    text_position_y = img.height - text_height - 10  # Position 10px from the bottom
    draw.text((text_position_x, text_position_y), text, fill="black", font=font)
    
    if not os.path.exists(category_dir):
        os.makedirs(category_dir)
    img.save(os.path.join(category_dir, f"{qr_code_name}.png"))

    flash(f"QR code '{qr_code_name}' successfully created in the '{category}' category.", 'success')
    return redirect(url_for('home'))


@app.route('/delete/<category>/<qr_code_name>')
@login_required
def delete_qr(category, qr_code_name):
    category_dir = os.path.join(qr_code_root_dir, category)
    os.remove(os.path.join(category_dir, f"{qr_code_name}.png"))
    flash(f"QR code '{qr_code_name}' successfully deleted.", 'success')
    return redirect(url_for('home'))

@app.route('/download/<category>/<qr_code_name>')
@login_required
def download_qr(category, qr_code_name):
    category_dir = os.path.join(qr_code_root_dir, category)
    return send_from_directory(category_dir, f"{qr_code_name}.png", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
