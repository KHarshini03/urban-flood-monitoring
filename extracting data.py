import requests
from datetime import datetime, timedelta

url = ""

bearer_token = ""

query = "sewerage OR overflow OR complaint"  

# Define date range
today_date = datetime.now()
start_date = today_date - timedelta(days=7)
end_date = today_date

from_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
to_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

params = {
    "query": query,
    "start_time": from_date_str,
    "end_time": to_date_str,
    "max_results": 100,  # Twitter max per request = 100
    "tweet.fields": "id,text,created_at,author_id,geo"
}

headers = {
    "Authorization": f"Bearer {bearer_token}"
}

all_data = []

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data_list = response.json().get("data", [])
    all_data.extend(data_list)

    print(f"Fetched {len(data_list)} tweets from {from_date_str} to {to_date_str}!")

except requests.exceptions.HTTPError as errh:
    print(f"HTTP Error: {errh}")
except requests.exceptions.ConnectionError as errc:
    print(f"Error Connecting: {errc}")
except requests.exceptions.Timeout as errt:
    print(f"Timeout Error: {errt}")
except requests.exceptions.RequestException as err:
    print(f"Request Error: {err}")

print(f"Total Tweets collected: {len(all_data)}")


import os
import json
from IPython.display import display
import arcgis
from arcgis.gis import GIS
# from arcgis.mapping import WebMap, MapImageLayer, MapImageLayerManager
from arcgis.geometry import Geometry
gis = GIS(url="", username="")



result_list1 = []
for inner_list in all_data[:10]:
    for records in inner_list:
        result_list1.append(records)
        
print(f'Total open records from MCC : {len(result_list1)}')


import pandas as pd

total_df = pd.DataFrame(result_list1)

total_df.columns = total_df.columns.str.lower()

total_df.info()

columns_to_check = ["latitude","longitude",
                    "complainttype"]

# Fill null values with 0 in the specified columns
total_df[columns_to_check] = total_df[columns_to_check].fillna(0)


from arcgis.geometry import Geometry
total_df['geometry'] = total_df.apply(
    lambda row: Geometry({
        "x": float(row['longitude']), 
        "y": float(row['latitude']),  
        "spatialReference": {"wkid": 4326}
    })
)

total_df['complaintsource'].unique()


filtered_df = total_df[
    (total_df['grievancereason'] == 'SEWERAGE OVERFLOWS-ON THE ROAD') & 
    (total_df['can_latitude'] != 0) & 
    (total_df['can_latitude'].notnull()) & 
    (total_df['complaintsource'].isin(['Twitter']))
]

filtered_df

filtered_df.info()

filtered_df

filtered_df.info()

filtered_df.loc[:, 'recvddate'] = pd.to_datetime(filtered_df['recvddate'], format='%d-%b-%Y')

print(filtered_df['recvddate'].unique())


output_file = 'filtered_df.csv'
filtered_df.to_csv(output_file, index=False)

unique_values = filtered_df['recvddate'].unique()
print(unique_values)


import arcgis
from arcgis.gis import GIS
from arcgis.features import FeatureSet, FeatureLayer


filtered_features = []
for _, row in filtered_df.iterrows():
    feature = {
        "geometry": {
            "x": float(row["longitude"]),
            "y": float(row["latitude"]),
            "spatialReference": {"wkid": 4326}
        },
        "attributes": row.drop(["geometry", "latitude", "longitude"]).to_dict()  
    }
    filtered_features.append(feature)
fs = FeatureSet(features=filtered_features)
print(f"FeatureSet contains {len(fs.features)} features.")

for feature in fs.features[:5]:  
    print(feature)

search_results = gis.content.search("", "Feature Layer")

if len(search_results) > 0:
    webmap_item = search_results[0]  
    if hasattr(webmap_item, 'layers') and len(webmap_item.layers) > 0:
        feature_layer = webmap_item.layers[0]
        print("Layer added")

       
        chunk_size = 1000

       
        start = 0
        end = chunk_size

        total_features = len(fs.features)

        while start < total_features:
        
            chunk = FeatureSet(fs.features[start:end])

           
            try:
                edit_result = feature_layer.edit_features(adds=chunk.features)  
                print(f"Edit Result for chunk {start}-{end}: {edit_result}")

                start += chunk_size
                end = min(end + chunk_size, total_features)

            except Exception as e:
                print(f"Error applying edits: {e}")
                break 
    else:
        print("The item does not contain any layers.")
else:
    print("No items found in the search results.")
