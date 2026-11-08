#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial

class SerialToCmdVel(Node):
    def __init__(self):
        super().__init__('serial_to_cmd_vel')
        
        # Konfigurasi Port Serial USB M5Stack Core Grey
        self.port_name = '/dev/ttyUSB0'
        self.baud_rate = 115200
        
        try:
            self.ser = serial.Serial(self.port_name, self.baud_rate, timeout=0.1)
            self.get_logger().info(f"Berhasil terhubung ke M5Stack di {self.port_name}")
        except Exception as e:
            self.get_logger().error(f"Gagal membuka port serial: {e}")
            exit(1)

        # Publisher ke topik /cmd_vel untuk dibaca oleh Gazebo
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Timer pembacaan serial (20 Hz)
        self.timer = self.create_timer(0.05, self.read_serial_data)

        # Batas kecepatan virtual di Gazebo
        self.max_linear_vel = 0.5   # meter/detik
        self.max_angular_vel = 1.0  # radian/detik

    def read_serial_data(self):
        if self.ser.in_waiting:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                
                # Format yang diharapkan: "TGTL:...,TGTR:...,RPML:...,RPMR:...,BTN:..."
                if line.startswith("TGTL"):
                    parts = line.split(',')
                    
                    # Ekstrak nilai mentah dari string telemetri
                    tgt_l = float(parts[0].split(':')[1])
                    tgt_r = float(parts[1].split(':')[1])
                    btn_pressed = int(parts[8].split(':')[1])
                    
                    cmd = Twist()

                    # Evaluasi Tombol Emergency Stop
                    if btn_pressed == 1:
                        cmd.linear.x = 0.0
                        cmd.angular.z = 0.0
                        self.publisher_.publish(cmd)
                        return
                    
                    # Reverse Kinematics: (TGTL + TGTR) / 2 = Linear, (TGTL - TGTR) / 2 = Angular
                    raw_lin = (tgt_l + tgt_r) / 2.0
                    raw_ang = (tgt_l - tgt_r) / 2.0

                    # Tambahkan tanda minus (-) di sini untuk membalik arah maju/mundur dan kiri/kanan
                    cmd.linear.x = -((raw_lin / 100.0) * self.max_linear_vel)
                    cmd.angular.z = -((raw_ang / 100.0) * self.max_angular_vel)

                    # Publikasikan perintah ke Gazebo
                    self.publisher_.publish(cmd)
                    
            except IndexError:
                # Mengabaikan error string terpotong (umum saat koneksi serial baru dibuka)
                pass
            except Exception as e:
                self.get_logger().warn(f"Error parsing serial: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = SerialToCmdVel()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Kirim perintah berhenti SAAT context ROS masih aktif secara penuh
        stop_cmd = Twist()
        node.publisher_.publish(stop_cmd)
        node.get_logger().info("Menerima perintah penghentian (Ctrl+C). Menghentikan robot...")
    finally:
        # Tutup port dan hancurkan node secara aman
        if hasattr(node, 'ser') and node.ser.is_open:
            node.ser.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()