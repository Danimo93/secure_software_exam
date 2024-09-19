# app/file_controller.py
import os
from flask import request, redirect, flash, render_template, url_for, send_file, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from app.models import File
from app import db, app
from cryptography.fernet import Fernet
import io

encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

UPLOAD_FOLDER = os.path.join(app.config['UPLOAD_FOLDER'])
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'php', 'py'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encrypt_file(file_content):
    """Encrypt file content."""
    return cipher.encrypt(file_content)

def decrypt_file(file_content):
    """Decrypt file content."""
    return cipher.decrypt(file_content)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """Handle file upload."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(url_for('upload_file_route'))

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(url_for('upload_file_route'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if filename.endswith('.txt'):
                    encrypted_content = encrypt_file(file.read())
                    with open(filepath, 'wb') as encrypted_file:
                        encrypted_file.write(encrypted_content)
                else:
                    file.save(filepath)
                new_file = File(user_id=current_user.id, filename=filename, filepath=filepath)
                db.session.add(new_file)
                db.session.commit()
                flash('File uploaded successfully!', 'success')
                return redirect(url_for('upload_file_route'))
            except Exception as e:
                flash(f'Error saving file: {str(e)}', 'danger')
                return redirect(url_for('upload_file_route'))
        else:
            flash('File type not allowed.', 'danger')
            return redirect(url_for('upload_file_route'))

    return render_template('upload.html')

@app.route('/download', methods=['GET'])
@login_required
def list_files():
    """List all files for the current user."""
    try:
        files = File.query.filter_by(user_id=current_user.id).all()
        return render_template('download.html', files=files)
    except Exception as e:
        flash(f'Error retrieving files: {str(e)}', 'danger')
        return redirect(url_for('upload_file_route'))

@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_selected_file(filename):
    """Handle file download and decryption for .txt files."""
    try:
        sanitized_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], sanitized_filename)

        if os.path.exists(file_path):
            if sanitized_filename.endswith('.txt'):
                with open(file_path, 'rb') as encrypted_file:
                    encrypted_content = encrypted_file.read()
                    decrypted_content = decrypt_file(encrypted_content)
                return send_file(
                    io.BytesIO(decrypted_content),
                    mimetype='text/plain',
                    as_attachment=True,
                    download_name=sanitized_filename
                )
            else:
                return send_from_directory(app.config['UPLOAD_FOLDER'], sanitized_filename, as_attachment=True)
        else:
            flash(f'File "{sanitized_filename}" not found.', 'danger')
            return redirect(url_for('list_files_route'))
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'danger')
        return redirect(url_for('list_files_route'))

@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    """Handle file deletion."""
    try:
        sanitized_filename = secure_filename(filename)
        file_record = File.query.filter_by(filename=sanitized_filename, user_id=current_user.id).first()

        if file_record:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], sanitized_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                db.session.delete(file_record)
                db.session.commit()
                flash(f'File "{sanitized_filename}" deleted successfully.', 'success')
            else:
                flash(f'File "{sanitized_filename}" not found on the server.', 'danger')
        else:
            flash(f'File "{sanitized_filename}" not found in the database.', 'danger')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'danger')

    return redirect(url_for('list_files_route'))
