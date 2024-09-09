import os
from flask import request, redirect, flash, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from app.models import File
from app import db, app  # Assuming db and app are initialized in app/__init__.py

# Upload folder settings
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
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
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(filepath)
                # Save file metadata to the database
                new_file = File(user_id=current_user.id, filename=filename, filepath=filepath)
                db.session.add(new_file)
                db.session.commit()

                flash('File uploaded successfully', 'success')
                return redirect(url_for('upload_file'))
            except Exception as e:
                flash(f'Error saving file: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('File type not allowed', 'danger')
            return redirect(request.url)

    return render_template('upload.html')

# Route to display the list of files (Only accessible to authenticated users)
@app.route('/download', methods=['GET'])
@login_required
def list_files():
    try:
        files = File.query.filter_by(user_id=current_user.id).all()
        return render_template('download.html', files=files)
    except Exception as e:
        flash(f'Error retrieving files: {str(e)}', 'danger')
        return redirect(url_for('upload_file'))

# Route to download a specific file (Only accessible to authenticated users)
@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_selected_file(filename):
    try:
        # Construct the file path from the uploads directory
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if the file exists in the uploads folder
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            flash(f'File "{filename}" not found in uploads folder.', 'danger')
            return redirect(url_for('list_files'))
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'danger')
        return redirect(url_for('list_files'))

# Route to delete a specific file (Only accessible to authenticated users)
@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    try:
        # Get the file from the database
        file_record = File.query.filter_by(filename=filename, user_id=current_user.id).first()
        if file_record:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Check if the file exists in the upload folder
            if os.path.exists(file_path):
                # Delete the file from the file system
                os.remove(file_path)

                # Delete the file record from the database
                db.session.delete(file_record)
                db.session.commit()

                flash(f'File "{filename}" has been deleted successfully.', 'success')
            else:
                flash(f'File "{filename}" not found on the server.', 'danger')
        else:
            flash(f'File "{filename}" not found in the database.', 'danger')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'danger')
    
    return redirect(url_for('list_files'))
