# TouchMap

**Audio-guided navigation for flat physical interfaces**

TouchMap is an accessibility app designed to help blind and low-vision users independently interact with flat control panels such as microwaves, washers, thermostats, vending machines, and other modern appliances. The idea for this project came from asking my great-grandfather in India, who is blind, about the barriers he runs into with modern devices. Through those conversations, and by noticing that he could not easily navigate airport kiosks or use certain hospital equipment, we became more aware of how many important interfaces are now flat, visual, and difficult to use without tactile cues. Instead of only reading labels out loud, TouchMap scans the panel, uses AI to interpret the layout and controls, and then helps the user understand and operate the device through spoken guidance.

## Project Overview

At a high level, TouchMap turns a hard-to-use flat surface into something a blind user can understand and navigate. The project combines phone-based scanning, spoken scan guidance, OCR text reading, AI-based layout interpretation, step-by-step task help, and live spoken assistance into one system. Instead of only telling the user what words are on a device, TouchMap is designed to explain how the interface is organized and help the user complete real actions more independently.

### Repository Structure

```text
.
|-- backend/                     # Main server, logic, routes, and tests
|   `-- app/
|       |-- api/                # App endpoints for scan, task, locate, explore, and guidance
|       |-- domain/             # Core project data structures and templates
|       |-- flows/              # Full scan process
|       |-- services/           # Image reading, layout understanding, and guidance logic
|       `-- tests/              # Backend tests
|-- frontend/                    # Mobile app interface
|   `-- touchmap/
|       |-- screens/            # Main app screens
|       |-- components/         # Reusable interface pieces
|       |-- services/           # App support features such as speech and storage
|       |-- state/              # App flow and screen state
|       `-- models/             # Shared app data types
|-- docs/                        # Numbered project documentation
|-- tests/                       # Additional tests
`-- README.md
```

### Docs Roadmap

After reading this README, go through the `docs/` section in order:

1. `docs/01_REQUIREMENTS.md`
2. `docs/02_DESIGN.md`
3. `docs/03_IMPLEMENTATION.md`
4. `docs/04_TESTING.md`
5. `docs/05_TECH_STACK.md`
6. `docs/06_LOCAL_SETUP.md`

## Problem

Modern products increasingly replace tactile buttons, dials, and raised landmarks with smooth digital panels. While these designs may appear sleek and efficient, they remove the physical reference points many blind users depend on to navigate a device. As a result, routine actions such as heating food, starting a wash cycle, or operating a shared appliance can become difficult, frustrating, or inaccessible without outside help.

This challenge is not simply a matter of convenience. It is a growing accessibility problem created by modern design. Many current devices assume that a user can look at a panel, understand where the controls are, and press them in the correct order. For blind users, those assumptions fail immediately, which can take away independence from tasks that should otherwise be simple and routine.

## Gaps in Current Approaches

Current approaches help only part of the problem:

- Asking another person for help reduces independence and privacy.
- Memorizing a familiar machine does not work for new, shared, or public devices.
- Tactile stickers require manual setup and are not practical for every device.
- OCR tools can read labels such as "Start" or "Defrost," but they usually do not explain where those controls are or how they fit into the rest of the panel.
- Live camera readers can describe what the camera sees, but they do not consistently guide a user through locating the correct control and completing a task in the proper order.

The central gap is that most existing solutions focus on recognizing information rather than helping the user act on it. They may identify words or describe what is in view, but they do not give the user a clear picture of the layout or guide them through using the interface with confidence.

## Proposed Solution

TouchMap addresses this problem through a step-by-step process that moves from scanning a panel to actually using it:

1. The user scans a flat panel with a smartphone while receiving spoken framing feedback such as "move left," "tilt down," or "hold still."
2. The system reads the panel with OCR, uses AI to interpret the image and its labels, and builds a clear internal map of how the panel is arranged.
3. That map supports three user-facing modes:

- **Task Mode:** The user says what they want to do, such as "set the microwave for 60 seconds," and the system produces step-by-step spoken instructions.
- **Locate Mode:** The user asks for a specific control, such as "Where is Start?" and receives targeted spatial directions.
- **Explore Mode:** The user asks for descriptions of groups or sections, such as "Describe the number pad," to build a mental model before acting.

When a control remains difficult to locate, the system can switch into live guidance and provide more detailed spoken feedback to help the user move toward the correct area of the panel.

This design makes TouchMap more than a recognition tool. It is meant to help the user understand the panel, find the right controls, and complete a task with greater independence.

## Key Innovations

### 1. Goal-first interaction instead of label-first interaction

Most existing tools stop at naming what appears on a panel. TouchMap begins with what the user wants to do. Rather than returning isolated labels, the system uses AI and structured logic to turn a spoken goal into a useful sequence of actions. This changes the interaction from simply reading information to helping the user complete a task.

### 2. Spatial intelligence through structured panel mapping

TouchMap does not treat the interface as just a list of words. It uses AI to interpret how the controls are grouped and where they are located. This allows the app to describe the panel as an organized layout instead of a disconnected list of labels, making the interface easier to understand and use.

### 3. Multimodal accessibility pipeline

The project combines scan guidance, OCR, AI-based panel interpretation, task planning, voice output, and live corrective feedback in one layered system. This creates a solution that goes far beyond a basic reader and makes the app more useful in real-world accessibility situations.

### 4. Mode-based interaction for different user needs

A user may need to complete a task, locate a single control, or understand an entire interface before taking action. TouchMap supports these different needs through separate modes rather than forcing every situation into one workflow. This makes the system more flexible and better suited to real use.

### 5. Independence on unfamiliar devices

Many existing workarounds stop working as soon as the device changes. TouchMap is designed for first-time or shared-device use, which makes it especially valuable in places such as schools, workplaces, hotels, offices, and other spaces where blind users may encounter unfamiliar interfaces.

## Images of the App

### Home / Start Scan

`[Insert screenshot: home or landing screen]`

### Panel Scan Capture

`[Insert screenshot: panel scan capture screen]`

### Task Mode

`[Insert screenshot: task mode screen]`

### Locate Mode

`[Insert screenshot: locate mode screen]`

### Explore Mode

`[Insert screenshot: explore mode screen]`

### Live Guidance

`[Insert screenshot: live guidance screen]`
