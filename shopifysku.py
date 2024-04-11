import csv, datetime
import glob
import os
import pandas as pd
import numpy as np
import csvlib
from io import BytesIO
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())

def shopify_product_highest_sku(filtered_variations):
    highest = 0
    sku_col = filtered_variations['Variant SKU'].loc[lambda x: x.str.contains('LUV', na=False)]
    for sku in sku_col.tolist():
        stripped_sku = int(sku.split('-')[1])
        if stripped_sku > highest:
            highest = stripped_sku
    return highest

def shopify_generate_sku(filtered_variations):
    sku_col = filtered_variations['Variant SKU'].isna().loc[lambda x: x==True]
    skuless_count = sku_col.index.size
    highest_sku = shopify_product_highest_sku(filtered_variations)
    sku_counter = 1
    count = 0
    while count < skuless_count:
        variation_counter = 0
        filtered_index = sku_col.index[count]
        print(filtered_variations['Vendor'][filtered_index])
        if filtered_variations['Vendor'][filtered_index] != 'LuvForever':
            continue
        product_handle = filtered_variations['Handle'][filtered_index]
        while count+variation_counter < skuless_count and product_handle == filtered_variations['Handle'][sku_col.index[count+variation_counter]]:
            current_sku = f"LUV-{highest_sku+sku_counter}-{str(variation_counter).zfill(2)}"
            print(current_sku)
            print(count+variation_counter)
            filtered_variations['Variant SKU'][sku_col.index[count+variation_counter]] = current_sku
            variation_counter += 1
        sku_counter += 1
        count += variation_counter
    filtered_variations.to_csv(THIS_FOLDER + '/sku_exports/sku_upload.csv', encoding='utf-8', index=False)

def run_sku_job(file_path):
    latest_file_ds, filtered_variations = csvlib.import_shopify_products_from_path(file_path, ["Variant Barcode", "Variant SKU"], False)
    print("  ShopifySKUs Generation  ")
    print("--------------------------")
    print("Processing: Locating highest current SKU from Shopify data")
    #this is deliberately missing the call because we run it once during generate_sku already.
    print("Processing: Generating following SKUs into Shopify data")
    shopify_generate_sku(filtered_variations)
    print("Done!")
    ram_zip = csvlib.generate_zip_from_dir('/sku_exports/*.csv')

    return ram_zip
