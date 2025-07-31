from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for, flash, get_flashed_messages
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/mnt/cloudusb'
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Hardcoded correct credentials
CORRECT_EMAIL = "viratshm@gmail.com"
CORRECT_PASSWORD = "Virat06"
CORRECT_PIN = "0606"

# HTML for cloud (login) page
CLOUD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cloud Login</title>
  <link rel="stylesheet" href="/cloud.css">
</head>
<body>
  <div class="container">
    <h2>Login to Cloud</h2>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="error">{{ messages[0] }}</div>
      {% endif %}
    {% endwith %}
    <form method="POST" action="/">
      <input type="email" name="email" placeholder="Email" required>
      <input type="password" name="password" placeholder="Password" required>
      <input type="text" name="pin" placeholder="PIN" required>
      <button type="submit">Login</button>
    </form>
  </div>
</body>
</html>
"""

# HTML for upload page
UPLOAD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cloud Upload</title>
  <link rel="stylesheet" href="/cloud.css">
</head>
<body>
  <div class="container">
    <h2>Upload a file</h2>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file" required>
      <button type="submit">Upload</button>
    </form>

    <h3>Uploaded Files</h3>
    <ul>
    {% for file in files %}
      <li><a href="/download/{{ file }}">{{ file }}</a></li>
    {% endfor %}
    </ul>
  </div>
</body>
</html>
"""

# Allow all files
def allowed_file(filename):
    return True

# Rename files if they exist
def rename_if_exists(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_name = filename
    while os.path.exists(os.path.join(UPLOAD_FOLDER, new_name)):
        new_name = f"{base}_{counter}{ext}"
        counter += 1
    return new_name

# Main login page
@app.route('/', methods=['GET', 'POST'])
def cloud_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        pin = request.form.get('pin')
        
        if email == CORRECT_EMAIL and password == CORRECT_PASSWORD and pin == CORRECT_PIN:
            return redirect('/upload')
        else:
            flash('Invalid credentials. Please try again.')
            return redirect('/')
    return render_template_string(CLOUD_PAGE)

# Upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            filename = rename_if_exists(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file'))
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if not f.startswith('.')]
    return render_template_string(UPLOAD_PAGE, files=files)

# File download
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/cloud.css')
def cloud_css():
    return send_from_directory('.', 'cloud.css')

@app.route('/upload.css')
def upload_css():
    return send_from_directory('.', 'upload.css')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
