import csv, datetime
import glob
import os
import pandas as pd
import numpy as np
import csvlib
from io import BytesIO
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())



def match_yumi_orders_to_shopify(yumi_df, shopify_df):    
    shopify_df['YumiMatch'] = ""
    shopify_df['PriceDelta'] = ""
    for index, row in yumi_df.iterrows():
        found_indices = shopify_df['Name'][shopify_df['Name'] == str(row['Host Order Ref'])].index.tolist()
        if(len(found_indices) == 1):
            shopify_df['PriceDelta'][found_indices[0]] = shopify_df['Lineitem price'][found_indices[0]] - row['Item Price']
            shopify_df['YumiMatch'][found_indices] = "YES"
        if(len(found_indices) > 1):
            for mult_indices in found_indices:
                if shopify_df['Lineitem sku'][mult_indices] == yumi_df['Variant Code'][index]:
                    shopify_df['PriceDelta'][mult_indices] = shopify_df['Lineitem price'][found_indices] - yumi_df['Item Price']
                    shopify_df['YumiMatch'][mult_indices] = "YES"

    shopify_df.drop(shopify_df.columns[list(range(21, 75))], axis=1, inplace=True)
    shopify_df.drop(shopify_df.columns[[3, 6, 12, 14]], axis=1, inplace=True)
    shopify_df.to_csv(THIS_FOLDER + '/yumi_output/shopify-data.csv', encoding='utf-8', index=False)
                


def run_verif_job(shopify_path, yumi_path):
    latest_file_ds, filtered_variations = csvlib.import_shopify_orders_from_path(shopify_path)
    
    yumi_ds = csvlib.import_yumi_orders_from_path(yumi_path, 2)

    print("  ShopifyOrderVerif  ")
    print("---------------------")
    print("Processing: Matching Yumi orders to Shopify invoice data")
    match_yumi_orders_to_shopify(yumi_ds, csvlib.filter_yumi_orders(filtered_variations))
    print("Done!")
    ram_zip = csvlib.generate_zip_from_dir('/yumi_output/*.csv')

    return ram_zip