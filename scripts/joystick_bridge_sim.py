#!/usr/bin/env python3
"""
Jembatan joystick M5Stack -> ROS 2 (khusus simulasi Gazebo).
Membaca baris "JOY:<lin>,<ang>,<estop>,<fresh>" dari M5Stack lewat USB serial.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial


def parse_joy_line(line):
    """'JOY:50,-20,0,1' -> (50, -20, 0, 1); None jika format salah."""
    if not line.startswith('JOY:'):
        return None
    parts = line[4:].split(',')
    if len(parts) != 4:
        return None
    try:
        lin, ang, stop, fresh = (int(p) for p in parts)
    except ValueError:
        return None
    return lin, ang, stop, fresh


def joy_to_twist(lin, ang, stop, fresh, max_linear, max_angular, invert_turn):
    """
    Kembalikan (linear_x, angular_z, moving).
    moving=False berarti tidak ada yang perlu diterbitkan.
    """
    moving = bool(fresh) and (stop == 1 or lin != 0 or ang != 0)
    if not moving or stop == 1:
        return 0.0, 0.0, moving
    sign = 1.0 if invert_turn else -1.0
    lin = max(-100, min(100, lin))
    ang = max(-100, min(100, ang))
    return lin / 100.0 * max_linear, sign * ang / 100.0 * max_angular, True


class JoystickBridge(Node):
    def __init__(self):
        super().__init__('joystick_bridge_sim')

        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', 115200)
        # max_linear diubah ke -0.5 agar arah maju/mundur joystick tidak terbalik
        self.declare_parameter('max_linear', -0.5)    
        self.declare_parameter('max_angular', 1.0)   
        self.declare_parameter('invert_turn', False)
        # Default topic diubah langsung ke controller Gazebo (bypass mode)
        self.declare_parameter('topic', '/diff_cont/cmd_vel_unstamped')

        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value
        self.max_linear = self.get_parameter('max_linear').value
        self.max_angular = self.get_parameter('max_angular').value
        self.invert_turn = self.get_parameter('invert_turn').value
        topic = self.get_parameter('topic').value

        try:
            self.ser = serial.Serial(port, baud, timeout=0.05)
            self.get_logger().info(f"Terhubung ke M5Stack di {port}")
        except Exception as e:
            self.get_logger().error(f"Gagal membuka port serial: {e}")
            exit(1)

        self.pub = self.create_publisher(Twist, topic, 10)
        self.was_moving = False
        self.create_timer(0.02, self.poll_serial)  # 50 Hz

    def poll_serial(self):
        latest = None
        try:
            while self.ser.in_waiting:
                raw = self.ser.readline()
                if not raw.endswith(b'\n'):
                    continue  # baris terpotong
                try:
                    line = raw.decode('utf-8').strip()
                except UnicodeDecodeError:
                    continue
                parsed = parse_joy_line(line)
                if parsed is not None:
                    latest = parsed
        except Exception as e:
            self.get_logger().warn(f"Error membaca serial: {e}")
            return

        if latest is None:
            return

        lin, ang, stop, fresh = latest
        self.get_logger().info(
            f"JOY lin={lin} ang={ang} estop={stop} fresh={fresh}",
            throttle_duration_sec=1.0)

        x, z, moving = joy_to_twist(lin, ang, stop, fresh,
                                    self.max_linear, self.max_angular, self.invert_turn)
        if moving:
            msg = Twist()
            msg.linear.x = x
            msg.angular.z = z
            self.pub.publish(msg)
            self.was_moving = True
        elif self.was_moving:
            self.pub.publish(Twist())  # satu pesan nol, lalu lepas prioritas
            self.was_moving = False


def main(args=None):
    rclpy.init(args=args)
    node = JoystickBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(node, 'ser') and node.ser.is_open:
            node.ser.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()