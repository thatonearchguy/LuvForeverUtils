from flask import Flask, render_template, request, send_file
import shopify2yumi
import shopify2gs1
import os
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())

app = Flask(__name__)

@app.route('/shopify2gs1', methods=['POST'])
def shopify2gs1_route():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_products = request.files['shopify']
        uploaded_gs1s = request.files['gs1']
        # Save the file temporarily (you might want to handle this more securely)
        product_file_path = THIS_FOLDER + '/gs1_exports/' + uploaded_products.filename
        gs1_file_path = THIS_FOLDER + '/gs1_exports/' + uploaded_gs1s.filename

        uploaded_products.save(product_file_path)
        uploaded_gs1s.save(gs1_file_path)
        # Process the CSV file
        result_file = shopify2gs1.run_csv_job(product_file_path, gs1_file_path)

        return send_file(result_file, as_attachment=True, mimetype='application/zip', download_name='barcode-output.zip')


@app.route('/shopify2yumi', methods=['POST'])
def shopify2yumi_route():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.files['file']
        # Save the file temporarily (you might want to handle this more securely)
        file_path = THIS_FOLDER + '/shopify_exports/' + uploaded_file.filename

        uploaded_file.save(file_path)
        # Process the CSV file
        result_file = shopify2yumi.run_csv_job(file_path, request.form.get('stockonly'))

        return send_file(result_file, as_attachment=True, mimetype='application/zip', download_name='yumi-output.zip')


@app.route('/', methods=['GET', 'POST'])
def index():

    dirs = ['yumi_output', 'shopify_exports', 'gs1_exports', 'gs1_output']

    for entry in dirs:
        if not os.path.exists(THIS_FOLDER + f'/{entry}'):
            os.makedirs(THIS_FOLDER + f'/{entry}')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)