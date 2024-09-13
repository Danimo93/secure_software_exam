# app/file_controller.py

import os
from flask import request, redirect, flash, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from app.models import File
from app import db, app

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('upload_file')) 
        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('upload_file')) 
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
                new_file = File(user_id=current_user.id, filename=filename, filepath=filepath)
                db.session.add(new_file)
                db.session.commit()
                flash('File uploaded successfully', 'success')
                return redirect(url_for('upload_file'))
            except Exception as e:
                flash(f'Error saving file: {str(e)}', 'danger')
                return redirect(url_for('upload_file'))
        else:
            flash('File type not allowed', 'danger')
            return redirect(url_for('upload_file'))

    return render_template('upload.html')


@app.route('/download', methods=['GET'])
@login_required
def list_files():
    try:
        files = File.query.filter_by(user_id=current_user.id).all()
        return render_template('download.html', files=files)
    except Exception as e:
        flash(f'Error retrieving files: {str(e)}', 'danger')
        return redirect(url_for('upload_file'))


@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_selected_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            flash(f'File "{filename}" not found in uploads folder.', 'danger')
            return redirect(url_for('list_files'))
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'danger')
        return redirect(url_for('list_files'))


@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    try:
        safe_filename = secure_filename(filename)
        file_record = File.query.filter_by(filename=safe_filename, user_id=current_user.id).first()
        if file_record:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            print(f"Attempting to delete: {file_path}")
            if os.path.commonpath([file_path, app.config['UPLOAD_FOLDER']]) != app.config['UPLOAD_FOLDER']:
                flash('Invalid file path.', 'danger')
                return redirect(url_for('list_files'))
            if os.path.exists(file_path):
                os.remove(file_path)
                db.session.delete(file_record)
                db.session.commit()
                flash(f'File "{safe_filename}" has been deleted successfully.', 'success')
            else:
                print(f"File not found at path: {file_path}")
                flash(f'File "{safe_filename}" not found on the server.', 'danger')
        else:
            print(f"File record not found in the database for: {safe_filename}")
            flash(f'File "{safe_filename}" not found in the database.', 'danger')
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        flash(f'Error deleting file: {str(e)}', 'danger')
    return redirect(url_for('list_files'))

