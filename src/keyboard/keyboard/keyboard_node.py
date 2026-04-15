#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from keyboard_input_msgs.msg import PressedKeys


class KeyboardNode(Node):
    def __init__(self) -> None:
        super().__init__("keyboard_node")

        self.declare_parameter("topic_name", "key")
        self.declare_parameter("publish_hz", 20.0)
        self.declare_parameter("backend", "evdev")
        self.declare_parameter("device_path", "")
        self.declare_parameter("log_output", False)

        topic_name = str(self.get_parameter("topic_name").value)
        publish_hz = float(self.get_parameter("publish_hz").value)
        backend = str(self.get_parameter("backend").value).strip().lower()
        device_path = str(self.get_parameter("device_path").value).strip()
        self._log_output = bool(self.get_parameter("log_output").value)

        if publish_hz <= 0.0:
            self.get_logger().warn("publish_hz must be > 0.0．20.0 Hz に戻します．")
            publish_hz = 20.0

        self._pub = self.create_publisher(PressedKeys, topic_name, 10)
        self._reader = self._create_reader(backend, device_path)
        self._timer = self.create_timer(1.0 / publish_hz, self._timer_cb)

        self.get_logger().info(
            f"keyboard_node started．topic={topic_name}, publish_hz={publish_hz}, backend={backend}"
        )

    def _create_reader(self, backend: str, device_path: str):
        if backend == "evdev":
            if device_path == "":
                raise RuntimeError(
                    "evdev backend requires device_path．"
                    "Example: --ros-args -p backend:=evdev -p device_path:=/dev/input/event3"
                )
            from .readers.evdev_reader import EvdevKeyboardReader
            return EvdevKeyboardReader(
                device_path=device_path,
                logger=self.get_logger(),
            )

        if backend == "pygame":
            from .readers.pygame_reader import PygameKeyboardReader
            return PygameKeyboardReader(
                logger=self.get_logger(),
            )

        raise RuntimeError(
            f"Unknown backend: {backend}. Supported backends are: evdev, pygame"
        )

    def _timer_cb(self) -> None:
        msg = PressedKeys()
        msg.keys = self._reader.snapshot()
        self._pub.publish(msg)

        if self._log_output:
            self.get_logger().info(f"pressed_keys: {msg.keys}")

    def shutdown(self) -> None:
        self._reader.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = KeyboardNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()