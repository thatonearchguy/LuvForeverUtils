import csv, datetime
import glob
import os
import pandas as pd
import numpy as np
import csvlib
from io import BytesIO
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())



def match_yumi_orders_to_shopify(yumi_df, shopify_df, shopify_product_df):    
    shopify_df['YumiMatch'] = ""
    shopify_df['PriceDelta'] = ""
    shopify_df['Actual RRP'] = ""
    shopify_df['Sold at'] = ""
    for index, row in yumi_df.iterrows():
        found_indices = shopify_df['Name'][shopify_df['Name'] == str(row['Host Order Ref'])].index.tolist()
        if(len(found_indices) == 1):
            actual_price = shopify_product_df['rrp'][shopify_product_df['variantCode'] == row['Variant Code']]
            shopify_df['PriceDelta'][found_indices] = actual_price - row['Item Price']
            shopify_df['YumiMatch'][found_indices] = "YES"
            shopify_df['Actual RRP'][found_indices] = actual_price
            shopify_df['Sold at'][found_indices] = row['Item Price']
            shopify
        if(len(found_indices) > 1):
            for mult_indices in found_indices:
                if shopify_df['Lineitem sku'][mult_indices] == row['Variant Code']:
                    actual_price = shopify_product_df['rrp'][shopify_product_df['variantCode'] == row['Variant Code']].values[0]
                    shopify_df['PriceDelta'][mult_indices] = actual_price - row['Item Price']
                    shopify_df['YumiMatch'][mult_indices] = "YES"
                    shopify_df['Actual RRP'][mult_indices] = actual_price
                    break
                    shopify_df['Sold at'][found_indices] = row['Item Price']

    shopify_df.drop(shopify_df.columns[list(range(21, 75))], axis=1, inplace=True)
    shopify_df.drop(shopify_df.columns[[3, 6, 12, 14, 18, 19]], axis=1, inplace=True)
    shopify_df.to_csv(THIS_FOLDER + '/yumi_output/shopify-data.csv', encoding='utf-8', index=False)
                


def run_verif_job(shopify_order_path, yumi_path, shopify_product_path):
    ordered_file_ds, filtered_orders = csvlib.import_shopify_orders_from_path(shopify_order_path)
    product_file_ds, filtered_products = csvlib.import_shopify_products_from_path(shopify_product_path)
    yumi_ds = csvlib.import_yumi_orders_from_path(yumi_path, 2)

    print("  ShopifyOrderVerif  ")
    print("---------------------")
    print("Processing: Matching Yumi orders to Shopify invoice data")
    match_yumi_orders_to_shopify(yumi_ds, csvlib.filter_yumi_orders(filtered_orders), filtered_products)
    print("Done!")
    ram_zip = csvlib.generate_zip_from_dir('/yumi_output/*.csv')

    return ram_zip