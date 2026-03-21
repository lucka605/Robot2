# Smart Mobile Robot Controller and Pick-and-Place Simulator

A compact Python robotics demo built for presentations, coursework, and local experimentation. The project includes two desktop applications:

- a controller dashboard for sending robot commands over UDP
- a 2D simulator that visualizes motion, path planning, obstacle avoidance, and a full pick-and-place sequence

The result is intentionally simple, visual, and easy to run while still showing core robotics ideas clearly.

## GitHub Project Description

Presentation-ready Python robotics demo with a UDP controller dashboard, 2D robot simulator, A* path planning, obstacle avoidance, and an autonomous pick-and-place workflow.

## Features

- Clean two-window demo: controller on one side, simulator on the other
- UDP-based command flow for local robot-control testing
- Dashboard with connection settings, movement controls, joystick pad, speed slider, arm controls, gripper controls, and obstacle toggle
- 2D simulator with robot, object, goal zone, optional obstacles, path overlay, and status log
- A* path planning on a grid for obstacle-aware navigation
- Autonomous state flow: `idle -> moving_to_object -> picking -> carrying -> moving_to_goal -> releasing -> completed`
- Manual controls for quick interactive demos
- Modular project layout so new planners or behaviors can be added later

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
- `reset_simulation`
- `joystick:<x>:<y>`

Because UDP is lightweight and connectionless, it works well for a local interactive robotics demo. The controller "Connect" action stores the destination IP and port, and each button press sends one datagram to the simulator. The joystick is handled a little differently: while it is held, the controller streams small `joystick:<x>:<y>` updates so the simulator can move smoothly using the selected speed.

## How A* Obstacle Avoidance Works

The simulator models the environment as a 2D occupancy grid. Each cell is either free or blocked. When autonomous mode is triggered:

1. The planner computes a path from the robot position to the object.
2. Once the object is picked, the planner computes a second path from the robot position to the goal zone.
3. If obstacle mode is enabled, obstacle cells are marked as blocked and the planner routes around them.
4. The current planned path is drawn in the simulator to make the decision process visible during the presentation.

The planning logic is isolated in `algorithms/astar.py`, so you can add Dijkstra, RRT, or other planners later without changing the UI or simulator architecture.

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

- Clean controller dashboard with grouped controls and live status feedback
- Smooth robot movement in the simulator for presentation-friendly visuals
- Clear planned path overlay and traveled path history
- Toggleable obstacle mode for live path-planning demonstrations
- Object pickup and release highlighted visually during the autonomous task
- Symbolic arm and gripper animation that is simple, readable, and stable

## Demo Flow

For a clean 2-minute presentation:

1. Start the simulator and point out the map, robot, object, goal, and status panel.
2. Start the controller and click `Connect`.
3. Toggle `Obstacle Mode: ON/OFF` to show obstacles appearing in the simulator.
4. Move the robot manually with the direction buttons or joystick pad.
5. Press `Auto Pick & Place` to trigger the full task: the robot moves to the object, picks it up, replans to the goal, avoids obstacles, and releases it.
6. Highlight the live path overlay and state transitions in the log.

## Future Improvements

- Add diagonal movement and richer kinematic motion
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
