import csv, datetime
import glob
import os
import pandas as pd
import numpy as np
import csvlib
from io import BytesIO
from pathlib import Path
THIS_FOLDER = str(Path(__file__).parent.resolve())


def ogden_product_csv_process(filtered_variations):
    auto_fields = ['SKU', 'Name', 'EANBarcode', 'UPCBarcode', 'Description', 'Discontinued', 'BackOrderable', 'CommodityCode', 'CustomsDescription', 'CountryOfManufacture', 'Categories', 'Suppliers', 'HasBatchNumber', 'LogBatchInbound', 'LogBatchOutbound', 'HasSerialNumber', 'LogSerialInbound', 'LogSerialOutbound', 'LowStockAlertLevel', 'Weight', 'Height', 'Length', 'Depth', 'Price', 'CostPrice', 'Volume', 'PalletSizes', 'FirstItemPickingCost', 'AdditionalItemPickingCost', 'FirstCartonPickingCost', 'AdditionalCartonPickingCost', 'FirstPalletPickingCost', 'AdditionalPalletPickingCost', 'StorageUnit', 'PackagingFee', 'AdditionalParcelsRequired', 'ImageURL', 'UnNumber', 'HandlingTime', 'HasExpiryDate', 'LogExpiryDateInbound', 'LogExpiryDateOutbound', 'FreePickingAsAdditional', 'PackingInstructions', 'InfiniteStock', 'BestBeforeDateWarningPeriodDays', 'UnitsPerParcel', 'NewSKU', 'OpeningStockLevel', 'Location', 'GoodsInCostSku', 'GoodsInCostUnit', 'AmazonFBAActive', 'ASIN', 'FNSKU', 'FBALabelQty']

    generated_product_csv = pd.DataFrame()

    for i in auto_fields:
        generated_product_csv[i] = ""

    generated_product_csv['SKU'] = filtered_variations['barcode']    
    generated_product_csv['Name'] = filtered_variations['title'] + " " + filtered_variations['size']
    generated_product_csv['EANBarcode'] = filtered_variations['barcode']
    generated_product_csv['Description'] = filtered_variations['description']
    generated_product_csv['Discontinued'] = 'N'
    generated_product_csv['BackOrderable'] = 'Y'
    generated_product_csv['CommodityCode'] = filtered_variations['category'].map(csvlib.commodity_codes)
    generated_product_csv['CustomsDescription'] = "Women's Eveningwear"
    generated_product_csv['CountryOfManufacture'] = 'China'
    generated_product_csv['PackingInstructions'] = 'Bubble Bag'
    raise KeyError
    generated_product_csv.to_csv(THIS_FOLDER + '/ogden_output/products.csv', encoding='utf-8', index=False)


def ogden_asn_csv_process(filtered_variations):
    ogden_asn_df = pd.DataFrame()
    ogden_asn_df['SKU'] = filtered_variations['barcode']
    ogden_asn_df['Quantity'] = filtered_variations['Variant Inventory Qty']
    ogden_asn_df['Name'] = filtered_variations['title'] + " " + filtered_variations['size']
    ogden_asn_df['EANBarcode'] = filtered_variations['barcode']
    ogden_asn_df['UPCBarcode'] = ""
    ogden_asn_df['WeightInKG'] = ""
    ogden_asn_df['Height'] = ""
    ogden_asn_df['Length'] = ""
    ogden_asn_df['Depth'] = ""
    ogden_asn_df['DefaultLocation'] = ""
    ogden_asn_df['CommodityCode'] = filtered_variations['category'].map(csvlib.commodity_codes)
    ogden_asn_df['CountryOfManufacture'] = 'China'
    ogden_asn_df['CustomsDescription'] = "Women's Eveningwear"
    ogden_asn_df['SSCCNumber'] = ""

    ogden_asn_df.to_csv(THIS_FOLDER + '/ogden_output/asn.csv', encoding='utf-8', index=False)


def run_asn_job(shopify_path):
    #csvs = glob.glob('./shopify_exports/*.csv')
    #latest_file = max(csvs, key=os.path.getctime)
    latest_file_ds, filtered_variations = csvlib.import_shopify_from_path(shopify_path)

    print("  Shopify2Ogden ASN Generator  ")
    print("-------------------------------")
    print("Processing: Generating Ogden format ASN")
    ogden_asn_csv_process(filtered_variations)
    print("Done!")
    ram_zip = csvlib.generate_zip_from_dir('/ogden_output/*.csv')

    return ram_zip



def run_product_job(shopify_path):
    #csvs = glob.glob('./shopify_exports/*.csv')
    #latest_file = max(csvs, key=os.path.getctime)
    latest_file_ds, filtered_variations = csvlib.import_shopify_from_path(shopify_path)

    print("  Shopify2Ogden Product Sheet Generator  ")
    print("-----------------------------------------")
    print("Processing: Generating Ogden format product sheet")
    ogden_product_csv_process(filtered_variations)
    print("Done!")
    ram_zip = csvlib.generate_zip_from_dir('/ogden_output/*.csv')
    return ram_zip