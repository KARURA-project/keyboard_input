# keyboard (ROS2)

## Overview

This package provides a ROS2 node for keyboard input.

It supports multiple simultaneous key presses and continuously publishes
the current set of pressed keys as a ROS2 topic.

---

## Features

- Multi-key (simultaneous) input support
- Key hold (press-and-hold) detection
- Backend switching:
  - `evdev` (recommended for native Linux)
  - `pygame` (for development / virtual environments)
- Simple ROS2 integration

---

## Supported Environments

| Environment            | Backend |
|------------------------|---------|
| Native Ubuntu / Linux  | evdev   |
| Raspberry Pi           | evdev   |
| UTM / Virtual Machine  | pygame  |

---

## Installation

```bash
cd ~/your_ws
colcon build
source install/setup.bash
```

---

## Dependencies

### evdev (for native Linux)

```bash
sudo apt install python3-evdev
```

### pygame (for development)

```bash
pip install pygame
```

---

## Usage

### evdev (recommended for real robot / native Linux)

```bash
ros2 run keyboard keyboard_node \
  --ros-args \
  -p backend:=evdev \
  -p device_path:=/dev/input/event3
```

> Note: You must specify the correct input device.

### pygame (recommended for development / VM)

```bash
ros2 run keyboard keyboard_node \
  --ros-args \
  -p backend:=pygame
```

> A small window will appear. Make sure it has focus to capture input.

### Enable Debug Logging

```bash
ros2 run keyboard keyboard_node \
  --ros-args \
  -p backend:=pygame \
  -p log_output:=true
```

---

## Topic

### `/keyboard/pressed_keys`

**Type:**

```text
keyboard_input_msgs/msg/PressedKeys
```

**Content:**

```yaml
keys: ["w", "a", "shift"]
```

---

## Parameters

| Parameter    | Type   | Description |
|--------------|--------|-------------|
| backend      | string | `evdev` or `pygame` |
| device_path  | string | Required for `evdev` |
| publish_hz   | float  | Publish frequency (default: 20.0) |
| topic_name   | string | Output topic |
| log_output   | bool   | Enable debug logs |

---

## Backend Details

### evdev

- Uses `/dev/input/eventX`
- High reliability
- Supports true simultaneous input
- Requires proper permissions

### pygame

- Uses GUI window input
- Works in virtual environments (UTM, etc.)
- Requires window focus
- Intended for development use

---

## Troubleshooting

### Permission denied (`/dev/input/eventX`)

```bash
sudo usermod -aG input $USER
```

Then log out and log in again.

### No input detected (pygame)

- Make sure the window is focused
- Click on the window before typing

### Cannot find correct device

```bash
ls /dev/input
```

```bash
sudo evtest /dev/input/eventX
```

---

## Notes

- Many keyboards support only up to 6 simultaneous keys (hardware limitation)
- For reliable operation, use native Linux with `evdev`
- `pygame` backend is intended for development only
