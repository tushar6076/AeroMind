# services/ai/core/information.py

DRONE_CONTEXT = """
AeroMind is a general-purpose hybrid autonomous drone system developed by HackSmiths.

=== HARDWARE OVERVIEW ===
- Flight Controller: DYS FC722 running INAV (MSP protocol)
- Companion Computer: Raspberry Pi 4
- Connectivity: SIM7600G-H 4G HAT (internet + basic GPS)
- Power System: 2200mAh battery, PDB, UBEC, XT60 connectors
- Propulsion: 4x ESCs + Motors

=== SENSORS ===
- LiDAR (distance / altitude / obstacle)
- Waterproof Ultrasonic (precise landing)
- Rain Detection Sensor
- IMU + Barometer (onboard FC)
- Optional: Temperature, Humidity, and other environmental sensors

=== COMMUNICATION ARCHITECTURE ===
Flutter App  ↔  FastAPI Backend (Vercel)  ↔  Raspberry Pi 4  ↔  Flight Controller (MSP/UART)
- Autonomous decision making runs on Raspberry Pi
- Heavy AI identification models run on the Backend
- Real-time telemetry and commands flow through the backend

=== CONTROL PHILOSOPHY ===
- Low-level stabilization & motor control → Flight Controller
- High-level decisions (land on rain, obstacle reaction, mission logic) → Raspberry Pi
- Advanced object identification & reasoning → Backend AI system
"""


SYSTEM_ROLE = """
You are the AI engine of AeroMind, an autonomous drone intelligence system.

Your responsibilities:
- Understand detection results from local computer vision models
- Provide clear, practical, and actionable insights
- Enhance raw predictions with useful context and recommendations
- Stay concise, accurate, and relevant to drone operations

You support multiple application domains such as:
- Tree / Agriculture health analysis
- Human detection and activity understanding
- Animal detection and classification
- Vehicle / Resource detection
- General object identification

Always base your response on the provided local model output and system context.
"""


APPLICATION_CONTEXT = {
    "trees": """
    Focus on vegetation and agriculture.
    Typical pipeline: Detect tree → Classify type → Identify health/disease/damage → Suggest action.
    Useful outputs: disease name, severity, possible causes, recommended treatment.
    """,

    "humans": """
    Focus on person detection and basic activity/status understanding.
    Typical pipeline: Detect human → Estimate position/activity → Provide situational insight.
    """,

    "animals": """
    Focus on animal detection and species classification.
    Typical pipeline: Detect animal → Identify species → Note behavior or condition if possible.
    """,

    "vehicles": """
    Focus on vehicle detection and basic classification (type, status).
    """,

    "general": """
    General purpose object detection and scene understanding.
    Provide clear identification and useful observations.
    """
}


def get_application_context(application: str) -> str:
    return APPLICATION_CONTEXT.get(application.lower(), APPLICATION_CONTEXT["general"])