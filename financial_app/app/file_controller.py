import os
from flask import request, redirect, flash, render_template, url_for
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from app.models import File
from app import db, app  # Assuming db and app are initialized in app/__init__.py

# Upload folder settings
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Check if the file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to upload a file (Only accessible to authenticated users)
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # Check if a file is in the request
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']
        
        # Check if a file is selected
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        # Check if file type is allowed and process the upload
        if file and allowed_file(file.filename):
            # Secure the filename to prevent issues with special characters
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save the file to the upload folder
            try:
                file.save(filepath)

                # Save file metadata to the database
                new_file = File(user_id=current_user.id, filename=filename, filepath=filepath)
                db.session.add(new_file)
                db.session.commit()

                flash('File uploaded successfully', 'success')
                return redirect(url_for('upload_file'))
            except Exception as e:
                # Handle errors related to saving the file or database issues
                flash(f'Error saving file: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('File type not allowed', 'danger')
            return redirect(request.url)

    return render_template('upload.html')
