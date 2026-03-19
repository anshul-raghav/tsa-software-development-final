

# TouchMap

**Audio-guided navigation for flat physical interfaces**

TouchMap is an accessibility app designed to help blind and low-vision users independently interact with flat control panels such as microwaves, washers, thermostats, vending machines, and other modern appliances. The idea for this project came from asking my great-grandfather in India, who is blind, about the barriers he runs into with modern devices. Through those conversations, and by noticing that he could not easily navigate airport kiosks or use certain hospital equipment, we became more aware of how many important interfaces are now flat, visual, and difficult to use without tactile cues. Rather than just reading labels out loud, TouchMap scans the panel, uses AI to interpret the layout and controls, and then helps the user understand and operate the device through spoken guidance.

## Project Overview

At a high level, TouchMap turns a hard-to-use flat surface into something a blind user can understand and navigate. The project combines phone-based scanning, optical character recognition (OCR) text reading, AI-based layout interpretation, and step-by-step task help into one system. It does more than tell the user what words are on a device. It explains how the interface is organized and helps the user complete real actions more independently.

### Repository Structure

```text
.
|-- backend/                    # FastAPI backend and scan/guidance logic
|   |-- app/
|   |   |-- api/               # Routes and controllers
|   |   |-- core/              # Config, logging, exceptions
|   |   |-- domain/            # Models, schemas, and templates
|   |   |-- flows/             # End-to-end scan pipeline
|   |   |-- prompts/           # AI prompt definitions
|   |   |-- repositories/      # Persistence-layer hooks
|   |   `-- services/          # OCR, panel mapping, tasks, locate, explore, guidance
|   |-- uploads/               # Saved backend image outputs
|   `-- pytest.ini
|-- frontend/                   # Expo / React Native mobile app
|   |-- touchmap/
|   |   |-- components/        # Reusable UI pieces
|   |   |-- constants/         # Design tokens and API config
|   |   |-- models/            # Shared frontend data types
|   |   |-- screens/           # Main app screens
|   |   |-- services/          # API, speech, haptics, storage
|   |   `-- state/             # Session state machine and hooks
|   |-- assets/
|   |-- package.json
|   `-- touchmap-app.tsx
|-- docs/                       # Numbered project documentation
|-- tests/                      # Unit and integration tests
|-- app_images/                 # README screenshots
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

Modern products increasingly replace tactile buttons, dials, and raised landmarks with smooth digital panels. While these designs may appear sleek and efficient, they remove the physical reference points many blind users depend on to navigate a device. As a result, routine actions such as heating food, starting a wash cycle, or operating a shared appliance can become difficult, frustrating, or inaccessible without outside help. This is not just a hypothetical concern: Ontario's accessibility guidance for self-service kiosks specifically calls out the need for features such as audio instructions, tactile keyboards, and headset jacks, and kiosk accessibility researchers note that these systems are now common in public and essential settings while still creating major access barriers for blind and low-vision users ([Ontario accessibility guidance](https://www.ontario.ca/page/how-make-self-service-kiosks-accessible), [Toward Unified Guidelines for Kiosk Accessibility](https://pmc.ncbi.nlm.nih.gov/articles/PMC8855367/)).

This challenge is not simply a matter of convenience. It is a growing accessibility problem created by modern design. Many current devices assume that a user can look at a panel, understand where the controls are, and press them in the correct order. For blind users, those assumptions fail immediately, which can take away independence from tasks that should otherwise be simple and routine. Recent research makes the same point directly: "many public kiosks with touchscreens are inaccessible to blind people" ([Making Inaccessible Public Touchscreens Accessible](https://arxiv.org/abs/2305.04097)).

## Gaps in Current Approaches

Current approaches help only part of the problem:

- Asking another person for help reduces independence and privacy, which kiosk accessibility researchers specifically identify as a real concern in public and sensitive interactions ([Toward Unified Guidelines for Kiosk Accessibility](https://pmc.ncbi.nlm.nih.gov/articles/PMC8855367/)).
- Memorizing a familiar machine does not work for new, shared, or public devices.
- Tactile stickers require manual setup and are not practical for every device.
- Optical character recognition (OCR) tools can read labels such as "Start" or "Defrost," but they usually do not explain where those controls are or how they fit into the rest of the panel.
- Live camera readers can describe what the camera sees, but they do not consistently guide a user through locating the correct control and completing a task in the proper order.

The main gap is that most existing solutions focus on recognizing information rather than helping the user act on it. They may identify words or describe what is in view, but they do not give the user a clear picture of the layout or guide them through using the interface with confidence.

## Proposed Solution

TouchMap addresses this problem through a step-by-step process that moves from scanning a panel to actually using it:

1. The user scans a flat panel with a smartphone while receiving spoken framing feedback such as "move left," "tilt down," or "hold still."
2. The system reads the panel with OCR, uses AI to interpret the image and its labels, and builds a clear internal map of how the panel is arranged.
3. That map supports three user-facing modes:

- **Task Mode:** The user says what they want to do, such as "set the microwave for 60 seconds," and the system produces step-by-step spoken instructions.
- **Locate Mode:** The user asks for a specific control, such as "Where is Start?" and receives targeted spatial directions.
- **Explore Mode:** The user asks for descriptions of groups or sections, such as "Describe the number pad," to build a mental model before acting.

When a control remains difficult to locate, the system can switch into live guidance and provide more detailed spoken feedback to help the user move toward the correct area of the panel.

That makes TouchMap more than a recognition tool. It helps the user understand the panel, find the right controls, and complete a task with greater independence.

## Key Innovations

TouchMap is not just a reader for buttons on a screen. It takes a hard accessibility problem and solves it in a more original, usable way. These are the three clearest innovations:

### 1. It starts with the user's goal, not just the label on a button

Most existing tools answer questions like "What text is on this panel?" TouchMap can answer "How do I do what I want to do?" If the user says "heat food for 30 seconds" or "start delicate wash," the app turns that goal into guided steps instead of just reading labels one by one.

Why it stands out: it changes the interaction from passive reading to task completion. That is a much more original use of AI and accessibility support than a basic OCR reader.

### 2. It builds a mental map of the panel instead of treating it like random text

TouchMap does not treat the interface as a flat list of words. It tries to understand where controls are, which buttons belong together, and how the layout is organized. That lets the app say things like "the number pad is on the left" or "Start is in the lower-right area" in a way that is useful to someone who cannot rely on sight.

Why it stands out: most accessibility tools stop at recognition. TouchMap adds spatial understanding, which makes the panel easier to imagine and navigate.

### 3. It turns the panel into a control map the app can reason about

After reading the panel, TouchMap does not stop at labels. It assigns controls to rows and columns, groups them into regions, and records spatial relationships such as left of, right of, above, below, and adjacent. In other words, the app builds a structured control map instead of treating the panel like a loose collection of text.

Why it stands out: this gives the system something concrete to reason over. That is what makes it possible to support task guidance, locate help, and panel exploration from the same scan.

## Comparison With Existing Approaches


| Approach              | What it does well                                        | What it usually misses                                                    | How TouchMap is different                                                                       |
| --------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Object detection      | Can point out that buttons or controls exist             | Often does not explain what each control means or how to use it in order  | TouchMap connects control identity, layout, and task planning in one flow                       |
| OCR readers           | Reads visible text such as `Start`, `Stop`, or `Defrost` | Does not explain layout, button groups, or task sequence                  | TouchMap reads text, builds a panel map, and turns goals into guided actions                    |
| Asking another person | Can help in the moment                                   | Reduces privacy and independence, especially for shared or public devices | TouchMap is designed to let the user scan, understand, and operate the panel more independently |


## Example Use Cases

### Use Case 1: Heat food for 30 seconds on a microwave

1. The user points their phone at the microwave panel.
2. TouchMap gives scan guidance such as "move left" or "hold still" until the panel is framed well enough.
3. The app reads the panel, identifies the controls, and builds an internal map of the layout.
4. The user says, "Heat food for 30 seconds."
5. TouchMap turns that request into steps such as: press `Time Cook`, press `3`, press `0`, then press `Start`.
6. If the user cannot find `Start`, they can ask where it is and get location guidance such as "bottom-right corner."
7. If needed, the app can switch to live guidance to help the user move their hand closer to the right control, with feedback such as "move your hand slightly to the left."

### Use Case 2: Start a delicate wash cycle on a washer

1. The user scans the washer panel with the app.
2. TouchMap reads the labels, identifies the cycle controls, and figures out how the panel is grouped.
3. The user says, "Start delicate wash."
4. The app figures out which controls matter for that goal, such as the cycle selector and `Start`.
5. It gives step-by-step spoken guidance, for example: move to the cycle area, select `Delicates`, then press `Start`.
6. If the user wants more context first, they can use Explore Mode to ask something like "Describe the cycle options area."
7. If a control is still hard to find, TouchMap can guide the user more precisely instead of making them start over.

## Images of the App

If any of the screenshots do not render here, you can open the same image files directly in `app_images/`.

### Home Screen

Home Screen

### Point Camera at Control Panel

Point Camera at Control Panel

### Processing Control Panel Image

Processing Control Panel Image

### Finished Processing Options Available

Finished Processing Options Available

### Finished Processing Options Available 2

Finished Processing Options Available 2

### Task Mode Screen

Task Mode Screen

### Task Mode Step 1

Task Mode Step 1

### Task Mode Live Feedback

Task Mode Live Feedback

### Locate Mode Step 1

Locate Mode Step 1

### Locate Mode Live Feedback

Locate Mode Live Feedback

### Explore Mode

Explore Mode

For more detail, see the numbered documents in `docs/`.