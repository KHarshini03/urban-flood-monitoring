#A feature layer from available tweets should be prepared after extrating from API 
#extracting from HMWSSB database API.
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime


url = "" 


basic_auth = HTTPBasicAuth('')


all_data = []
#an example date 
start_date = datetime(2024, 1, 1)
end_date   = datetime(2025, 1, 1)


# Format the date in the required format for the API
from_date_str = start_date.strftime("%d-%b-%Y")
to_date_str = end_date.strftime("%d-%b-%Y")

params = {
    "FromDate": from_date_str,
    "ToDate": to_date_str,
}

try:
    # Make the GET request
    response = requests.get(url, auth=basic_auth, data=params)
    
    # Check if the request was successful (status code 200)
    response.raise_for_status()

    # Access the list within the JSON response
    data_list = response.json()["Mydatatable1"]
    
    # Append the data to the all_data list
    all_data.append(data_list)

    print(f'Request for {from_date_str} to {to_date_str} was successful!')

except requests.exceptions.HTTPError as errh:
    print(f'HTTP Error: {errh}')

except requests.exceptions.ConnectionError as errc:
    print(f'Error Connecting: {errc}')

except requests.exceptions.Timeout as errt:
    print(f'Timeout Error: {errt}')

except requests.exceptions.RequestException as err:
    print(f'Request Error: {err}')

# Print or use the collected data as needed
print("All data fetched successfully!")



# converting into data frame and that to csv
result_list = []
for inner_list in all_data[:10]:
    for records in inner_list:
        result_list.append(records)
        
print(f'Total open records from MCC : {len(result_list)}')


import pandas as pd

total_df = pd.DataFrame(result_list)

total_df.columns = total_df.columns.str.lower()

output_file = 'filtered_df.csv'
total_df.to_csv(output_file, index=False)