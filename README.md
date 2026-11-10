<div align="center">

# 🤖 RAMABOT V3
**Robot Autonomous Medical Asistant**

![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-22314E?style=for-the-badge&logo=ros&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![Intel RealSense](https://img.shields.io/badge/Intel_RealSense-D435-0071C5?style=for-the-badge&logo=intel&logoColor=white)

</div>

## 📌 Deskripsi Proyek

**RAMABOT V3** adalah robot resepsionis medis otonom berbasis arsitektur *2-wheel differential drive*. Paket ROS 2 ini mencakup sistem navigasi, simulasi, dan integrasi *hardware* tingkat rendah untuk interaksi pasien. Robot ini memanfaatkan sensor penglihatan mendalam (*depth camera*) untuk pelacakan manusia secara empiris, serta bertindak sebagai *gateway* lokal untuk perangkat diagnostik medis.

## ✨ Fitur Utama

- 🎯 **Human Tracking:** Pelacakan objek dan pasien secara presisi menggunakan **Intel RealSense D435**.
- 🏥 **Medical BLE Gateway:** Integrasi mikrokontroler untuk *parsing* data Bluetooth Low Energy (BLE) secara *real-time* dari perangkat medis seperti **Yuwell YX110 SpO2/BPM, Termometer YE670CR, dan Tensimeter YHW-6**.
- 🗺️ **Autonomous Navigation:** Pemetaan dan navigasi mandiri menggunakan Nav2 dan SLAM Toolbox (didukung *map server* dan *transform tree* yang optimal).
- 💻 **Simulation Ready:** Konfigurasi SDF/URDF lengkap untuk simulasi Gazebo dan visualisasi RViz2 tanpa *crash*.

---

## 🛠️ Arsitektur & Spesifikasi

### Stack Perangkat Lunak

| Komponen | Teknologi |
| :--- | :--- |
| **OS & Framework** | Ubuntu 22.04 + ROS 2 Humble |
| **Middleware** | `rmw_fastrtps_cpp` |
| **Network Security** | `ROS_LOCALHOST_ONLY=1` (isolasi jaringan OTA) |
| **Bahasa Node** | Python 3 & C++ |

### Stack Perangkat Keras

| Komponen | Spesifikasi |
| :--- | :--- |
| **SBC / Host** | Linux Development Node (env `raka01`) |
| **Low-level Controller** | ESP32 (firmware berbasis C++/Arduino, di-*flash* via `esptool`) |
| **Kinematika** | Differential Drive (links: `base_link`, `left_wheel`, `right_wheel`, `laser_frame`) |

---

## 🚀 Instalasi & Persiapan (*Setup*)

### 1. Prasyarat

Pastikan ROS 2 Humble, Nav2, dan Gazebo sudah terinstal. Lalu konfigurasikan *environment* untuk FastRTPS:

```bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_LOCALHOST_ONLY=1
```

### 2. Kloning Repositori

Tarik repositori langsung ke dalam *workspace*:

```bash
mkdir -p ~/ramabot_ws/src
cd ~/ramabot_ws/src
git clone https://github.com/KizunaK15/Ramabot_V3.git ramabot
```

### 3. Kompilasi (*Build*)

```bash
cd ~/ramabot_ws
colcon build --symlink-install
source install/setup.bash
```

---

## 🕹️ Penggunaan (*Usage*)

### Mode Simulasi (Gazebo + RViz2)

Untuk menguji model robot, lingkungan *maze*, dan memastikan *transform tree* berjalan sempurna:

```bash
ros2 launch ramabot sim_launch.py
```

### Navigasi & Pemetaan

Untuk menjalankan node pemetaan SLAM:

```bash
ros2 launch ramabot slam_launch.py
```

### Jembatan Komunikasi Hardware

Untuk menghubungkan perintah gerak ROS 2 ke motor ESP32 (memperbaiki logika kontrol matriks pergerakan):

```bash
ros2 run ramabot serial_to_cmd_vel.py
```
