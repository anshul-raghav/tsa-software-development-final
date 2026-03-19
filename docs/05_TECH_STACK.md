# TouchMap Tech Stack

This document explains the technology stack behind `TouchMap`, why each major tool was chosen, and how all of the pieces work together as one system. The goal of this section is not only to list technologies, but to show the technical reasoning behind the project.

For TouchMap, the tech stack mattered because the project had to solve several different problems at once:

- build a mobile app that blind users can operate
- capture and process real panel images
- understand layout and text from those images
- turn that understanding into guidance
- keep the full system modular, testable, and maintainable

Because of that, we did not choose tools randomly. Each part of the stack was selected to solve a specific challenge in the project.

## 1. Full Stack Overview

TouchMap uses a layered stack:

- **Frontend:** React Native + Expo + TypeScript
- **Backend:** Python + FastAPI
- **Image Processing:** OpenCV + NumPy + Pillow
- **OCR:** EasyOCR
- **AI Reasoning:** OpenAI API
- **Data Modeling / Validation:** Pydantic
- **State Flow:** XState
- **Networking:** Axios + HTTP REST endpoints
- **Storage / Persistence:** AsyncStorage on mobile and session/database support on backend
- **Testing:** Pytest + HTTPX
- **Version Control / Development Tools:** GitHub + VSCode

```mermaid
flowchart LR
    A[React Native Mobile App] --> B[Axios API Client]
    B --> C[FastAPI Backend]
    C --> D[OpenCV + NumPy + Pillow]
    C --> E[EasyOCR]
    C --> F[OpenAI API]
    C --> G[Pydantic Validation]
    G --> H[Control Graph + Task Logic]
    H --> A
```

## 2. Frontend Stack

The frontend is responsible for the user experience. Since TouchMap is an accessibility product, this part of the stack had to support a voice-first, mobile-first workflow.

### React Native

We chose **React Native** because TouchMap is a mobile app and needed to run in a smartphone environment. A phone is the right platform for this project because it already includes the camera, audio output, and portability needed for real-world use.

We specifically used React Native because it allowed us to:

- build an actual mobile interface rather than a desktop prototype
- create multiple screens for scan, task, locate, explore, and guidance flows
- keep the experience centered on real device interaction

### Expo

We chose **Expo** because it made mobile development faster and more practical. TouchMap depends on device features such as:

- camera access
- speech output
- haptics
- app testing on mobile hardware

Expo gave us a strong framework for using those capabilities while keeping development more manageable.

### TypeScript

We chose **TypeScript** because TouchMap passes structured data between many parts of the app and backend. TypeScript helped reduce mistakes by making those data shapes explicit.

This was especially valuable for:

- scan responses
- panel data
- task plans
- locate and explore results
- live guidance data

Using typed data improved reliability and made the frontend easier to maintain.

### XState

We chose **XState** to manage the app’s flow because TouchMap is not a simple single-screen app. It moves through a chain of states such as:

- idle
- scanning
- processing
- panel ready
- task mode
- locate mode
- explore mode
- live guidance
- error recovery

XState was a strong choice because it made the app’s behavior explicit instead of relying on loose navigation logic. This supports technical skill because it shows that the app flow was designed as a predictable system.

### Axios

We chose **Axios** for communication between the mobile app and backend because it gave us:

- simple HTTP request handling
- file upload support for scan images
- timeout configuration
- structured error handling

This helped the app interact with the backend in a clean and organized way.

### Expo Speech

We chose **Expo Speech** because voice output is one of the most important parts of the project. The app needs to speak:

- scan guidance
- task steps
- locate directions
- explore descriptions
- error messages

This tool fit the accessibility needs of the project directly.

### Expo Haptics

We chose **Expo Haptics** to add tactile feedback. Since TouchMap supports blind users, spoken output alone is not always enough. Haptic feedback reinforces:

- selections
- success states
- warnings
- errors
- live guidance changes

This choice improved accessibility and made the user experience richer and more reliable.

### AsyncStorage

We chose **AsyncStorage** because a mobile app needs lightweight on-device persistence for temporary session-related information and history. It supports a smoother user experience without requiring complex account infrastructure.

## 3. Backend Stack

The backend is where TouchMap performs most of its deeper processing and decision-making.

### Python

We chose **Python** because it works especially well for:

- image processing
- OCR
- AI integration
- structured backend services
- rapid iteration on complex logic

Python was a strong fit because TouchMap combines accessibility logic with image-based reasoning, and Python has a powerful ecosystem for those needs.

### FastAPI

We chose **FastAPI** because it allowed us to build a clean API with clearly separated routes for:

- scanning
- task planning
- locating
- exploring
- guidance
- health and debug support

FastAPI was a particularly strong choice because it combines:

- strong structure
- good performance
- easy request/response modeling
- automatic validation support through Pydantic

This helped keep the backend organized as the project grew more complex.

### Uvicorn

We used **Uvicorn** to run the FastAPI app. This gave us a practical local development server for testing the backend while building and debugging the project.

## 4. Image and Vision Stack

TouchMap begins with a panel image, so the vision stack is one of the most important parts of the system.

### OpenCV

We chose **OpenCV** because it is a strong tool for real image preprocessing. In TouchMap, OpenCV supports:

- resizing
- basic orientation correction
- contrast improvement
- glare reduction
- panel cropping

This is important because raw camera images are often imperfect. If the system uses the raw image without cleanup, later steps become less reliable.

### NumPy

We chose **NumPy** because image data is ultimately numerical data. NumPy works naturally with OpenCV and supports efficient processing of image arrays.

This is a technical but important choice because it helps the backend handle image transformations cleanly and efficiently.

### Pillow

We chose **Pillow** as a useful fallback and image utility library. It helped support image creation and handling in places where lightweight image operations were needed, including test-related workflows.

## 5. Text Recognition and AI Stack

TouchMap needed more than one kind of intelligence. It needed both raw text reading and higher-level reasoning.

### EasyOCR

We chose **EasyOCR** because the project needs to read visible labels from real control panels. EasyOCR was a strong fit because it can detect text directly from images and return both:

- the text itself
- where that text appears on the panel

That position information matters because TouchMap does not only need to know what a button says. It also needs to know where it is.

### OpenAI API

We chose the **OpenAI API** because some parts of the project require higher-level interpretation rather than simple pattern matching. Specifically, OpenAI is used for:

- turning OCR and image context into a structured panel map
- helping parse ambiguous user requests when rules are not enough
- supporting advanced interpretation in guidance-related workflows

This was a key technical design choice. We did not use AI as an all-purpose black box. Instead, we used it for the specific parts of the project where flexible interpretation is actually needed.

That distinction is important:

- **EasyOCR** reads text
- **OpenAI** interprets meaning and structure
- **Deterministic logic** handles planning and graph reasoning after that

This layered use of AI shows stronger technical skill than simply sending everything to one model and accepting whatever comes back.

## 6. Structured Data and Validation Stack

### Pydantic

We chose **Pydantic** because TouchMap depends on structured data passing through many layers. Pydantic helps validate and organize:

- panel maps
- controls
- spatial edges
- task intents
- task plans
- API requests and responses

This was one of the most important technical decisions in the project. Without strong data modeling, the app would be much harder to debug, test, and extend.

Pydantic also supports a better engineering process because it catches invalid data early instead of allowing silent failures later.

### Pydantic Settings

We used **Pydantic Settings** to manage environment-based configuration such as:

- API prefix
- OpenAI model settings
- OCR settings
- upload directory
- database configuration

This keeps environment-specific settings separate from the application logic, which is a strong software engineering practice.

## 7. Maintainability Choices in the Code

Beyond choosing frameworks, we also made code-level stack decisions that improved readability and maintainability.

- preprocessing thresholds were moved into named constants instead of being left as unexplained numbers
- spatial graph thresholds and layout boundaries were given explicit constant names
- larger service methods were broken into smaller helper methods
- repeated logic was grouped into reusable utility methods

These choices matter for technical skill because they show that the stack was used in a disciplined way. The project is not only functional, but also easier to read, debug, and improve.

## 8. Storage and Persistence Stack

### SQLite + SQLAlchemy + Aiosqlite

The backend includes support for **SQLite**, **SQLAlchemy**, and **Aiosqlite**. These technologies were chosen because they provide a practical path for persistence without requiring a large production database setup.

- **SQLite** is lightweight and appropriate for a student project
- **SQLAlchemy** provides structured database access
- **Aiosqlite** supports asynchronous use in the backend environment

Even though TouchMap currently relies heavily on in-memory session behavior for the demo flow, this stack shows that the project was built with future persistence in mind.

### In-Memory Session Store

We also used an **in-memory session store** because TouchMap needs to keep the current scan, panel map, graph, and mode-related context available during an active user session.

This was a practical design choice for a working prototype because it kept the live flow simple while still supporting a multi-step user experience.

## 9. Testing and Quality Stack

### Pytest

We chose **Pytest** because it is a strong testing framework for Python and made it practical to test:

- domain models
- service logic
- integration routes
- scan workflow behavior

This supports the technical skill of the project because it shows that the backend logic was built in a testable way.

### HTTPX

We used **HTTPX** for integration testing of backend routes. This made it possible to verify API behavior in a realistic but controlled way.

This was important because TouchMap is not only a collection of isolated functions. It is an interacting system, and route-level testing helps confirm that those interactions work correctly.

## 10. Development Workflow Tools

### VSCode

We chose **VSCode** because it provided a practical environment for writing, organizing, and debugging a multi-part codebase with both frontend and backend code.

### GitHub

We chose **GitHub** because TouchMap was built as a team project. GitHub helped us:

- save progress
- share code
- combine work from multiple team members
- maintain a structured repository

This matters because strong technical skill is not only about writing code. It is also about managing a project responsibly.

## 11. How the Stack Worked Together

The real strength of the TouchMap tech stack is not any one tool by itself. It is how the tools connect.

```mermaid
flowchart TD
    A[User scans panel in React Native app]
    A --> B[Expo Camera captures image]
    B --> C[Axios sends image to FastAPI]
    C --> D[OpenCV + NumPy preprocess image]
    D --> E[EasyOCR reads text]
    E --> F[OpenAI interprets layout and structure]
    F --> G[Pydantic validates panel map]
    G --> H[Control graph and task logic build guidance]
    H --> I[FastAPI returns structured result]
    I --> J[XState manages app state]
    J --> K[Expo Speech + Haptics guide the user]
```

This flow shows why the stack demonstrates technical skill:

- each technology has a specific job
- the system moves from raw image input to structured guidance in clear stages
- AI is used carefully, not blindly
- typed models and validation keep the system organized
- the frontend and backend cooperate through a clean API boundary

## 12. Why This Stack Shows Technical Skill

The technical skill of TouchMap comes from how intentionally the stack was chosen and combined.

This project demonstrates technical skill because it:

- combines mobile development, backend engineering, image processing, OCR, AI reasoning, and structured validation
- separates concerns instead of mixing all logic together
- uses different technologies for the jobs they do best
- builds a pipeline where each stage improves the reliability of the next stage
- supports accessibility at the interface level, not just the algorithm level

In other words, the stack is advanced not just because it uses many tools, but because those tools were selected for clear reasons and connected logically.

## 13. Why This Stack Supports Complexity

TouchMap is a complex project because its stack supports multiple layers of behavior:

1. **Physical-world input** through a camera
2. **Image cleanup** through computer vision
3. **Text detection** through OCR
4. **Meaning extraction** through AI interpretation
5. **Structured reasoning** through validation and graph logic
6. **User guidance** through voice, haptics, and mode-based interaction

Each of these layers required different technology choices. The final product works because the stack supports all of them together.

## 14. Final Reflection

The TouchMap tech stack was chosen to do more than make the app functional. It was chosen to make the project technically strong, logically organized, and capable of solving a difficult accessibility problem in a real way.

Every major tool in the stack was selected for a reason:

- mobile tools for accessibility-centered interaction
- backend tools for structure and reliability
- vision tools for panel understanding
- AI tools for interpretation
- validation tools for safety and consistency
- testing tools for software quality

Together, these choices create a system that demonstrates strong technical skill, meaningful complexity, and a thoughtful engineering process.
