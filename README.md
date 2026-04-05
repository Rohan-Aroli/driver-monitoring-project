rohan:

frame_data = {
    "frame": frame,
    "face_bbox": (x, y, w, h),
    "face_detected": True/False
}

pranav:

landmark_data = {
    "left_eye": [(x,y), ...],
    "right_eye": [(x,y), ...]
}

rida:

fatigue_data = {
    "ear": 0.23,
    "eye_closed_duration": 1.4
}

sumanth:

{
  "state": "NORMAL | DROWSY | UNRESPONSIVE",
  "confidence": 0.85
}             


******************************* THE WHOLE FLOW **********************************



           🎥 WEBCAM INPUT
                      │
                      ▼
        ┌────────────────────────────┐
        │   ROHAN — Face Detection   │
        │                            │
        │ Input: frame               │
        │ Output: frame_data         │
        │                            │
        │ {                          │
        │   frame,                   │
        │   face_bbox,               │
        │   face_detected            │
        │ }                          │
        └────────────────────────────┘
                      │
                      ▼
        ┌────────────────────────────┐
        │ PRANAV — Landmark Extract  │
        │                            │
        │ Input: frame_data          │
        │ Output: landmark_data      │
        │                            │
        │ {                          │
        │   left_eye,                │
        │   right_eye                │
        │ }                          │
        └────────────────────────────┘
                      │
                      ▼
        ┌────────────────────────────┐
        │   RIDA — EAR Computation   │
        │                            │
        │ Input: landmark_data       │
        │ Output: fatigue_data       │
        │                            │
        │ {                          │
        │   ear,                     │
        │   eye_closed_duration      │
        │ }                          │
        └────────────────────────────┘
                      │
                      ▼
        ┌────────────────────────────┐
        │ SUMANTH — State Decision   │
        │                            │
        │ Input: fatigue_data        │
        │ Output: driver_state       │
        │                            │
        │ {                          │
        │   state,                   │
        │   confidence              │
        │ }                          │
        └────────────────────────────┘
                      │
                      ▼
        ┌────────────────────────────┐
        │   JSON BRIDGE (FILE I/O)   │
        │                            │
        │ driver_state.json          │
        └────────────────────────────┘
                      │
                      ▼
        ┌────────────────────────────┐
        │   CARLA CONTROL MODULE     │
        │                            │
        │ Reads state                │
        │                            │
        │ IF UNRESPONSIVE → brake    │
        │ ELSE → autopilot           │
        └────────────────────────────┘
                      │
                      ▼
                🚗 VEHICLE BEHAVIOR
         (Slow down → Stop safely)
