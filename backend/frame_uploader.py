import cv2
import os
import time
from supabase import create_client

SUPABASE_URL = "https://fmeqoylucfimorzhncwv.supabase.co"
SUPABASE_KEY = "sb_publishable_yznlwBM_kMVNuyPOBaerIg_4tMWpRAO"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_driver_frame(frame):
    try:
        filename = "latest_driver.jpg"

        # Save current frame temporarily
        cv2.imwrite(filename, frame)

        with open(filename, "rb") as f:
            file_data = f.read()

        # Upload and overwrite existing file
        supabase.storage.from_("driver-feed").upload(
            filename,
            file_data,
            {
                "content-type": "image/jpeg",
                "upsert": "true"
            }
        )

        # Get public URL
        public_url = supabase.storage.from_("driver-feed").get_public_url(filename)

        # Update single row
        supabase.table("latest_driver_frame").update({
            "frame_url": public_url
        }).eq("id", 1).execute()

        print("frame updated")

        os.remove(filename)

    except Exception as e:
        print("upload failed:", e)