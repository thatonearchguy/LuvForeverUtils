from flask import Flask, render_template, request, send_file
import shopify2yumi
import shopify2gs1
import shopify2ogden
import shopifysku
import shopifyorderverif
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

@app.route('/shopify2ogden_asn', methods=['POST'])
def shopify2ogden_asn_route():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.files['file']

        file_path = THIS_FOLDER + '/shopify_exports/' + uploaded_file.filename

        uploaded_file.save(file_path)
        # Process the CSV file
        result_file = shopify2ogden.run_asn_job(file_path)

        return send_file(result_file, as_attachment=True, mimetype='application/zip', download_name='ogden-asn-ouput.zip')


@app.route('/shopify2ogden_product', methods=['POST'])
def shopify2ogden_product_route():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.files['file']

        file_path = THIS_FOLDER + '/shopify_exports/' + uploaded_file.filename

        uploaded_file.save(file_path)
        # Process the CSV file
        result_file = shopify2ogden.run_product_job(file_path)


        return send_file(result_file, as_attachment=True, mimetype='application/zip', download_name='ogden-product-output.zip')

@app.route('/shopifysku_gen', methods=['POST'])
def shopifysku_gen_route():
    if request.method == 'POST':
        uploaded_file = request.files['file']

        file_path = THIS_FOLDER + '/shopify_exports/' + uploaded_file.filename

        uploaded_file.save(file_path)
        # Process the CSV file
        result_file = shopifysku.run_sku_job(file_path) 

        return send_file(result_file, as_attachment=True, mimetype='application/zip', download_name='yumi-output.zip')

@app.route('/shopify2yumi', methods=['POST'])
def shopify2yumi_route():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.files['file']

        file_path = THIS_FOLDER + '/shopify_exports/' + uploaded_file.filename

        uploaded_file.save(file_path)
        # Process the CSV file
        result_file = shopify2yumi.run_csv_job(file_path, request.form.get('stockonly'))

        return send_file(result_file, as_attachment=True, mimetype='application/zip', download_name='yumi-output.zip')


@app.route('/shopify2yumi_order', methods=['POST'])
def shopify2yumi_order_verif_route():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_orders = request.files['shopify_order']
        uploaded_yumi = request.files['yumi']
        uploaded_products = request.files['shopify_product']
        # Save the file temporarily (you might want to handle this more securely)
        product_file_path = THIS_FOLDER + '/shopify_exports/' + uploaded_products.filename
        order_file_path = THIS_FOLDER + '/shopify_exports/' + uploaded_orders.filename
        yumi_file_path = THIS_FOLDER + '/yumi_exports/' + uploaded_yumi.filename

        uploaded_products.save(product_file_path)
        uploaded_yumi.save(yumi_file_path)
        uploaded_orders.save(order_file_path)
        # Process the CSV file
        result_file = shopifyorderverif.run_verif_job(order_file_path, yumi_file_path, product_file_path)

        return send_file(result_file, as_attachment=True, mimetype='application/zip', download_name='order-verif-output.zip')


@app.route('/', methods=['GET', 'POST'])
def index():

    dirs = ['ogden_output', 'yumi_output', 'shopify_exports', 'gs1_exports', 'gs1_output', 'sku_exports', 'yumi_exports']

    for entry in dirs:
        if not os.path.exists(THIS_FOLDER + f'/{entry}'):
            os.makedirs(THIS_FOLDER + f'/{entry}')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
