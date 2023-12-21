from flask import Flask, render_template, request, send_file
import shopify2yumi
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.files['file']

        # Save the file temporarily (you might want to handle this more securely)
        file_path = THIS_FOLDER + '/shopify_exports/' + uploaded_file.filename

        uploaded_file.save(file_path)

        # Process the CSV file
        result_file = shopify2yumi.run_csv_job(file_path)

        return send_file(result_file, as_attachment=True, mimetype='application/zip', download_name='yumi-output.zip')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)