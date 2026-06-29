import cv2
import time
import uuid

from supabase_client import supabase

last_frame_upload = 0
UPLOAD_INTERVAL = 1.0  # seconds
last_uploaded_url = None


def upload_driver_frame(frame):
    """
    Upload driver frame to Supabase Storage.

    Returns:
        str: Public URL of uploaded frame
        None: If upload fails
    """

    global last_frame_upload
    global last_uploaded_url

    current_time = time.time()

    # Throttle uploads

    if current_time - last_frame_upload < UPLOAD_INTERVAL:
        return last_uploaded_url

    try:
        # ---------------------------------
        # COMPRESS FRAME
        # ---------------------------------
        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, 55]
        )

        if not success:
            print("[FRAME ERROR] JPEG encoding failed")
            return None

        frame_bytes = buffer.tobytes()

        # ---------------------------------
        # GENERATE UNIQUE FILE NAME
        # ---------------------------------
        filename = (
            f"driver_frame_"
            f"{int(current_time)}_"
            f"{uuid.uuid4().hex[:8]}.jpg"
        )

        bucket_name = "driver-feed"

        # ---------------------------------
        # UPLOAD TO STORAGE
        # ---------------------------------
        response = (
            supabase.storage
            .from_(bucket_name)
            .upload(
                path=filename,
                file=frame_bytes,
                file_options={
                    "content-type": "image/jpeg",
                    "upsert": "false"
                }
            )
        )

        # ---------------------------------
        # GET PUBLIC URL
        # ---------------------------------
        public_url = (
            supabase.storage
            .from_(bucket_name)
            .get_public_url(filename)
        )
        last_uploaded_url = public_url

        print(
            f"[FRAME UPLOAD SUCCESS] {filename}"
        )

        last_frame_upload = current_time

        return public_url

    except Exception as e:

        error_message = str(e)

        if "Bucket not found" in error_message:
            print(
                "[FRAME UPLOAD ERROR] "
                "Supabase bucket 'driver-frames' "
                "does not exist."
            )

        elif "Duplicate" in error_message:
            print(
                "[FRAME UPLOAD ERROR] "
                "File already exists."
            )

        else:
            print(
                f"[FRAME UPLOAD ERROR]: {e}"
            )

        return None