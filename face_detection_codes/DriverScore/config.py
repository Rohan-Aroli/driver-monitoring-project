# ==========================================
# SCORING CONFIGURATION
# ==========================================

NORMALIZATION_VERSION = "1.0"


# ------------------------------------------
# Driver Score weights
# ------------------------------------------

DRIVER_SCORE_WEIGHTS = {
    "fatigue": 0.35,
    "safety": 0.25,
    "attention": 0.15,
    "experience": 0.15,
    "health": 0.10,
}


# ------------------------------------------
# Fatigue weights
# ------------------------------------------

FATIGUE_WEIGHTS = {
    "perclos": 0.30,
    "microsleep": 0.25,
    "yawn": 0.15,
    "drowsiness": 0.20,
    "unresponsive": 0.10,
}


MICROSLEEP_WEIGHTS = {
    "rate": 0.50,
    "average_duration": 0.30,
    "maximum_duration": 0.20,
}


YAWN_WEIGHTS = {
    "rate": 0.70,
    "duration": 0.30,
}


# ------------------------------------------
# Attention
# ------------------------------------------

ATTENTION_WEIGHTS = {
    "distraction_rate": 0.45,
    "distracted_time": 0.45,
    "blink": 0.10,
}


# ------------------------------------------
# Safety
# ------------------------------------------

SAFETY_WEIGHTS = {
    "emergency": 0.40,
    "braking": 0.25,
    "acceleration": 0.20,
    "steering": 0.15,
}


# ------------------------------------------
# PERCLOS
# ------------------------------------------

PERCLOS_LOW = 0.125
PERCLOS_HIGH = 0.30

# IMPORTANT:
# This is configurable because PERCLOS
# definitions/thresholds vary.


# ------------------------------------------
# Recency
# ------------------------------------------

RECENCY_LAMBDA = 0.01


# ------------------------------------------
# Critical-event rules
# ------------------------------------------

ONE_UNRESPONSIVE_SCORE_CAP = 75.0
REPEATED_CRITICAL_SCORE_CAP = 50.0


# ------------------------------------------
# Confidence
# ------------------------------------------

LOW_CONFIDENCE_HOURS = 5.0
MEDIUM_CONFIDENCE_HOURS = 25.0
HIGH_CONFIDENCE_HOURS = 50.0