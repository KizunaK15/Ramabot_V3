#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
import serial
import threading
import time

class SerialToCmdVel(Node):
    def __init__(self):
        super().__init__('serial_to_cmd_vel')
        
        self.cb_group = ReentrantCallbackGroup()
        self.serial_lock = threading.Lock()
        self.last_send_time = 0.0  # Untuk throttling pengiriman serial
        
        self.port = self.declare_parameter('port', '/dev/ttyUSB0').value
        self.baudrate = self.declare_parameter('baudrate', 115200).value
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.05)
            self.get_logger().info(f"Berhasil membuka serial: {self.port}")
        except Exception as e:
            self.get_logger().error(f"Gagal membuka serial: {e}")
            self.ser = None

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10,
            callback_group=self.cb_group
        )
        
        self.timer = self.create_timer(0.05, self.read_serial_telemetry, callback_group=self.cb_group)

    def cmd_vel_callback(self, msg):
        self.get_logger().info(f"==> Menerima cmd_vel | Linear X: {msg.linear.x:.2f}, Angular Z: {msg.angular.z:.2f}")
        
        current_time = time.time()
        # Batasi pengiriman ke serial maksimal setiap 0.08 detik (~12 Hz) agar buffer M5Stack tidak overflow
        if (current_time - self.last_send_time) < 0.08:
            return
        self.last_send_time = current_time

        if not self.ser or not self.ser.is_open:
            return

        wheel_separation = 0.41  # meter
        wheel_radius = 0.075     # meter

        v_left = msg.linear.x - (msg.angular.z * wheel_separation / 2.0)
        v_right = msg.linear.x + (msg.angular.z * wheel_separation / 2.0)

        rpm_left = (v_left / (2.0 * 3.14159 * wheel_radius)) * 60.0
        rpm_right = (v_right / (2.0 * 3.14159 * wheel_radius)) * 60.0

        # Kirim format yang sangat tegas dengan \r\n
        payload = f"V:{rpm_left:.1f},W:{rpm_right:.1f}\n"

        with self.serial_lock:
            try:
                self.ser.write(payload.encode('utf-8'))
                self.ser.flush()  # Paksa kirim langsung dari buffer OS
            except Exception as e:
                self.get_logger().error(f"Gagal kirim serial: {e}")

    def read_serial_telemetry(self):
        if not self.ser or not self.ser.is_open:
            return

        with self.serial_lock:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line and "TGTL" in line:
                        self.get_logger().info(f"ESP32 Feedback: {line}")
            except Exception as e:
                pass

def main(args=None):
    rclpy.init(args=args)
    node = SerialToCmdVel()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        if node.ser and node.ser.is_open:
            node.ser.write(b"V:0.0,W:0.0\n")
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()