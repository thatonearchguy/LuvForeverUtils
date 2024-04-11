import pandas as pd
import numpy as np
from io import BytesIO
import zipfile 
import glob
import os
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())

def import_csv_from_path(file_path, rowskip=[]):
    latest_file_ds = pd.read_csv(file_path, skiprows=rowskip)

    latest_file_ds.replace('', np.nan, inplace=True)

    return latest_file_ds

def strip_junk_from_barcodes(barcode):
    return ''.join(a for a in barcode if a.isdigit())


def filter_yumi_orders(df):
    df = df[(df['Name'].str.len() == 6) | (df['Tags'] == 'Yumi')]
    return df


def import_yumi_orders_from_path(file_path, rowskip=[]):
    yumi_invoice_ds = pd.ExcelFile(file_path)
    return yumi_invoice_ds.parse('Export View', skiprows=rowskip)


def import_shopify_orders_from_path(file_path):
    latest_file_ds = import_csv_from_path(file_path)

    filtered_orders = latest_file_ds.dropna(subset=['Fulfillment Status'])
    filtered_orders = filtered_orders[filtered_orders['Fulfillment Status'] != 'unfulfilled']

    return latest_file_ds, filtered_orders


def import_shopify_products_from_path(file_path, col_skip=[], change_headers=True):
    latest_file_ds = import_csv_from_path(file_path)

    filtered_variations = latest_file_ds.dropna(subset=['Option1 Value']).copy()
    if(len(col_skip) > 0):
        filtered_variations.loc[:, filtered_variations.columns.difference(col_skip)] = filtered_variations.loc[:, filtered_variations.columns.difference(col_skip)].ffill(axis=0)
    else:
        filtered_variations.ffill(inplace=True, axis=0)

    if change_headers == True:
        filtered_variations.insert(1, "Root SKU", filtered_variations["Variant SKU"].str[:-3])

        filtered_variations.rename(columns={"Root SKU" : "code", "Title": "title", "Body (HTML)" : "description", "Type" : "category", "Option1 Value" : "size", "Variant SKU": "variantCode", "Variant Compare At Price" : "rrp", "Vendor": "productBrand", "Variant Barcode": "barcode"}, inplace=True)

    return latest_file_ds, filtered_variations


def generate_zip_from_dir(target_path):
    print("Creating zip file")
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'a', zipfile.ZIP_DEFLATED, False) as zf:
        for file in glob.glob(THIS_FOLDER + target_path):
            with open(file, 'rb') as file_contents:
                zf.writestr(file.split('/')[-1], file_contents.read())
    memory_file.seek(0)
    for file in glob.glob(THIS_FOLDER + target_path):
        os.remove(file)

    return memory_file


commodity_codes = {
        "Dress" : 6204430000,
        "Suit" : 6204130000,
        "Ultra" : 6204430000,
        "Jumpsuit" : 6114300000,
        "Jumpsuits" : 6114300000,
        "Coat": 6102301000,
        "Dresses": 6204430000,
}

