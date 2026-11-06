# youtube-videos-engineering

<img width="1196" height="896" alt="image" src="https://github.com/user-attachments/assets/f991dab7-22f8-4cff-a5d3-36ddac5dfbaf" />

A cloud-native, automated engineering pipeline designed to archive high-definition YouTube videos directly into AWS S3 storage using Python.

## 🚀 Overview

This repository demonstrates modern software engineering principles applied to media handling and cloud integration. It features a reliable automated script that extracts YouTube video streams, processes/merges high-quality files locally, streams them to AWS S3 securely, and performs automated disk-space cleanups.

## 🛠️ Tech Stack & System Requirements

- **Language:** Python 3.10+
- **Media Engine:** [FFmpeg](https://ffmpeg.org) (Required for stitching HD video and high-fidelity audio streams together)
- **Cloud Provider:** Amazon Web Services (AWS S3)
- **Key Libraries:** `yt-dlp`, `boto3`, `python-dotenv`

### System Dependency Installation

Before running the application, make sure `ffmpeg` is available in your system path:

- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`
- **Windows:** Download from official website and add the `/bin` folder to your System Environment variables (`PATH`).

## ⚙️ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com
cd youtube-videos-engineering
```

### 2. Set up a virtual environment and install packages
```bash
python -bin/venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables Setup
Create a `.env` file in the root directory using the template:
```bash
cp .env.example .env
```
Fill in your AWS parameters:
```env
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
```

### 4. Execute the pipeline
```bash
python main.py
```

## 🏗️ Core Architecture Flow

1. **Extraction:** `yt-dlp` fetches metadata and isolates the absolute highest-resolution format available.
2. **Processing:** Local `ffmpeg` instance merges independent modern video/audio codecs seamlessly into an optimal `.mp4` format.
3. **Transmission:** `boto3` initiates an upload process pointing towards your designated S3 bucket directory.
4. **Cleanup:** Post-upload garbage collection fires immediately to remove high-weight temp files, keeping disk usage perfectly steady.
