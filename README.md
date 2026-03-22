# Smart Mobile Robot Controller and Pick-and-Place Simulator

A Python robotics software project that combines a desktop control interface with a 2D robot simulator. The system demonstrates core software engineering skills relevant to robotics: GUI development, UDP-based inter-process communication, modular code organization, state-driven behavior, and grid-based path planning with A*.

This repository was prepared as a programming portfolio project and is intended to be understandable, runnable locally, and easy to extend.

## Project Overview

The project contains two PySide6 desktop applications:

- a **controller application** that acts as an operator dashboard
- a **simulator application** that visualizes a mobile robot, a mounted arm, a pickable object, a goal zone, and optional obstacles

The controller sends UDP commands to the simulator. The simulator can respond to manual commands or execute an autonomous pick-and-place sequence:

1. move from the start position toward the object
2. pick the object
3. plan a path to the goal using A*
4. avoid obstacles when obstacle mode is enabled
5. deliver and release the object at the goal zone

The current implementation is intentionally compact and presentation-friendly. It is not a physics simulator; instead, it focuses on clear software structure and interactive visualization.

## Features

- Dual-application architecture with separate controller and simulator GUIs
- UDP communication between the controller and simulator
- Modern PySide6 controller dashboard with:
  connect/disconnect workflow, movement buttons, joystick control, speed slider, arm controls, gripper controls, obstacle toggle, simulator reset, and event log
- Simulator with:
  2D occupancy-grid environment, robot visualization, object and goal zone, optional obstacles, path overlay, traveled path, and status/event log
- Continuous joystick-based motion controlled by the speed slider
- Autonomous pick-and-place sequence with visible state transitions
- A* path planning in a dedicated algorithms module
- Randomized obstacle placement on reset for more varied demonstrations
- Basic unit tests for the path planner

## Technologies

- Python
- PySide6
- UDP sockets from Python standard library
- A* path planning on a 2D grid
- `unittest` for lightweight testing

## Project Structure

```text
robot_project/
  README.md
  requirements.txt
  .gitignore
  algorithms/
    __init__.py
    astar.py
  controller/
    __init__.py
    controller_ui.py
    main_controller.py
    udp_client.py
  simulator/
    __init__.py
    environment.py
    main_simulator.py
    robot.py
    simulator_ui.py
    udp_server.py
  tests/
    __init__.py
    test_astar.py
```

### Module Summary

- `controller/`
  Desktop operator interface and UDP command sender.
- `simulator/`
  Robot state, environment, rendering, UDP listener, and execution loop.
- `algorithms/`
  Path planning logic, currently implemented with A*.
- `tests/`
  Basic automated tests for planner behavior.

## How the System Works

### Controller

The controller allows the user to configure a UDP endpoint and connect to the simulator. Until the user clicks `Connect`, motion and automation controls remain disabled. After disconnecting, controls are disabled again until the next connection.

The controller can send commands such as:

- `move_forward`
- `move_backward`
- `turn_left`
- `turn_right`
- `stop`
- `speed:<value>`
- `arm_up`
- `arm_down`
- `grip_open`
- `grip_close`
- `obstacle_on`
- `obstacle_off`
- `auto_pick_and_place`
- `reset_simulation`
- `joystick:<x>:<y>`

### Simulator

The simulator listens on UDP, updates robot state based on incoming commands, and continuously redraws the scene. It supports:

- manual stepped movement using direction buttons
- continuous motion using joystick streaming
- object pickup and release visualization
- obstacle toggling
- autonomous pick-and-place execution

### Path Planning

The autonomous behavior uses A* on a 2D grid. Obstacles are treated as blocked cells, and the planner produces a path from the robot position to the target. The same planner is used for:

- moving to the object
- replanning from the object to the goal

This logic is isolated in `algorithms/astar.py`, which keeps the project structure suitable for future extensions.

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd robot_project
```

### 2. Create a Virtual Environment

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## How to Run

Start the simulator first:

```bash
python simulator/main_simulator.py
```

Then start the controller in a second terminal:

```bash
python controller/main_controller.py
```

Default local settings:

- Host: `127.0.0.1`
- Port: `5005`

Typical usage:

1. launch the simulator
2. launch the controller
3. click `Connect`
4. use manual controls or the joystick
5. toggle obstacle mode if desired
6. trigger `Auto Pick & Place`

## Testing

The repository includes a small automated test module for the A* planner.

Run tests with:

```bash
python -m unittest tests.test_astar
```

## My Contribution

This repository represents my work in:

- designing the project structure and application split
- implementing the controller GUI and simulator GUI in PySide6
- building UDP-based communication between two desktop applications
- implementing grid-based A* path planning
- modeling the robot state, obstacle handling, and autonomous pick-and-place behavior
- refining the project for demo/presentation use with clearer visuals and interaction flow

## Repository Notes

This project is designed to present programming and software design ability rather than full physical realism. The emphasis is on:

- modular Python code
- readable GUI logic
- clear communication between components
- algorithm integration in an interactive application

## Planned Media

The following sections are intentionally left ready for later additions:

### Screenshots

- Controller dashboard
- Simulator environment
- Autonomous pick-and-place sequence

### Demo Video

Demo link: `TBD`

## Future Work

Potential next steps include:

- additional planning algorithms beyond A*
- richer robot kinematics or sensor simulation
- telemetry and data logging
- more advanced environment generation
- packaging for easier distribution
