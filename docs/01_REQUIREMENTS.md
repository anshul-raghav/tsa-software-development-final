# TouchMap Requirements Specification

This document summarizes the most important requirements for `TouchMap`, a voice-guided app that helps blind and low-vision users use flat control panels more independently.

## 1. Design Goals

- **Accessibility:** The app must work without requiring the user to rely on sight.
- **Usability:** A first-time user should be able to scan a panel and get help with minimal training.
- **Performance:** The system should respond quickly enough to feel practical in everyday use.
- **Reliability:** If the app is unsure, it should say so clearly and guide the user toward the next best step.

## 2. Functional Requirements

### FR-1: Guided Scan
**Description:** The app helps the user capture a clear image of the panel.  
**Input:** Camera feed.  
**Process:** The app gives spoken directions such as "move left" or "hold still."  
**Output:** A usable scan image.  
**Priority:** High  
**Why it matters:** A poor scan makes every later step less reliable.

### FR-2: AI-Assisted Panel Understanding
**Description:** The system identifies labels, buttons, and layout sections on the panel.  
**Input:** Captured image.  
**Process:** The backend uses OCR to read visible text and an AI interpretation layer to organize what it finds into a clear internal map.  
**Output:** A panel map that shows where controls are and how they relate to each other.  
**Priority:** High  
**Why it matters:** This feature turns raw image data into a panel map the app can reason about.

### FR-3: Task Mode
**Description:** The app guides the user through a goal such as heating food for 60 seconds.  
**Input:** User request and panel map.  
**Process:** The system decides which controls are needed and gives step-by-step spoken instructions.  
**Output:** A spoken task plan.  
**Priority:** High  
**Why it matters:** This helps the app do more than read labels. It can guide the user through an actual task.

### FR-4: Locate Mode
**Description:** The app helps the user find one specific control.  
**Input:** User request and panel map.  
**Process:** The system searches for the requested control and describes its position.  
**Output:** Spoken location guidance.  
**Priority:** High  
**Why it matters:** Users often need one button quickly, not a full explanation of the panel.

### FR-5: Explore Mode
**Description:** The app describes parts of the panel so the user can build a mental map.  
**Input:** User request and panel map.  
**Process:** The system explains what is in a selected area, such as a row or number pad.  
**Output:** Spoken layout description.  
**Priority:** High  
**Why it matters:** This helps users understand the interface before taking action.

### FR-6: Live Guidance
**Description:** The app gives more precise real-time help when a control is still hard to find.  
**Input:** Live camera view during guidance.  
**Process:** The system checks what area is in view and gives corrective spoken cues.  
**Output:** Real-time feedback such as "slightly right" or "almost there."  
**Priority:** High  
**Why it matters:** This provides a recovery path when basic directions are not enough.

### FR-7: Error Recovery
**Description:** The app handles unclear input, failed scans, and missing controls safely.  
**Input:** Errors or low-confidence results.  
**Process:** The system avoids guessing and offers retry, clarify, or rescan guidance.  
**Output:** Clear spoken recovery instructions.  
**Priority:** High  
**Why it matters:** Safe failure behavior improves trust and accessibility.

## 3. Non-Functional Requirements

### NFR-1: Accuracy
- The app should identify common controls well enough to provide useful help.
- AI-generated panel understanding should be checked before it is used for guidance.
- If confidence is low, it should ask the user to retry instead of pretending to be certain.

### NFR-2: Responsiveness
- Spoken feedback should begin quickly after user input.
- The app should remain smooth while waiting for backend processing.

### NFR-3: Accessibility
- Instructions must use simple, direct language.
- Important steps must be spoken clearly and repeatable on request.

### NFR-4: Maintainability
- Major features should be split into clear modules such as scanning, task planning, locating, and guidance.
- Requirements should connect clearly to features and tests.

## 4. User Stories

- As a blind user, I want the app to tell me how to position my phone, so that I can scan the panel independently.
- As a blind user, I want the app to tell me where a button is, so that I can press it without assistance.
- As a blind user, I want to say what I am trying to do, so that I can complete a task step by step.
- As a blind user, I want the app to describe the layout, so that I can understand the interface before acting.

## 5. Constraints and Assumptions

- The system depends on a smartphone with a working camera.
- Some features depend on internet access and configured backend/API services.
- Performance may vary depending on lighting, glare, camera quality, and panel condition.
- The user may need to grant camera and microphone permissions.

## 6. Edge Cases and Failure Conditions

- If the user request is unclear, the app should ask for clarification.
- If the scan is blurry or incomplete, the app should request a rescan.
- If the requested control is not found, the app should say so clearly and suggest another mode or retry.
- If the system cannot complete a task safely, it should stop and explain why.

## 7. Scope Definition

### In Scope
- Guided scan capture
- Panel reading and layout mapping
- Task Mode
- Locate Mode
- Explore Mode
- Live guidance fallback
- Testing of major workflows

### Out of Scope
- Fully offline intelligence for all features
- Physical hardware modifications to appliances
- Automatic button pressing or robotics

## 8. Requirement Traceability Preview

| Requirement ID | Feature / Module | Planned Test |
|---|---|---|
| FR-1 | Scan capture flow | Scan guidance test |
| FR-2 | OCR + AI panel mapping pipeline | Scan pipeline integration test |
| FR-3 | Task planning | Task planning unit test |
| FR-4 | Locate service | Locate logic unit test |
| FR-5 | Explore service | Explore description test |
| FR-6 | Live guidance | Guidance workflow test |
| FR-7 | Error handling | Failure-path test |

## Who's Doing What

| Team Member | Responsibilities |
|---|---|
| Ryan | Frontend accessibility flow, navigation, and user experience |
| Avyank | Scan pipeline, image handling, and backend processing |
| Parthiv | Task logic, locate logic, and action guidance |
| Stephanie | Requirements quality, testing, and traceability |
| Anshul | System integration, architecture, live guidance, and final coordination |
