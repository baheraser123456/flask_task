from flask import Flask, request, send_file, redirect, flash
import os
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import PyPDF2 as p

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ZIP_FOLDER'] = 'zips'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.secret_key = 'supersecretkey' 

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['ZIP_FOLDER']):
    os.makedirs(app.config['ZIP_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return '''
    <!doctype html>
    <title>Upload PDF</title>
    <h1>Automatic Split</h1>
    <form action="/automaticsplit" method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Split">
    </form>

    <h1>Get Ranges</h1>
    <form action="/getranges" method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Get Ranges">
    </form>

    </form>

    <h1>Manual Split</h1>
    <form action="/manualsplit" method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <label for="ranges">Enter ranges (e.g. 1-3, 5-7, 10):</label>
      <input type="text" name="ranges" placeholder="1-3,5-7,10">
      <input type="submit" value="Manual Split">
    </form>
    '''

@app.route('/automaticsplit', methods=['POST'])
def automaticsplit():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        def get_ranges(file_path):
            reader = p.PdfReader(file_path)
            len_page = len(reader.pages)
            list_ranges = []
            j = 0
            for i in range(len_page):
                if i == 0:
                    continue
                text = reader.pages[i].extract_text().upper()
                if 'SECTION 1:' in text or 'SECTION 1.' in text:
                    list_ranges.append((j, i))
                    j = i
            return list_ranges


        ranges = get_ranges(file_path)
        split_files = []

        for i, (start_page, end_page) in enumerate(ranges):
            pdf_writer = p.PdfWriter()
            for page_num in range(start_page, end_page):
                pdf_writer.add_page(p.PdfReader(file_path).pages[page_num])
            output_filename = f'split_{i + 1}.pdf'
            output_path = os.path.join(app.config['ZIP_FOLDER'], output_filename)
            with open(output_path, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
            split_files.append(output_path)


        zip_filename = 'split_files.zip'
        zip_path = os.path.join(app.config['ZIP_FOLDER'], zip_filename)
        with ZipFile(zip_path, 'w') as zipf:
            for split_file in split_files:
                zipf.write(split_file, os.path.basename(split_file))
        
        return send_file(zip_path, as_attachment=True)

    return redirect(request.url)

@app.route('/getranges', methods=['POST'])
def get_ranges():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        def get_ranges(file_path):
            reader = p.PdfReader(file_path)
            len_page = len(reader.pages)
            list_ranges = []
            j = 0
            for i in range(len_page):
                if i == 0:
                    continue
                text = reader.pages[i].extract_text().upper()
                if 'SECTION 1:' in text or 'SECTION 1.' in text:
                    list_ranges.append((j, i))
                    j = i+1
            return list_ranges
        ranges = get_ranges(file_path)
        ranges_filename = 'ranges.txt'
        ranges_file_path = os.path.join(app.config['ZIP_FOLDER'], ranges_filename)
        
        with open(ranges_file_path, 'w') as f:
            for start_page, end_page in ranges:
                f.write(f"{start_page},-,{end_page}\n")

        zip_filename = 'ranges.zip'
        zip_path = os.path.join(app.config['ZIP_FOLDER'], zip_filename)
        with ZipFile(zip_path, 'w') as zipf:
            zipf.write(ranges_file_path, os.path.basename(ranges_file_path))
        
        return send_file(zip_path, as_attachment=True)

    return redirect(request.url)

@app.route('/manualsplit', methods=['POST'])
def manualsplit():
    if 'file' not in request.files or 'ranges' not in request.form:
        flash('No file or ranges provided')
        return redirect(request.url)
    
    file = request.files['file']
    ranges_input = request.form['ranges']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)


        ranges = []
        try:
            for part in ranges_input.split(','):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    ranges.append((start - 1, end))  
                else:
                    page = int(part)
                    ranges.append((page - 1, page))  
        except ValueError:
            flash('Invalid range format')
            return redirect(request.url)

        split_files = []
        reader = p.PdfReader(file_path)

        for i, (start_page, end_page) in enumerate(ranges):
            pdf_writer = p.PdfWriter()
            for page_num in range(start_page, end_page):
                pdf_writer.add_page(reader.pages[page_num])
            
            output_filename = f'split_manual_{i + 1}.pdf'
            output_path = os.path.join(app.config['ZIP_FOLDER'], output_filename)
            with open(output_path, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
            split_files.append(output_path)

        zip_filename = 'split_manual_files.zip'
        zip_path = os.path.join(app.config['ZIP_FOLDER'], zip_filename)
        with ZipFile(zip_path, 'w') as zipf:
            for split_file in split_files:
                zipf.write(split_file, os.path.basename(split_file))
        
        return send_file(zip_path, as_attachment=True)

    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)

