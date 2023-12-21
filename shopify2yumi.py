import csv, datetime
import glob
import os
import pandas as pd
import numpy as np
import zipfile 
from io import BytesIO

if not os.path.exists('./yumi_output'):
    os.makedirs('./yumi_output')


def image_file_process(latest_file_ds):
    full_fill_img = latest_file_ds.copy()
    full_fill_img.ffill(inplace=True, axis=0)
    full_fill_img.insert(1, "code", full_fill_img["Variant SKU"].str[:-3])
    full_fill_img.rename(columns={'Image Src': 'imageURL'}, inplace=True)

    new_img_ds = full_fill_img[['code', 'imageURL']].copy()

    new_img_ds.insert(1, "type", full_fill_img["code"].duplicated(keep='first'))

    new_img_ds["type"] = new_img_ds["type"].map({True: 'Secondary', False: 'Primary'})

    new_img_ds.to_excel("yumi_output/image.xlsx", index=False)


def product_file_process(filtered_variations):

    product_df = filtered_variations[['code', 'title', 'description', 'category', 'size', 'variantCode', 'barcode', 'rrp', 'productBrand']].copy()

    size_index = product_df.columns.get_loc('size')


    product_df.insert(size_index, 'colour', product_df['title'].str.split().str.get(0))
    variant_code_index = product_df.columns.get_loc('variantCode')
    product_df.insert(variant_code_index, 'sequence', '0')

    product_brand_index = product_df.columns.get_loc('productBrand')
    product_df.insert(product_brand_index, 'sellPrice', np.nan)


    product_df["season"] = ""
    product_df["origin"] = "China"
    product_df["composition"] = ""
    product_df["careInstructions"] = ""

    commodity_codes = {
        "Dress" : 6204430000,
        "Suit" : 6204130000,
        "Ultra" : 6204430000,
        "Jumpsuit" : 6114300000,
        "Jumpsuits" : 6114300000,
        "Coat": 6102301000,
        "Dresses": 6204430000,
    }

    product_df["commodityCode"] = product_df["category"].map(commodity_codes)
    product_df["vatable"] = ""
    product_df.to_excel("yumi_output/product.xlsx", index=False)


def stock_file_process(filtered_variations):
    stock_df = pd.DataFrame()
    stock_df["code"] = filtered_variations["barcode"]
    stock_df["quantity"] = filtered_variations["Variant Inventory Qty"]
    stock_df.to_excel("yumi_output/stock.xlsx", index=False)




def run_csv_job(file_path):
    #csvs = glob.glob('./shopify_exports/*.csv')
    #latest_file = max(csvs, key=os.path.getctime)
    latest_file_ds = pd.read_csv(file_path)

    latest_file_ds.replace('', np.nan, inplace=True)

    filtered_variations = latest_file_ds.dropna(subset=['Option1 Value']).copy()
    filtered_variations.ffill(inplace=True, axis=0)


    filtered_variations.insert(1, "Root SKU", filtered_variations["Variant SKU"].str[:-3])

    filtered_variations.rename(columns={"Root SKU" : "code", "Title": "title", "Body (HTML)" : "description", "Type" : "category", "Option1 Value" : "size", "Variant SKU": "variantCode", "Variant Compare At Price" : "rrp", "Vendor": "productBrand", "Variant Barcode": "barcode"}, inplace=True)

    print("  Shopify2Yumi Product Converter  ")
    print("----------------------------------")
    print("Processing: yumi_output/product.xlsx")
    product_file_process(filtered_variations)
    print("Processing: yumi_output/stock.xlsx")
    stock_file_process(filtered_variations)
    print("Processing: yumi_output/image.xlsx")
    image_file_process(latest_file_ds)
    print("Creating zip file")
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'a', zipfile.ZIP_DEFLATED, False) as zf:
        for file in glob.glob('yumi_output/*.xlsx'):
            with open(file, 'rb') as excel_file:
                zf.writestr(file, excel_file.read())
    memory_file.seek(0)
    return memory_file
