import csv, datetime
import glob
import os
import pandas as pd
import numpy as np
import zipfile 
import csvlib

from io import BytesIO
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())


def update_gs1_process(filtered_variations, gs1_file_ds):
    left_join = pd.merge(gs1_file_ds, filtered_variations, on='Number', how='left')
    
    #Copying data from shopify side after left join
    left_join['Product Name'] = left_join['title']
    left_join['Description'] = left_join['description']
    left_join['Main Brand'] = left_join['productBrand']
    left_join['SKU'] = left_join['variantCode']

    left_join['Product Link'] = left_join['Handle'].map(lambda x: "https://luvforeverfashion.com/products/" + str(x))

    left_join.iloc[:,:10].to_csv(THIS_FOLDER + '/gs1_output/gs1-numberbank.csv', encoding='utf-8', index=False)

    return left_join.iloc[:,:10]


def update_shopify_process(og_shopify_csv, filtered_variations, gs1_file_ds):
    cond = filtered_variations['barcode'].isna().loc[lambda x: x==True]
    gs1_cond = gs1_file_ds['Product Name'].isna().loc[lambda x: x==True]
    barcodeless_count = cond.index.size
    print(f'{barcodeless_count} products found with no barcode')
    print("Allocating range in GS1")
    for i in range(barcodeless_count):

        filtered_index = cond.index[i]
        gs1_barcode_index = gs1_cond.index[i]
        shopify_no_barcode_prod_sku = filtered_variations['variantCode'][filtered_index]
        #We are using a filtered sheet so the indexes are preserved.
        # Verification by sku is therefore unnecessary,  
        #og_shopify_sheet_row_upd = og_shopify_csv['Variant SKU'].rows.get_loc(shopify_no_barcode_prod_sku)
        #Copy new barcode
        filtered_variations['barcode'][filtered_index] = gs1_file_ds["Number"][gs1_barcode_index]
        #necessary for gs1 process to correctly match the new allocations on inner join
        filtered_variations['Number'][filtered_index] = gs1_file_ds["Number"][gs1_barcode_index]
        og_shopify_csv['Variant Barcode'][filtered_index] = gs1_file_ds["Number"][gs1_barcode_index]
        #Update GS1 bank with new data
    
    update_gs1_process(filtered_variations, gs1_file_ds)
    og_shopify_csv.to_csv(THIS_FOLDER + '/gs1_output/shopify-data.csv', encoding='utf-8', index=False)


def run_csv_job(shopify_path, gs1_path):
    #csvs = glob.glob('./shopify_exports/*.csv')
    #latest_file = max(csvs, key=os.path.getctime)
    latest_file_ds, filtered_variations = csvlib.import_shopify_products_from_path(shopify_path, ["Variant Barcode", "Variant SKU"])
    filtered_variations.insert(2, 'Number', filtered_variations['barcode'])

    gs1_file_ds = csvlib.import_csv_from_path(gs1_path, [0,1,2])
    gs1_file_ds['Number'] = gs1_file_ds['Number'].map(csvlib.strip_junk_from_barcodes)
    print("  Shopify2GS1 Barcode Population  ")
    print("----------------------------------")
    print("Processing: Updating GS1 numberbank from Shopify data")
    gs1_file_ds = update_gs1_process(filtered_variations, gs1_file_ds)
    print("Processing: Populating empty Shopify barcode ranges from GS1")
    update_shopify_process(latest_file_ds, filtered_variations, gs1_file_ds)
    print("Done!")
    ram_zip = csvlib.generate_zip_from_dir('/gs1_output/*.csv')

    return ram_zip
