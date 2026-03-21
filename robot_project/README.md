# Smart Mobile Robot Controller and Pick-and-Place Simulator

Smart Mobile Robot Controller and Pick-and-Place Simulator is a presentation-ready Python robotics demo with two connected desktop applications: a modern controller dashboard and a 2D robot simulator. The controller sends UDP commands to the simulator, and the simulator executes manual robot actions or a full autonomous pick-and-place sequence with A* path planning and obstacle avoidance.

## GitHub Project Description

Modern Python robotics demo featuring a UDP-based controller dashboard, 2D mobile robot simulator, A* path planning, obstacle avoidance, and a complete pick-and-place workflow.

## Features

- Dual-application architecture: controller GUI and simulator GUI
- UDP socket communication between both apps
- Modern robot-control dashboard with connect section, movement controls, speed slider, joystick pad, arm controls, and gripper controls
- Obstacle mode toggle from the controller with live simulator updates
- 2D environment with robot, arm, object, drop zone, and optional obstacles
- A* path planning on a grid with path visualization
- Autonomous pick-and-place state machine: `idle -> moving_to_object -> picking -> carrying -> moving_to_goal -> releasing -> completed`
- Manual movement commands for quick testing during a demo
- Status and event log panel in the simulator
- Modular code structure so other planning algorithms can be added later

## Architecture

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
    main_controller.py
    controller_ui.py
    udp_client.py
  simulator/
    __init__.py
    main_simulator.py
    simulator_ui.py
    robot.py
    environment.py
    udp_server.py
  assets/
  tests/
    test_astar.py
```

### Main Components

- `controller/`: dashboard UI and UDP client for sending robot commands
- `simulator/`: robot state, environment model, UDP server, animation loop, and rendering
- `algorithms/`: path-planning module with an A* implementation and a planner-friendly interface
- `tests/`: lightweight automated checks for A* behavior

## How UDP Communication Works

The simulator starts a UDP server and listens on a configurable host and port, defaulting to `127.0.0.1:5005`.

The controller uses a UDP client and sends plain-text commands such as:

- `move_forward`
- `move_backward`
- `turn_left`
- `turn_right`
- `stop`
- `speed:60`
- `arm_up`
- `arm_down`
- `grip_open`
- `grip_close`
- `obstacle_on`
- `obstacle_off`
- `auto_pick_and_place`

Because UDP is lightweight and connectionless, it works well for a local interactive robotics demo. The controller "connect" action stores the destination IP and port, and every UI action sends one datagram to the simulator.

## How A* Obstacle Avoidance Works

The simulator models the environment as a 2D occupancy grid. Each cell is either free or blocked. When autonomous mode is triggered:

1. The planner computes a path from the robot position to the object.
2. Once the object is picked, the planner computes a second path from the robot position to the goal zone.
3. If obstacle mode is enabled, obstacle cells are marked as blocked and the planner routes around them.
4. The current planned path is drawn in the simulator to make the decision process visible during the presentation.

The planning logic is isolated in `algorithms/astar.py`, so you can add Dijkstra, RRT, or other planners later without restructuring the whole project.

## Install Dependencies

1. Create and activate a virtual environment.
2. Install the required package:

```bash
pip install -r requirements.txt
```

## How to Run the Simulator

From the `robot_project` directory:

```bash
python simulator/main_simulator.py
```

The simulator window opens first and starts listening for UDP commands.

## How to Run the Controller

Open a second terminal in the same `robot_project` directory:

```bash
python controller/main_controller.py
```

Use the default host `127.0.0.1` and port `5005`, click `Connect`, then test manual commands or launch the full autonomous demo with `Auto Pick & Place`.

## Presentation-Friendly Feature List

- Clean control dashboard with fast UDP command transmission
- Interactive manual drive controls and joystick-style pad
- Toggleable obstacle mode for live path-planning demonstrations
- Autonomous pick-and-place routine with visible state transitions
- Visual robot path history and current A* planned route
- Symbolic arm and gripper animation suitable for teaching and demos

## Demo Flow

For a clean 2-minute presentation:

1. Start the simulator and point out the map, robot, object, goal, and status panel.
2. Start the controller and click `Connect`.
3. Toggle `Obstacle Mode: ON/OFF` to show obstacles appearing in the simulator.
4. Move the robot manually with the direction buttons or joystick pad.
5. Press `Auto Pick & Place` to trigger the full task: robot navigates to object, picks it, replans to the goal, avoids obstacles, and releases the object.
6. Highlight the live path overlay and state transitions in the log.

## Future Improvements

- Add diagonal movement and smoother kinematic motion
- Add SLAM-style map updates and sensor simulation
- Support multiple objects and multiple goal zones
- Add planner selection from the controller
- Add telemetry charts for speed, distance, and command history
- Replace symbolic arm motion with joint-level animation

## Suggested Screenshots and GIF Ideas

- Controller dashboard with all control panels visible
- Simulator showing the robot, object, goal, and displayed path
- Side-by-side screenshot of controller and simulator during autonomous mode
- GIF of obstacle mode turning on and the path changing
- GIF of object pickup, carrying, and release at the goal
