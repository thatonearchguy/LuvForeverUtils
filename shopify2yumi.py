import csv, datetime
import glob
import os
import pandas as pd
import numpy as np
import csvlib
from io import BytesIO
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())



def image_file_process(latest_file_ds):
    full_fill_img = latest_file_ds.copy()
    full_fill_img.ffill(inplace=True, axis=0)
    full_fill_img.insert(1, "code", full_fill_img["Variant SKU"].str[:-3])
    full_fill_img.rename(columns={'Image Src': 'imageURL'}, inplace=True)

    new_img_ds = full_fill_img[['code', 'imageURL']].copy()

    new_img_ds.insert(1, "type", full_fill_img["code"].duplicated(keep='first'))

    new_img_ds["type"] = new_img_ds["type"].map({True: 'Secondary', False: 'Primary'})

    new_img_ds.to_excel(THIS_FOLDER + "/yumi_output/image.xlsx", index=False)


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
    product_df.to_excel(THIS_FOLDER + "/yumi_output/product.xlsx", index=False)


def stock_file_process(filtered_variations):
    stock_df = pd.DataFrame()
    stock_df["code"] = filtered_variations["barcode"]
    stock_df["quantity"] = filtered_variations["Variant Inventory Qty"]
    stock_df.to_excel(THIS_FOLDER + "/yumi_output/stock.xlsx", index=False)


def price_file_process(filtered_variations):
    price_df = pd.DataFrame()
    price_df["code"] = filtered_variations["barcode"]
    price_df["price"] = filtered_variations["rrp"]
    price_df["currency"] = "GBP"
    price_df.to_excel(THIS_FOLDER + "/yumi_output/price.xlsx", index=False)


def run_csv_job(file_path, stock_only):
    #csvs = glob.glob('./shopify_exports/*.csv')
    #latest_file = max(csvs, key=os.path.getctime)
    latest_file_ds, filtered_variations = csvlib.import_shopify_from_path(file_path)

    print("  Shopify2Yumi Product Converter  ")
    print("----------------------------------")
    print("Processing: yumi_output/stock.xlsx")
    stock_file_process(filtered_variations)
    if(stock_only != "stock"):
        print("Processing: yumi_output/product.xlsx")
        product_file_process(filtered_variations)
        print("Processing: yumi_output/image.xlsx")
        image_file_process(latest_file_ds)
        print("Processing: yumi_output/price.xlsx")
        price_file_process(filtered_variations)
    
    ram_zip = csvlib.generate_zip_from_dir('/yumi_output/*.xlsx')
    os.remove(file_path)

    return ram_zip

