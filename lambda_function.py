import json
import urllib.request
import csv
import io
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # 1. Define the API URL (Fetching USD base rates)
    url = "https://open.er-api.com/v6/latest/USD"
    
    try:
        # 2. Fetch data from the currency API
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
        rates = data.get("rates", {})
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # 3. Create a CSV structure in memory
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        # Write headers and data rows
        writer.writerow(["Base_Currency", "Target_Currency", "Rate", "Date"])
        for currency, rate in rates.items():
            writer.writerow(["USD", currency, rate, date_str])
            
        # 4. Upload the CSV data to your Amazon S3 bucket
        s3 = boto3.client('s3')
        
        # CHANGE THIS to your exact bucket name from Step 1
        bucket_name = "my-financial-data-bucket-2026" 
        file_name = f"currency_rates_{date_str}.csv"
        
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully saved {file_name} to S3!")
        }
        
    except Exception as e:
        print(f"Error encountered: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to process rates: {str(e)}")
        }
