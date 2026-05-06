import boto3
import pandas as pd
import io
from datetime import datetime

# --- CONFIGURATION ---
MINIO_CONF = {
    "endpoint_url": "http://127.0.0.1:9000",
    "aws_access_key_id": "minioadmin",
    "aws_secret_access_key": "minioadmin",
}

s3 = boto3.client('s3', **MINIO_CONF)

def run_medallion_pipeline():
    try:
        # --- PHASE 1: BRONZE TO SILVER ---
        print("--- Phase 1: Extracting metadata from Bronze ---")
        bronze_files = s3.list_objects_v2(Bucket='bronze')
        
        if 'Contents' not in bronze_files:
            print("Bronze bucket is empty.")
            return

        metadata_list = []

        for obj in bronze_files['Contents']:
            key = obj['Key']
            ext = key.split('.')[-1].lower() if '.' in key else 'no_ext'

            # Tambahan: parsing nama file
            try:
                name_only = key.split('.')[0]
                parts = name_only.split('_')

                nrp = parts[0]
                student = parts[1]
                assignment = parts[2]
            except:
                print(f"Format filename salah: {key}")
                nrp, student, assignment = None, None, None

            metadata_list.append({
                "file_name": key,
                "NRP": nrp,
                "Student_Name": student,
                "Assignment_Title": assignment,
                "size_bytes": obj['Size'],
                "upload_time": obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S"),
                "extension": ext
            })

        # Save to local CSV
        df_silver = pd.DataFrame(metadata_list)
        local_csv = "metadata_inventory.csv"
        df_silver.to_csv(local_csv, index=False)
        
        # Upload to Silver
        s3.upload_file(local_csv, 'silver', local_csv)
        print("Successfully uploaded inventory to Silver.")

        # --- PHASE 2: SILVER TO GOLD ---
        print("\n--- Phase 2: Converting Silver CSV to Gold Parquet ---")

        csv_obj = s3.get_object(Bucket='silver', Key=local_csv)
        df_gold = pd.read_csv(io.BytesIO(csv_obj['Body'].read()))

        # Tambahan: Storage Category
        df_gold['Storage_Category'] = df_gold['size_bytes'].apply(
            lambda x: 'Large' if x > 1024 * 1024 else 'Small'
        )

        # Convert ke Parquet
        parquet_buffer = io.BytesIO()
        df_gold.to_parquet(parquet_buffer, index=False)

        gold_filename = f"catalog_{datetime.now().strftime('%Y%m%d')}.parquet"
        s3.put_object(
            Bucket='gold',
            Key=gold_filename,
            Body=parquet_buffer.getvalue()
        )

        print(f"Successfully uploaded {gold_filename} to Gold.")

        # --- PHASE 3: ANALYTICS ---
        print("\n--- Phase 3: Analysis ---")

        # 1. Total per extension
        print("\nTotal files per extension:")
        print(df_gold['extension'].value_counts())

        # 2. Student dengan file Large
        print("\nStudents with Large files:")
        large_students = df_gold[df_gold['Storage_Category'] == 'Large']['Student_Name']
        print(large_students.dropna().unique())

        # 3. Average size
        avg_size = df_gold['size_bytes'].mean()
        print(f"\nAverage file size: {avg_size / 1024:.2f} KB")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    run_medallion_pipeline()