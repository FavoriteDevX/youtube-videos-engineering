import os
import sys
import logging
from pathlib import Path
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
import yt_dlp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

# Initialize S3 Client
try:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
except Exception as e:
    logger.error(f"Failed to initialize S3 client: {e}")
    sys.exit(1)


def download_youtube_video(video_url: str, output_dir: str = "downloads") -> str:
    """
    Downloads a YouTube video in the best available quality using yt-dlp.
    Ensures output is in MP4 format.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Template names the file using its YouTube ID to avoid special character issues
    outtmpl = os.path.join(output_dir, "%(id)s.%(ext)s")
    
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": outtmpl,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
    }
    
    logger.info(f"Starting download for URL: {video_url}")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=True)
            video_id = info_dict.get("id", "video")
            # yt-dlp might change extension during merge, we find the actual file created
            downloaded_file = os.path.join(output_dir, f"{video_id}.mp4")
            
            if os.path.exists(downloaded_file):
                logger.info(f"Download complete: {downloaded_file}")
                return downloaded_file
            else:
                raise FileNotFoundError("Merged MP4 file could not be found.")
                
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            raise


def upload_to_s3(local_file_path: str, bucket_name: str, s3_key: str = None) -> bool:
    """
    Uploads a local file to a specified AWS S3 bucket.
    """
    if not bucket_name:
        logger.error("S3_BUCKET_NAME environment variable is missing.")
        return False

    if s3_key is None:
        s3_key = os.path.basename(local_file_path)

    logger.info(f"Uploading {local_file_path} to s3://{bucket_name}/{s3_key}...")
    
    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_key)
        logger.info("Upload successful!")
        return True
    except FileNotFoundError:
        logger.error(f"The file {local_file_path} was not found.")
        return False
    except NoCredentialsError:
        logger.error("AWS credentials not found or invalid.")
        return False
    except ClientError as e:
        logger.error(f"AWS S3 Client Error: {e}")
        return False


def main():
    # Example video URL (change this to test)
    target_url = "https://youtube.com"
    
    local_file = None
    try:
        # 1. Download video
        local_file = download_youtube_video(target_url)
        
        # 2. Upload to Cloud Storage
        s3_folder_prefix = "youtube-archive/"
        s3_dest_key = f"{s3_folder_prefix}{os.path.basename(local_file)}"
        
        success = upload_to_s3(local_file, S3_BUCKET, s3_dest_key)
        
        # 3. Cleanup local storage (Crucial for Cloud Engineering / Docker environments)
        if success and local_file and os.path.exists(local_file):
            os.remove(local_file)
            logger.info(f"Cleaned up local file: {local_file}")
            
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        if local_file and os.path.exists(local_file):
            os.remove(local_file)


if __name__ == "__main__":
    main()
