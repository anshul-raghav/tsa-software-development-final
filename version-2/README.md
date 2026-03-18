# TouchMap

**Audio-Guided Navigation for Flat Physical Interfaces**

TouchMap is a mobile accessibility system that helps blind users interact with flat control panels — microwaves, thermostats, washers, vending machines, and similar devices — by converting them into structured, navigable interfaces with spoken guidance.

---

## Architecture

TouchMap uses a **hybrid mobile + backend architecture** with a multi-stage intelligence pipeline.

```
Mobile App (React Native + TypeScript)
    │
    │  REST API
    ▼
Backend API (FastAPI + Python)
    │
    ├── Image Preprocessing (OpenCV)
    ├── ML Interface Classifier (MobileNetV2)
    ├── OCR Extraction (EasyOCR)
    ├── OpenAI Vision → Structured PanelMap
    ├── Schema Validation (Pydantic)
    ├── ControlGraph Builder (deterministic)
    └── Mode Engines (Task / Locate / Explore / Guidance)
```

### Core Pipeline

```
Raw Image → Preprocessing → ML Classifier → OCR → OpenAI PanelMap → Validator → ControlGraph → Modes
```

Every component after scanning works off the structured `ControlGraph`, not raw text or unstructured LLM output.

---

## Key Features

### Three Interaction Modes

- **Task Mode** — Goal-first. Say "Set the microwave for 60 seconds" and get step-by-step button instructions.
- **Locate Mode** — Find a specific control. "Where is Start?" returns spatial directions.
- **Explore Mode** — Build a mental map. "Describe the number pad" returns a spoken layout description.

### Live Guidance

Real-time camera-based fallback when spoken directions aren't enough. The app gives directional spoken cues ("move right", "almost there") with haptic proximity feedback.

### Audio-Guided Scanning

During capture, the app provides spoken alignment feedback — "move left", "hold still", "too far" — so the user can frame the panel correctly.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile App | React Native, Expo, TypeScript |
| State Management | Pure reducer state machine (12 states, defined transitions) |
| Speech | Expo Speech (TTS), voice input |
| Haptics | Expo Haptics |
| Backend API | FastAPI, Python, Pydantic |
| Image Processing | OpenCV (perspective, contrast, glare, crop) |
| OCR | EasyOCR |
| ML Classifier | MobileNetV2 transfer learning (PyTorch) |
| Semantic Parsing | OpenAI GPT-4o Vision → strict JSON |
| Graph Engine | Deterministic spatial graph builder |
| Task Planning | Template-based deterministic planner |
| Persistence | In-memory (demo), SQLite-ready |

---

## Project Structure

### Backend

```
backend/
  app/
    api/routes/          # REST endpoints (scan, task, locate, explore, guidance, debug, health)
    core/                # Config, logging, exception hierarchy
    domain/
      models/            # Pydantic domain models (PanelMap, ControlGraph, TaskPlan)
      schemas/           # API request/response schemas
      templates/         # Device templates (MicrowaveTemplate)
    services/            # 12 service modules
      scan_processing/   # Image preprocessing (OpenCV)
      interface_classification/  # ML classifier
      ocr/               # Text extraction (EasyOCR)
      panelmap_extraction/       # OpenAI Vision integration
      panelmap_validation/       # Schema validation + normalization
      control_graph/     # Spatial graph builder
      intent_parsing/    # NL intent extraction (rules + LLM fallback)
      task_planning/     # Deterministic task plan generator
      locate/            # Control finder with spatial descriptions
      explore/           # Layout description generator
      live_guidance/     # Real-time directional guidance
      session/           # Session and scan storage
    ml/
      training/          # MobileNetV2 training script
      inference/         # Model loading and prediction
    prompts/             # OpenAI prompt templates
    tests/
      unit/              # Unit tests for all services
      integration/       # API endpoint tests
      prompt_eval/       # PanelMap extraction evaluation
    main.py              # FastAPI application factory
```

### Mobile

```
mobile/
  src/
    models/              # TypeScript interfaces (PanelMap, TaskPlan, etc.)
    services/
      api/               # Typed API client (axios)
      speech/            # TTS service
      haptics/           # Haptic feedback patterns
      storage/           # AsyncStorage persistence
    state/
      sessionMachine/    # 12-state machine with pure transitions
      hooks/             # React hooks
    screens/             # HomeScreen, ScanScreen, PanelReady, TaskMode, LocateMode, ExploreMode, LiveGuidance
    components/          # VoiceButton, SpokenPromptCard, ModeCard, StatusBanner, ScanOverlay
    constants/           # Theme (colors, spacing, font sizes), config
  App.tsx                # Root — state-machine-driven screen routing
```

---

## Data Models

### PanelMap

Structured representation of a scanned control panel:
- Controls with labels, types, bounding boxes, aliases, and spoken descriptions
- Regions grouping related controls (e.g., "Number Pad", "Action Buttons")
- Landmarks for non-interactive visual anchors
- Normalized bounding box coordinates (0.0–1.0)

### ControlGraph

Spatial graph derived from PanelMap:
- Nodes: individual controls with row/column indices
- Edges: spatial relationships (left_of, right_of, above, below, adjacent_to, inside_region)
- Spoken reference phrases for each control

### TaskPlan

Ordered sequence of steps to accomplish a user goal:
- Parsed intent (e.g., `heat_for_time`, `duration_seconds: 60`)
- Step-by-step instructions with control IDs
- Confidence scoring and fallback messages

---

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env      # Add your OPENAI_API_KEY
uvicorn app.main:app --reload
```

### Mobile

```bash
cd mobile
npm install
npx expo start
```

---

## Testing

```bash
cd backend
pytest                     # Run all tests
pytest app/tests/unit/     # Unit tests only
pytest -v                  # Verbose output
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/scan` | Full scan pipeline |
| GET | `/api/v1/scan/{scan_id}` | Retrieve scan results |
| POST | `/api/v1/task/plan` | Generate task plan |
| POST | `/api/v1/task/repeat` | Repeat current step |
| POST | `/api/v1/task/clarify` | Clarify a step |
| POST | `/api/v1/locate` | Find a control |
| POST | `/api/v1/explore` | Describe layout |
| POST | `/api/v1/guidance/start` | Start live guidance |
| POST | `/api/v1/guidance/frame` | Process guidance frame |
| POST | `/api/v1/guidance/stop` | Stop guidance |
| GET | `/api/v1/debug/panel/{scan_id}` | Raw debug data |
| GET | `/api/v1/health` | Health check |

---

## State Machine

The app uses an explicit 12-state machine for session lifecycle:

```
idle → scanning → processing_scan → panel_ready → task_mode / locate_mode / explore_mode
                                                 ↘ live_guidance (fallback from Task/Locate)
```

Every mode transition is a defined event. Error recovery routes through a dedicated state.

---

## Design Principles

1. **LLM as semantic layer, not the whole app** — OpenAI extracts structured data; everything after runs deterministically.
2. **Structured internal models** — All reasoning runs on PanelMap and ControlGraph, not raw text.
3. **Deterministic where possible** — Task planning uses templates; LLM is a fallback for ambiguous input.
4. **Voice-first, accessible UI** — Large targets, high contrast, full spoken confirmations.
5. **Modular service architecture** — Each service has a single responsibility, explicit inputs/outputs, and is independently testable.
