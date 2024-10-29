import csv, datetime
import math
import glob
import os
import pandas as pd
import numpy as np
import csvlib
from io import BytesIO
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())


def shopify_sale_edit(latest_file_ds, percentage_sale):
    latest_file_ds['Variant Price'] = (latest_file_ds['Variant Compare At Price'] - (latest_file_ds['Variant Compare At Price'] * percentage_sale/100)) // 0.01 / 100
    latest_file_ds.to_csv(THIS_FOLDER + '/price_exports/products_export_price_update.csv', encoding='utf-8', index=False)

def run_sale_edit(file_path, percentage_sale):
    latest_file_ds, filtered_variations = csvlib.import_shopify_products_from_path(file_path)
    print("  Shopify Price Edit Generation  ")
    print("--------------------------")
    print("Processing: Generating new prices")
    #this is deliberately missing the call because we run it once during generate_sku already.
    print("Processing: Mapping prices into Shopify data")
    shopify_sale_edit(latest_file_ds, percentage_sale)
    print("Done!")

    ram_zip = csvlib.generate_zip_from_dir('/price_exports/*.csv')
    return ram_zip
