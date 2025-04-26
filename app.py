from flask import Flask, render_template, request, flash, redirect, url_for
from summarizer import summarize_text, extract_text_from_pdf
import os
import tempfile 

app = Flask(__name__, static_folder='static folder') 
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def home():
    return render_template('index.html', summary="")

@app.route('/summarize', methods=['POST'])
def summarize():
    input_text = None
    summary = ""
    error = None

    try:
        input_type = request.form.get('input_type')

        if input_type == 'text':
            input_text = request.form.get('text')
            if not input_text or input_text.isspace():
                error = "Please enter some text to summarize."

        elif input_type == 'file':
            uploaded_file = request.files.get('file') 
            if uploaded_file and uploaded_file.filename != '':
                filename = uploaded_file.filename
                file_ext = os.path.splitext(filename)[1].lower()

                
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                    uploaded_file.save(temp_file.name)
                    temp_file_path = temp_file.name

                print(f"File saved temporarily to: {temp_file_path}") 

                try:
                    if file_ext == '.pdf':
                        
                        input_text = extract_text_from_pdf(temp_file_path)
                        if input_text is None:
                            error = "Could not extract text from the PDF. It might be image-based or corrupted."
                    elif file_ext == '.txt':
                        with open(temp_file_path, 'r', encoding='utf-8') as f:
                            input_text = f.read()
                    else:
                        error = "Please upload a valid PDF or TXT file."
                finally:
                    
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                        print(f"Temporary file {temp_file_path} removed.") 

            else:
                error = "No file uploaded or file is empty."
        else:
            error = "Invalid input type selected."

        
        if error is None and input_text:
            print("Starting summarization...") 
            
            summary = summarize_text(input_text)
            print("Summarization complete.") 
            if not summary or "Error during summarization" in summary:
                error = f"Summarization failed. Details: {summary}"

        elif error is None and not input_text:
             
             error = "Extracted text was empty. Cannot summarize."

    except Exception as e:
        print(f"An unexpected error occurred: {e}") 
        error = f"An unexpected error occurred: {e}"

    
    if error:
        flash(error, 'error') 
        return redirect(url_for('home')) 
    else:   
        return render_template('index.html', summary=summary)


if __name__ == '__main__':
    app.run(debug=True)
