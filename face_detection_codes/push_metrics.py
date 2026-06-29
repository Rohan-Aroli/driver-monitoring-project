from supabase_client import supabase
import time

last_push_time = 0
last_payload = {}


def push_driver_metrics(
        metrics,
        driver_state,
        frame_url=None):

    global last_push_time
    global last_payload

    current_time = time.time()

    # Update only once every second
    if current_time - last_push_time < 1:
        return

    try:
        payload = {
            "ear": float(
                metrics.get("ear", 0)
            ),

            "perclos": float(
                metrics.get("perclos", 0)
            ),

            "blink_rate": int(
                metrics.get("blink_rate", 0)
            ),

            "driver_state": str(
                driver_state
            ),

            "fatigue_score": float(
                metrics.get(
                    "drowsiness_score",
                    0
                )
            ),

            "eye_closure_duration": float(
                metrics.get(
                    "avg_closure_duration",
                    0
                )
            ),

            "updated_at": int(current_time)
        }

        if frame_url:
            payload["frame_url"] = frame_url

        # Skip duplicate updates
        compare_payload = payload.copy()
        compare_payload.pop("updated_at", None)

        if compare_payload == last_payload:
            return

        last_payload = compare_payload

        response = (
            supabase
            .table("live_driver_state")
            .update(payload)
            .eq("id", 1)
            .execute()
        )

        print(
            "[SUPABASE LIVE ROW UPDATED]"
        )

        last_payload = compare_payload.copy()
        last_push_time = current_time

    except Exception as e:
        print(
            f"[SUPABASE ERROR]: {e}"
        )