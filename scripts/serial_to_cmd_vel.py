#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial

class SerialToCmdVel(Node):
    def __init__(self):
        super().__init__('serial_to_cmd_vel')
        
        # Konfigurasi Port Serial USB M5Stack Core Grey (diubah ke ttyUSB1)
        self.port_name = '/dev/ttyUSB1'
        self.baud_rate = 115200
        
        try:
            self.ser = serial.Serial(self.port_name, self.baud_rate, timeout=0.1)
            self.get_logger().info(f"Berhasil terhubung ke M5Stack di {self.port_name}")
        except Exception as e:
            self.get_logger().error(f"Gagal membuka port serial: {e}")
            exit(1)

        # 1. SUBSCRIBER: Mendengarkan perintah gerak dari Jetson (Nav2 / Teleop)
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        self.subscription  # Mencegah warning unused variable
        
        # 2. TIMER: Membaca balasan/telemetri dari M5Stack (20 Hz)
        self.timer = self.create_timer(0.05, self.read_serial_feedback)

    def cmd_vel_callback(self, msg):
        """
        Fungsi ini dipanggil setiap kali ada data baru di topik /cmd_vel.
        Tugasnya: Mengubah Twist menjadi string lalu menembakkannya ke M5Stack.
        """
        # Ekstrak nilai kecepatan maju (linear X) dan putar (angular Z)
        v = msg.linear.x
        w = msg.angular.z
        
        # Format perintah sesuai Master Context: "V:0.20,W:-0.10\n"
        command = f"V:{v:.2f},W:{w:.2f}\n"
        
        try:
            # Kirim perintah mentah ke port serial M5Stack
            self.ser.write(command.encode('utf-8'))
            # Aktifkan baris di bawah ini jika Anda ingin melihat log pengiriman (bisa spam terminal)
            # self.get_logger().info(f"Mengirim: {command.strip()}")
        except Exception as e:
            self.get_logger().error(f"Gagal mengirim data serial: {e}")

    def read_serial_feedback(self):
        """
        Fungsi ini membaca umpan balik (odometri/status) dari M5Stack.
        """
        if self.ser.in_waiting:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    # Tampilkan balasan dari ESP32 ke terminal Jetson
                    self.get_logger().info(f"ESP32 Feedback: {line}")
            except UnicodeDecodeError:
                # Abaikan data biner kotor yang masuk
                pass
            except Exception as e:
                self.get_logger().warn(f"Error membaca serial: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = SerialToCmdVel()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Menerima perintah penghentian (Ctrl+C). Menghentikan robot...")
        
        # Kirim perintah V:0.0,W:0.0 ke M5Stack untuk mengerem darurat sebelum node mati
        if hasattr(node, 'ser') and node.ser.is_open:
            node.ser.write(b"V:0.00,W:0.00\n")
            
    finally:
        # Tutup port dan hancurkan node secara aman
        if hasattr(node, 'ser') and node.ser.is_open:
            node.ser.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()