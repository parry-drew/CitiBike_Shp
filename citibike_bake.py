#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# citibike_bake.py
# This script will convert the CitiBike feed to a shp using arcpy.
#
# C:\Python27\ArcGIS10.4\python.exe citibike_bake.py
#
# ---------------------------------------------------------------------------
import os, datetime, timeit, csv, json, shutil,  urllib2, arcpy, pandas, zipfile
from zipfile import *

root = os.path.abspath(os.path.curdir)
fn ="CitiBike_Stations.zip"

def baking(src):
    #manage directories
    if os.path.exists('CitiBike'):
        shutil.rmtree(root + '/CitiBike')
        os.makedirs('CitiBike')
        print("\n    REPLACED CITIBIKE FOLDER.")
    else:
        os.makedirs('CitiBike')
        print("\n    CREATED CITIBIKE FOLDER.")
    #used to over come proxy issue in the office
    proxy = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    #Gets CitiBike JSON data
    response = urllib2.urlopen(src)
    data = json.load(response)
    #Convers data to a JSON file
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
    #Converts JSON file to CSV
    df = pandas.read_json("data.json")
    df.to_csv('citibike.csv')
    #Converts CSV to SHP
    spatial_ref = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision"
    arcpy.env.workspace = root
    arcpy.MakeXYEventLayer_management("citibike.csv", "longitude", "latitude", "CitiBike_Stations", spatial_ref)
    arcpy.FeatureClassToShapefile_conversion("CitiBike_Stations", root + "/CitiBike")
    #Remove Fields from SHP
    arcpy.DeleteField_management(root+"\\CitiBike\\CitiBike_Stations.shp",["altitude", "lastCommun", "availableD","availableB"])
    #Zip SHP
    zipf = zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED)
    zipdir('tmp/', zipf)
    zipf.close(
    #Clean
    os.remove(root + "/data.json")
    os.remove(root + "/citibike.csv")

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def main():
    start = timeit.default_timer()
    print("\n    LET'S START BAKING.")

    json_src = "https://a841-dotweb01.nyc.gov/DOTTransit/api/CitiBike/40.48456/40.96953/-74.28406/-73.54797"
    baking(json_src)

    stop = timeit.default_timer()
    m, s = divmod(stop - start, 60)
    h, m = divmod(m, 60)

    print("\n    YOUR CITIBIKE BAKE IS READY.")
    print("\n    " +  str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')) )
    print("\n    TOTAL RUN TIME: " +  "%d:%02d:%02d" % (h, m, s))

if __name__ == '__main__':
    main()
