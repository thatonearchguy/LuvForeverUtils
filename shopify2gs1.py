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

def run_csv_job(file_path, stock_only):
    #csvs = glob.glob('./shopify_exports/*.csv')
    #latest_file = max(csvs, key=os.path.getctime)
    latest_file_ds, filtered_variations = csvlib.import_csv_from_path(file_path)

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

    return ram_zip