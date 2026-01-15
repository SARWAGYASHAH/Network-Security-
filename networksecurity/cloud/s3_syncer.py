import os

class S3Sync:
    def sync_folder_to_s3(self, folder, aws_bucket_url):
        command = f"aws s3 sync {folder} {aws_bucket_url} --region ap-south-1"
        
        print(f"🚀 Running command: {command}")
        exit_code = os.system(command)

        if exit_code != 0:
            raise Exception("❌ S3 sync to bucket failed")
        else:
            print("✅ S3 sync to bucket completed successfully")

    def sync_folder_from_s3(self, folder, aws_bucket_url):
        command = f"aws s3 sync {aws_bucket_url} {folder} --region ap-south-1"
        
        print(f"🚀 Running command: {command}")
        exit_code = os.system(command)

        if exit_code != 0:
            raise Exception("❌ S3 sync from bucket failed")
        else:
            print("✅ S3 sync from bucket completed successfully")
