# Driver Health Monitoring & Automated Parking

## Driver Temporal Analysis & Scoring System

> **Team README**  *

> Covers system architecture, design decisions, temporal analysis methodology, database schemas, scoring engines, mathematical formulations, and execution flows.  *

> *Note: This specification document intentionally excludes application implementation code.**

---

## 1. Project Overview

The project is a **Driver Health Monitoring and Fleet Safety System** designed to continuously monitor a driver's physiological and behavioral indicators, detect fatigue and distraction, record vehicle behavior and safety events, and generate a **long-term Driver Score**.

The system is engineered for logistics and fleet environments where scoring informs:
* **Driver assignment** & scheduling
* **Route suitability** matching
* **Fatigue-risk** proactive assessment
* **Safety-performance** benchmarking
* **Long-term driver reliability** indexing
* **Pattern monitoring** for repeated hazardous behaviors

```

┌─────────────────────────────────────────────────────────────────────────────┐

│                               CORE PRINCIPLE                                │

│                                                                             │

│   "Real-time signals are not the same thing as long-term performance."      │

│                                                                             │

│   Raw metrics (EAR, MAR, Head Pose) are instantaneous sensor observations.  │

│   They must be converted into temporal events and historical aggregates     │

│   prior to computing risk indices and score vectors.                        │

└─────────────────────────────────────────────────────────────────────────────┘

```

---

## 2. High-Level System Flow

```text

                             ┌──────────────────┐

                             │      CAMERA      │

                             └────────┬─────────┘

                                      │

                                      ▼

                           ┌─────────────────────┐

                           │   Face Detection    │

                           └──────────┬──────────┘

                                      │

                 ┌────────────────────┼────────────────────┐

                 ▼                    ▼                    ▼

               EAR                   MAR               HEAD POSE

                 │                    │                    │

                 ▼                    ▼                    ▼

          ┌─────────────┐      ┌─────────────┐      ┌─────────────┐

          │ Drowsiness  │      │    Yawn     │      │ Attention / │

          │  Detector   │      │  Detector   │      │ Distraction │

          └──────┬──────┘      └──────┬──────┘      └──────┬──────┘

                 │                    │                    │

                 └────────────────────┼────────────────────┘

                                      ▼

                           ┌─────────────────────┐

                           │    Driver State     │

                           │     Classifier      │

                           └──────────┬──────────┘

                                      │

                                      ▼

                           ┌─────────────────────┐

                           │ Real-Time Dashboard │

                           └──────────┬──────────┘

                                      │

                 ┌────────────────────┼────────────────────┐

                 ▼                    ▼                    ▼

          ┌─────────────┐      ┌─────────────┐      ┌─────────────┐

          │   Driver    │      │   Vehicle   │      │  Emergency  │

          │   Metrics   │      │   Metrics   │      │   Events    │

          └──────┬──────┘      └──────┬──────┘      └──────┬──────┘

                 │                    │                    │

                 └────────────────────┼────────────────────┘

                                      │

                                  [TRIP END]

                                      │

                                      ▼

                           ┌─────────────────────┐

                           │    Trip Feature     │

                           │     Extraction      │

                           └──────────┬──────────┘

                                      │

                                      ▼

                           ┌─────────────────────┐

                           │ Historical Feature  │

                           │     Aggregation     │

                           └──────────┬──────────┘

                                      │

                                      ▼

                           ┌─────────────────────┐

                           │    Normalization    │

                           │      (0 - 100)      │

                           └──────────┬──────────┘

                                      │

                 ┌────────────────────┼────────────────────┐

                 ▼                    ▼                    ▼

          ┌─────────────┐      ┌─────────────┐      ┌─────────────┐

          │   FATIGUE   │      │   SAFETY    │      │  ATTENTION  │

          │  RESILIENCE │      │ PERFORMANCE │      │   METRICS   │

          └──────┬──────┘      └──────┬──────┘      └──────┬──────┘

                 │                    │                    │

                 └────────────────────┼────────────────────┘

                                      │

                                      ▼

                           ┌─────────────────────┐

                           │ Experience + Health │

                           └──────────┬──────────┘

                                      │

                                      ▼

                           ┌─────────────────────┐

                           │ Driver Score Engine │

                           └──────────┬──────────┘

                                      │

                                      ▼

                           ┌─────────────────────┐

                           │   Critical Event    │

                           │     Constraints     │

                           └──────────┬──────────┘

                                      │

                                      ▼

                           ╔═════════════════════╗

                           ║ FINAL DRIVER SCORE  ║

                           ╚══════════╦══════════╝

                                      │

                                      ▼

                             Driver Score History

```

---

## 3. Current Monitoring Pipeline

```text

   [ Raw Input Frame ]

            │

            ▼

   [ Face Detection ]

            │

            ▼

   [ Landmark Extraction ] (Eye / Mouth Regions)

            │

            ├─► Eye Aspect Ratio (EAR)

            ├─► Mouth Aspect Ratio (MAR)

            ├─► Head Pose Estimation (Pitch, Yaw, Roll)

            ├─► PERCLOS Computation

            ├─► Blink Frequency Analysis

            ├─► Yawn State Classification

            └─► Microsleep Duration Tracking

            │

            ▼

   [ Enhanced Driver State Classifier ]

            │

            ▼

   ┌─────────────────────────────────────────────────────────┐

   │ NORMAL  │  DROWSY  │  UNRESPONSIVE  │  UNKNOWN / NO\_FACE │

   └─────────────────────────────────────────────────────────┘

```

### Integrated Submodules

* **Drowsiness Detector**: Evaluates eye closure persistence and frequency.
* **Mouth Landmark Extractor**: Pinpoints inter-lip coordinates across spatial frames.
* **MAR Calculator**: Derives real-time ratio of vertical vs. horizontal lip expansion.
* **Yawn Detector**: Categorizes prolonged high-MAR states as distinct yawn events.
* **Microsleep Detector**: Catches continuous bilateral eye closure events.
* **Head Pose Estimator**: Computes rotational pitch, yaw, and roll vectors.
* **Baseline Calibration**: Calibrates individualized physical threshold baselines.
* **Driver Manager**: Handles state bindings and active driver profiles.
* **Driver State Classifier**: Orchestrates unified multi-signal status outputs.
* **Metric Pushing**: Ingests and routes high-frequency timeseries batches.
* **Incident-Frame Handling**: Persists contextual imagery for anomalous windows.

---

## 4. Driver Monitoring Signals

### 4.1 EAR (Eye Aspect Ratio)

Determines eyelid closure state on a continuous coordinate scale.

```text

[ EAR Stream ] ──► [ Closure Gate ] ──► [ Event Tagging ] ──► [ Historical Stats ] ──► [ Fatigue Score ]

```

> **Architecture Constraint**: EAR is a real-time observation. It must never directly scale the final long-term score without going through temporal feature extraction.*

---

### 4.2 PERCLOS (Percentage of Eye Closure)

Represents the proportion of time eyes remain closed over a specified moving baseline.

```

┌─────────────────────────────── Key PERCLOS Features ───────────────────────────────┐

│ • Average PERCLOS            : Mean percentage over entire trip duration          │

│ • High-PERCLOS Time          : Cumulative seconds spent in elevated state          │

│ • High-PERCLOS Ratio         : % of operational time crossing hazard threshold     │

│ • PERCLOS Trend Curve        : Derivative trajectory of fatigue onset             │

└────────────────────────────────────────────────────────────────────────────────────┘

```

> ⚠️ **Important Validation Notice***

> PERCLOS implementation within this pipeline utilizes a smoothed window over rolling frame counts. Ensure calibration aligns with project definitions rather than generic academic assumptions.*

---

## 5. Blink Rate

Blink frequency functions strictly as a supporting contextual indicator.

```text

  [ Confounding Factors ]           [ Signal Transformation Pipeline ]

┌───────────────────────────┐

│ • Dynamic cabin lighting  │        ┌─────────────────────────┐

│ • Ocular dry conditions   │        │   Current Blink Rate    │

│ • Contact lens usage      │        └────────────┬────────────┘

│ • Vocal conversation      │                     ▼

│ • Cognitive focus load    │        ┌─────────────────────────┐

│ • Inter-driver variance   │        │ Comparison to Baseline  │

└───────────────────────────┘        └────────────┬────────────┘

                                                  ▼

                                     ┌─────────────────────────┐

                                     │  Normalized Deviation   │

                                     └────────────┬────────────┘

                                                  ▼

                                     ┌─────────────────────────┐

                                     │   Blink Score Penalty   │

                                     └─────────────────────────┘

```

### Baseline Deviation Formula

$$
\text{BlinkDeviation}
=
\frac{\left|\text{CurrentBlinkRate} - \text{BaselineBlinkRate}\right|}
{\text{BaselineBlinkRate}}
$$
---

## 6. Yawn Detection

### Metrics Provided

* Real-time **MAR**
* Active **Yawn State** boolean flag
* Current **Yawn Duration**
* Trip-level **Total Yawn Count**
* Mean **Yawn Duration**

### Historical Exposure Formula

$$
\text{YawnRate}
=
\frac{\text{TotalYawns}}{\text{DrivingHours}}
$$

```

┌───────────────────────────── Secondary Features ─────────────────────────────┐

│  • Average Yawn Duration (seconds)                                          │

│  • Long-Yawn Rate (Occurrences > Critical Duration / Driving Hours)          │

└─────────────────────────────────────────────────────────────────────────────┘

```

---

## 7. Microsleep Detection

Tracks critical lapse-of-consciousness events marked by prolonged eyelid closure.

### Temporal Feature Engine

$$
\text{MicrosleepRate}
=
\frac{\text{MicrosleepCount}}{\text{DrivingHours}}
$$
```

┌───────────────────────────────── Metric Scope ─────────────────────────────────┐

│ • Mean Microsleep Duration   : Tracks average sustained length per incident    │

│ • Max Microsleep Duration    : High-impact anchor tracking absolute peak risk  │

└────────────────────────────────────────────────────────────────────────────────┘

```

> **Design Note**: A single prolonged microsleep window carries higher severity weighting than multiple isolated micro-closures.*

---

## 8. Driver State Classification

```text

┌──────────────┐     ┌──────────────┐     ┌──────────────────┐     ┌─────────────┐

│    NORMAL    │ ──► │    DROWSY    │ ──► │   UNRESPONSIVE   │ ──► │   UNKNOWN   │

└──────────────┘     └──────────────┘     └──────────────────┘     └─────────────┘

```

### Historical Aggregation Derivations

* **Drowsy Time %**: Total operational duration spent within the Drowsy state.
* **Drowsy Episode Count & Rate**: Total distinct episodes per operating hour.
* **Duration Metrics**: Mean and maximum sustained duration of drowsy episodes.
* **Unresponsive Metrics**: Absolute frequency and hourly rate of critical lapses.

### Drowsy Proportion Formula

$$
\text{DrowsyTime\%}
=
\left(
\frac{\text{DrowsySeconds}}{\text{TotalDrivingSeconds}}
\right)
\times 100
$$

---

## 9. Important Classifier Issue

Current multi-stage classifiers handle varying combinations of inputs that require distinct semantic thresholds:

```text

[ Earlier Architecture ]         [ Enhanced Pipeline ]

 • Microsleep: \~2 seconds         • Missing Face / Occlusion

 • Unresponsive: \~5 seconds       • Missing Eyes / Gaze Loss

                                  • Eyelid Closure Persistence

                                  • Microsleep Event

                                  • Drowsiness Progression

```

```

┌─────────────────────────────────────────────────────────────────────────────┐

│                            STATE CLASSIFICATION HIERARCHY                   │

│                                                                             │

│   [ Normal ]                                                                │

│       │                                                                     │

│       ▼                                                                     │

│   [ Prolonged Eye Closure ]                                                 │

│       │                                                                     │

│       ▼                                                                     │

│   [ Microsleep / Severe Drowsiness ]                                        │

│       │                                                                     │

│       ▼                                                                     │

│   [ Unresponsive State ]                                                    │

│                                                                             │

│   Semantic Rule: A brief microsleep event must NOT immediately categorize   │

│   the driver under an Unresponsive classification without duration check.   │

└─────────────────────────────────────────────────────────────────────────────┘

```

---

## 10. Head Pose and Attention

```text

   Head Pose Signals (Pitch, Yaw, Roll)

                   │

                   ▼

   Comparison Against Personal Baseline

                   │

                   ▼

   Angular Deviation Calculation

                   │

                   ▼

       Sustained Deviation Window?

             │           │

            NO          YES

             │           │

             ▼           ▼

        [ Ignore ]   [ Distraction Event ]

```

### Historical Formulations

$$
\text{DistractionRate}
=
\frac{\text{DistractionCount}}{\text{DrivingHours}}
$$

$$
\text{DistractedTime\%}
=
\left(
\frac{\text{TotalDistractedSeconds}}{\text{TotalDrivingSeconds}}
\right)
\times 100
$$

```

┌──────────────────────── Additional Attention Features ────────────────────────┐

│  • Distraction Event Count          • Mean Distraction Episode Duration      │

└──────────────────────────────────────────────────────────────────────────────┘

```

---

## 11. Vehicle Behavior

### Telemetry Signals Tracked

* \`Speed\` · \`Throttle\` · \`Brake\` · \`Steering Angle\` · \`Hazard Lights\` · \`Vehicle State\`

### Extracted Safety Features

* **Harsh Braking Event Rate**
* **Rapid Acceleration Event Rate**
* **Steering Anomaly / Swerve Rate**
* **Overspeed Exposure Profile**
* **Emergency Incidents Count**
* **Severity-Weighted Safety Violations**

> ⚠️ **Implementation Notice***

> Operational thresholds for harsh kinematics must remain dynamic until raw CAN-bus and accelerometer units are validated. Emergency telemetry events must not be classified as collisions without multi-sensor verification.*

---

## 12. Database Architecture

```text

                      ┌──────────────────────┐

                      │       drivers        │

                      └──────────┬───────────┘

                                 │

                 ┌───────────────┴───────────────┐

                 ▼                               ▼

      ┌──────────────────────┐        ┌──────────────────────┐

      │    driver\_metrics    │        │   vehicle\_metrics    │

      └──────────┬───────────┘        └──────────┬───────────┘

                 │                               │

                 └───────────────┬───────────────┘

                                 ▼

                      ┌──────────────────────┐

                      │  Temporal Analysis   │

                      └──────────┬───────────┘

                                 ▼

                      ┌──────────────────────┐

                      │     Driver Score     │

                      └──────────────────────┘

  ┌──────────────────────┐                 ┌──────────────────────┐

  │   emergency\_events   │                 │  live\_driver\_state   │

  └──────────┬───────────┘                 └──────────┬───────────┘

             ▼                                        ▼

  ┌──────────────────────┐                 ┌──────────────────────┐

  │   Safety Analysis    │                 │ Real-Time Dashboard  │

  └──────────────────────┘                 └──────────────────────┘

  ┌──────────────────────┐                 ┌──────────────────────┐

  │    driver\_frames     │                 │ latest\_driver\_frame  │

  └──────────┬───────────┘                 └──────────┬───────────┘

             ▼                                        ▼

  ┌──────────────────────┐                 ┌──────────────────────┐

  │ Frame Storage / S3   │                 │ Active View Buffer   │

  └──────────────────────┘                 └──────────────────────┘

```

---

## 13. Existing Database Tables

| Table Name | Primary Role | Core Column Scope |
|---|---|---|
| `drivers` | Driver Profiles & Assignment | `id`, `name`, `license`, `vehicle`, `plate`, `route`, `origin`, `destination`, `shift_info`, `notes`, `created_at` |
| `driver_metrics` | High-Frequency Driver Timeseries | `ear`, `perclos`, `blink_rate`, `driver_state`, `fatigue_score`, `head_pose`, `eye_closure_duration`, `timestamp` |
| `vehicle_metrics` | Continuous Telemetry Ingestion | `speed`, `throttle`, `brake`, `steering`, `hazard_lights`, `vehicle_state`, `timestamp` |
| `emergency_events` | Discrete Safety Violations | `event_type`, `severity`, `message`, `resolved_status`, `timestamp` |
| `live_driver_state` | Low-Latency Dashboard Buffer | `driver_id`, `state`, `last_active_timestamp` |
| `driver_frames` | Incident Video Reference Store | `frame_url`, `event_ref`, `captured_at` |
| `latest_driver_frame` | Edge Frame Single-Slot Buffer | `frame_data`, `driver_ref`, `updated_at` |
---

## 14. Major Database Issue

```

┌─────────────────────────────────────────────────────────────────────────────┐

│                           CRITICAL SCHEMA DEFECT                            │

│                                                                             │

│   Existing historical records lack strict bindings to composite keys:        │

│                           [ driver\_id, trip\_id ]                            │

│                                                                             │

│   Without foreign keys explicitly tied to individual trips, aggregation     │

│   pipelines cannot segment metric timelines across multi-driver assets.     │

└─────────────────────────────────────────────────────────────────────────────┘

```

### Required Migration Schema Fix

Inject required identity columns across all timeseries tables:

- `driver_metrics` → add `driver_id`, `trip_id`
- `vehicle_metrics` → add `driver_id`, `trip_id`
- `emergency_events` → add `driver_id`, `trip_id`

---

## 15. Trip Concept

The fundamental atom of temporal analysis is an isolated **Trip Session**.

```text
Driver Profile
│
├── Trip #001
│   ├── trip_id, driver_id
│   ├── trip_start, trip_end, duration
│   │
│   ├── driver_metrics
│   ├── vehicle_metrics
│   └── emergency_events
│
├── Trip #002
│   ├── trip_id, driver_id
│   ├── trip_start, trip_end, duration
│   │
│   ├── driver_metrics
│   ├── vehicle_metrics
│   └── emergency_events
│
└── Trip #003
    ├── trip_id, driver_id
    ├── trip_start, trip_end, duration
    │
    ├── driver_metrics
    ├── vehicle_metrics
    └── emergency_events
```

---

## 16. Why Trip-Level Analysis?

Unweighted raw event counts skew operational risk assessments:

```text

┌─────────────────────────────────────────────────────────────────────────────┐

│ [ Driver A ] : 10 Yawns over a 2-Hour Window   ──► 5.0 Yawns/Hour  (HIGH)   │

│ [ Driver B ] : 10 Yawns over a 10-Hour Window  ──► 1.0 Yawns/Hour  (LOW)    │

└─────────────────────────────────────────────────────────────────────────────┘

```

### Rate Standardization

$$
\text{YawnRate}
=
\frac{\text{YawnCount}}{\text{DrivingHours}}
$$

$$
\text{MicrosleepRate}
=
\frac{\text{MicrosleepCount}}{\text{DrivingHours}}
$$

$$
\text{DistractionRate}
=
\frac{\text{DistractionCount}}{\text{DrivingHours}}
$$
---

## 17. Temporal Analysis Architecture

```text

   ┌───────────────────────────┐

   │      RAW SENSOR DATA      │

   └─────────────┬─────────────┘

                 ▼

   ┌───────────────────────────┐

   │     TRIP SEGMENTATION     │

   └─────────────┬─────────────┘

                 ▼

   ┌───────────────────────────┐

   │   TRIP TEMPORAL FEATURES  │

   └─────────────┬─────────────┘

                 ▼

   ┌───────────────────────────┐

   │  HISTORICAL AGGREGATION   │

   └─────────────┬─────────────┘

                 ▼

   ┌───────────────────────────┐

   │    HISTORICAL FEATURES    │

   └─────────────┬─────────────┘

                 ▼

   ┌───────────────────────────┐

   │       NORMALIZATION       │

   └─────────────┬─────────────┘

                 ▼

   ┌───────────────────────────┐

   │     COMPONENT SCORES      │

   └─────────────┬─────────────┘

                 ▼

   ╔═══════════════════════════╗

   ║    FINAL DRIVER SCORE     ║

   ╚═══════════════════════════╝

```

---

## 18. Trip Temporal Features

```

┌─────────────────────────────────────────────────────────────────────────────┐

│ FATIGUE FEATURES                                                            │

├─────────────────────────────────────────────────────────────────────────────┤

│ • Average PERCLOS                     • Drowsy Time %                       │

│ • High-PERCLOS %                      • Drowsy Episode Rate                 │

│ • Yawn Rate (events/hr)               • Average Drowsy Duration             │

│ • Average Yawn Duration               • Maximum Drowsy Duration             │

│ • Microsleep Rate (events/hr)         • Unresponsive Event Frequency        │

│ • Average Microsleep Duration         • Unresponsive Event Rate             │

│ • Maximum Microsleep Duration                                               │

├─────────────────────────────────────────────────────────────────────────────┤

│ ATTENTION FEATURES                                                          │

├─────────────────────────────────────────────────────────────────────────────┤

│ • Distraction Rate                    • Average Distraction Episode Time    │

│ • Distracted Time %                   • Baseline Blink Deviation            │

├─────────────────────────────────────────────────────────────────────────────┤

│ SAFETY FEATURES                                                             │

├─────────────────────────────────────────────────────────────────────────────┤

│ • Critical Emergency Rate             • Harsh Acceleration Frequency        │

│ • Severity-Weighted Risk Index        • Lateral Steering Anomaly Rate       │

│ • Harsh Braking Frequency                                                   │

└─────────────────────────────────────────────────────────────────────────────┘

```

---

## 19. Historical Aggregation

Individual trip scores must not be combined using a simple unweighted arithmetic mean. Aggregation accounts for total trip duration and time-decay recency:

### Composite Weight Vector

$$
w_i = T_i \cdot R_i
$$

Where:
* $T\_i$ = Session operating duration
* $R\_i$ = Exponential recency weight factor

### Exponential Recency Decay

$$
R_i = e^{-\lambda \Delta t_i}
$$

Where:
* $\lambda$ = Half-life decay constant
* $\Delta t\_i$ = Elapsed time delta since trip completion

---

## 20. Exposure-Weighted Historical Features

### Continuous Features Aggregation

$$
\text{HistoricalFeature}
=
\frac{
\sum \left(\text{Feature}_i \cdot T_i \cdot R_i\right)
}{
\sum \left(T_i \cdot R_i\right)
}
$$

### Discrete Event Rates Aggregation

$$
\text{EventRate}
=
\frac{\sum \text{TotalEvents}}
{\sum \text{TotalDrivingHours}}
$$

---

## 21. Driver Score Architecture

The centralized driver score represents a composite multi-factor index bounded strictly between $0$ and $100$:

$$
\boxed{
\text{DriverScore}
=
0.35F + 0.25S + 0.15A + 0.15E + 0.10H
}
$$

```

┌─────────────────────────────────────────────────────────────────────────────┐

│                            COMPONENT BREAKDOWN                              │

├────────────────────────────┬────────┬───────────────────────────────────────┤

│ Component                  │ Weight │ Primary Target Focus                  │

├────────────────────────────┼────────┼───────────────────────────────────────┤

│ Fatigue Resilience ($F$)   │  35%   │ Eye closure, yawns, microsleep lapses │

│ Safety Performance ($S$)   │  25%   │ Dynamic telemetry, critical incidents │

│ Attention Index ($A$)      │  15%   │ Head orientation, gaze tracking       │

│ Experience Factor ($E$)    │  15%   │ Cumulative logged hours, trip history │

│ Health & Fitness ($H$)     │  10%   │ Physiological baseline, vitals        │

└────────────────────────────┴────────┴───────────────────────────────────────┘

```

---

## 22. Fatigue Score ($F$)

$$
\boxed{
F = 0.30P + 0.25M + 0.15Y + 0.20D + 0.10U
}
$$

Where:
* $P$ = Normalized PERCLOS score
* $M$ = Microsleep severity score
* $Y$ = Yawn frequency score
* $D$ = Persistent drowsiness score
* $U$ = Unresponsive event score

---

## 23. Microsleep Score ($M$)

Deconstructed to balance episodic frequency against singular extreme severity events:

$$
\boxed{
M = 0.50M_r + 0.30M_a + 0.20M_x
}
$$

Where:
* $M\_r$ = Microsleep rate score
* $M\_a$ = Average microsleep duration score
* $M\_x$ = Maximum microsleep duration score

---

## 24. Yawn Score ($Y$)

$$
\boxed{
Y = 0.70Y_r + 0.30Y_d
}
$$

Where:
* $Y\_r$ = Normalized yawn frequency rate score
* $Y\_d$ = Normalized average yawn duration score

---

## 25. Drowsiness Score ($D$)

Historical drowsiness is derived from continuous cumulative exposure metrics:

```text

┌─────────────────────────────────────────────────────────────────────────────┐

│ • Total Drowsy Exposure Duration   • Average Sustained Episode Duration     │

│ • Episode Frequency per Hour       • Maximum Single Episode Length          │

└─────────────────────────────────────────────────────────────────────────────┘

```

---

## 26. Attention Score ($A$)

$$
\boxed{
A = 0.45D_r + 0.45D_t + 0.10B
}
$$

Where:
* $D\_r$ = Distraction episode rate score
* $D\_t$ = Cumulative distracted time percentage score
* $B$ = Normalized blink deviation score (allocated 10% due to noise)

---

## 27. Safety Score ($S$)

### Factor Allocation Structure

| Violation Factor | Proposed Weight | Trigger Dependencies |
|---|---:|---|
| **Emergency Incidents** | **40%** | Discrete critical threshold breaches |
| **Harsh Braking Events** | **25%** | Longitudinal deceleration limits |
| **Rapid Acceleration** | **20%** | Positive surge delta limits |
| **Steering Anomalies** | **15%** | High-frequency angular displacement |
---

## 28. Normalization

Converts raw risk indices into an inverted $[0, 100]$ score (where higher score indicates safer performance):

$$
\text{Score}(x)
=
\begin{cases}
100, & x \le L \\
100 \cdot \left(\frac{U-x}{U-L}\right), & L < x < U \\
0, & x \ge U
\end{cases}
$$

```text

     100 ┌──────────┐

         │          │\\

         │          │ \\

         │          │  \\

         │          │   \\

       0 └──────────┴────┴───────────► Metric Value (x)

                    ▲    ▲

                    │    │

             Lower (L)  Upper (U)

```

---

## 29. Initial PERCLOS Normalization

```text

   0%               12.5%                                   30.0%

   ├──────────────────┼───────────────────────────────────────┤

   │  Score = 100     │      Linear Degradation Area          │   Score = 0

   │  (Nominal Risk)  │      (100 ──────► 0 Points)           │   (Hazardous)

```

> ⚠️ **Calibration Prerequisite***

> Operational boundaries ($L = 12.5\\%$, $U = 30.0\\%$) represent empirical engineering configurations. These parameters must be systematically recalibrated following on-road trial evaluation.*

---

## 30. Critical Event Constraints

```text

                        [ Evaluated Score ]

                                 │

                                 ▼

                  Validated Critical Events Found?

                                 │

                   ┌─────────────┴─────────────┐

                  NO                          YES

                   │                           │

                   ▼                           ▼

            [ No Score Cap ]        Single or Multiple Events?

                                               │

                                 ┌─────────────┴─────────────┐

                            SINGLE                       REPEATED

                                 │                           │

                                 ▼                           ▼

                        [ Score Cap = 75 ]          [ Score Cap = 50 ]

```

---

## 31. Why Score Caps?

```text

  Hypothetical High-Scoring Driver Profile:

  ──────────────────────────────────────────

  Fatigue Resilience : 95

  Safety Score       : 95

  Attention Score    : 90

  Experience Factor  : 95

  Health Profile     : 90

  ──────────────────────────────────────────

  Uncapped Weighted Score ──► 93.5 (A Grade)  ◄── Dangerous false signal if an

                                                  unresponsive blackout occurred.

  Applying Safety Override:

  ──────────────────────────────────────────

  [ Uncapped Score: 93.5 ] + [ 1 Unresponsive Incident ] ──► Final Score Capped at 75

```

---

## 32. Score Confidence

Statistical weight scales in direct proportion to verified cumulative operating hours:

```text

       LOW                   MEDIUM                   HIGH                 VERY HIGH

  [ < 5 Hours ]   │      [ 5–25 Hours ]   │     [ 25–50 Hours ]   │      [ > 50 Hours ]

  ────────────────┼───────────────────────┼───────────────────────┼────────────────────

  Volatile index  │ Directional baseline  │  Statistically solid  │ Full confidence

```

---

## 33. Long-Term Driver Score vs Route Suitability

```text

┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐

│        LONG-TERM DRIVER SCORE        │     │        ROUTE SUITABILITY SCORE       │

├──────────────────────────────────────┤     ├──────────────────────────────────────┤

│ • Macro historical performance index │     │ • Dynamic immediate readiness factor │

│ • Stable rolling multi-week baseline │     │ • Evaluates acute, real-time fatigue │

│ • Used for fleet-wide ranking        │     │ • Evaluates impending route payload  │

└──────────────────────────────────────┘     └──────────────────────────────────────┘

```

> **Operational Scenario**: A top-tier driver ($Score = 85$) arriving off an extended shift with high acute fatigue will yield a low **Route Suitability Score** for high-risk nighttime assignments.*

---

## 34. Route Suitability Architecture

```text

                       ┌──────────────────────────────┐

                       │    LONG-TERM DRIVER SCORE    │

                       └──────────────┬───────────────┘

                                      │

                 ┌────────────────────┴────────────────────┐

                 ▼                                         ▼

   ┌───────────────────────────┐             ┌───────────────────────────┐

   │     ACUTE RISK ENGINE     │             │    ROUTE CONTEXT MODEL    │

   ├───────────────────────────┤             ├───────────────────────────┤

   │ • Recent Fatigue Gradient │             │ • Route Duration          │

   │ • Recent Microsleeps      │             │ • Operational Time of Day │

   │ • Active Logged Hours     │             │ • Terrain Risk Index      │

   │ • Immediate Safety Events │             │ • Weather Conditions      │

   └─────────────┬─────────────┘             └─────────────┬─────────────┘

                 │                                         │

                 └────────────────────┬────────────────────┘

                                      ▼

                       ╔═════════════════════════════╗

                       ║   ROUTE SUITABILITY SCORE   ║

                       ╚═════════════════════════════╝

```

---

## 35. Event-Based Architecture

Discrete driver anomalies are saved into an event ledger for instant replay and auditability:

```text

  Entity Schema: driver\_events

  ├── event\_id      : Unique event identifier (UUID)

  ├── driver\_id     : Associated driver profile key

  ├── trip\_id       : Associated trip session key

  ├── event\_type    : Discrete event classification

  │                   ├── YAWN

  │                   ├── MICROSLEEP

  │                   ├── DROWSY\_EPISODE

  │                   ├── UNRESPONSIVE

  │                   ├── DISTRACTION

  │                   ├── HARSH\_BRAKING

  │                   ├── HARSH\_ACCELERATION

  │                   └── STEERING\_ANOMALY

  ├── start\_time    : Incident start timestamp

  ├── end\_time      : Incident end timestamp

  ├── duration      : Total sustained duration (seconds)

  ├── severity      : Calculated risk level (0.0 - 1.0)

  ├── metadata      : Encoded context payload (JSON)

  └── frames        : S3/Blob storage image references

```
