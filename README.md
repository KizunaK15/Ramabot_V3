<a id="top"></a>

<div align="center">

# 🤖 RAMABOT V3 — Gazebo Simulation

**Robot Autonomous Medical Assistant · Simulation Environment**

![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-22314E?style=for-the-badge&logo=ros&logoColor=white)
![Gazebo](https://img.shields.io/badge/Gazebo-11-FFB800?style=for-the-badge&logo=gazebo&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![WSL2](https://img.shields.io/badge/WSL2-Optimized-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

[📌 Deskripsi](#-deskripsi-proyek) ·
[✨ Fitur](#-fitur-simulasi) ·
[🧰 Prasyarat](#-prasyarat--lingkungan-wsl2) ·
[🚀 Instalasi](#-instalasi--kompilasi-build) ·
[🧭 Runbook](#-runbook-penggunaan-simulasi--navigasi)

</div>

---

## 📌 Deskripsi Proyek

Repositori ini difokuskan pada **Lingkungan Simulasi Gazebo** untuk **RAMABOT V3** (*Robot Autonomous Medical Assistant*). Paket ROS 2 ini menyediakan simulasi lengkap arsitektur *2-wheel differential drive*, sensor LiDAR, serta *stack* pemetaan dan navigasi otonom menggunakan `slam_toolbox` dan `nav2`.

Lingkungan ini dirancang khusus dan telah dioptimasi untuk berjalan lancar di **WSL2 (Ubuntu 22.04)**.

### 🔎 Sekilas

| | |
| :--- | :--- |
| **Platform** | WSL2 · Ubuntu 22.04 |
| **Framework** | ROS 2 Humble |
| **Simulator** | Gazebo 11 |
| **Kinematika** | 2-wheel differential drive |
| **Sensor** | LiDAR (RPLidar A2M8 virtual) |
| **Pemetaan & Navigasi** | `slam_toolbox` · `nav2` |

---

## ✨ Fitur Simulasi

| | Fitur | Detail |
| :---: | :--- | :--- |
| 🏗️ | **URDF/Xacro Modular** | Konfigurasi robot lengkap dengan `ros2_control`, `diff_drive_controller`, dan `joint_state_broadcaster`. |
| 📡 | **Simulasi Sensor** | Integrasi RPLidar A2M8 virtual (`libgazebo_ros_ray_sensor.so`) pada `laser_frame` (konfigurasi *fixed frame* presisi di atas `base_link`). |
| 🎮 | **Teleoperasi ESP-NOW** | Dukungan jembatan joystick dari *hardware* M5Stack Core Grey ke ROS 2 menggunakan node kustom tanpa `twist_mux`. |
| 🗺️ | **SLAM & Navigasi Otonom** | Konfigurasi *tuning* untuk pemetaan `slam_toolbox` (*online async*) dan Nav2 dengan komparasi algoritma Dijkstra / A* dan DWB *Local Planner*. |
| 🚀 | **Optimasi WSL2** | *Bypass* probing audio OpenAL dan konfigurasi *local model* untuk mencegah *crash/freeze* pada `gzserver` saat inisialisasi. |

---

## 🧰 Prasyarat & Lingkungan (WSL2)

### 1. Instal dependensi

Pastikan dependensi berikut telah terinstal di Ubuntu 22.04:

```bash
sudo apt update
sudo apt install -y \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-ros2-control \
  ros-humble-gazebo-ros2-control \
  ros-humble-topic-tools
```

### 2. Atur *environment variables*

Tambahkan baris berikut ke dalam `~/.bashrc` untuk mencegah Gazebo *freeze* di WSL2:

```bash
export ALSOFT_DRIVERS=null
export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:$HOME/.gazebo/models
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_LOCALHOST_ONLY=1
```

> [!NOTE]
> Salin model dasar `sun` dan `ground_plane` ke `~/.gazebo/models` agar Gazebo dapat berjalan secara *offline*.

---

## 🚀 Instalasi & Kompilasi (Build)

```bash
# 1. Buat workspace dan clone repositori
mkdir -p ~/ramabot_ws/src
cd ~/ramabot_ws/src
git clone https://github.com/KizunaK15/Ramabot_V3.git ramabot

# 2. Kompilasi paket
cd ~/ramabot_ws
colcon build --packages-select ramabot --symlink-install
source install/setup.bash
```

---

## 🧭 Runbook: Penggunaan Simulasi & Navigasi

> [!IMPORTANT]
> Jalankan perintah-perintah berikut di **terminal terpisah**. Pastikan Anda selalu menjalankan `source install/setup.bash` di setiap terminal baru.

### 🔄 Alur Singkat

| Langkah | Tujuan | Node / Paket |
| :---: | :--- | :--- |
| **1** | Menjalankan Gazebo & memunculkan robot | `sim_launch.py` |
| **2** | Menjalankan node joystick *(opsional)* | `joystick_bridge_sim.py` |
| **3** | Membuka RViz2 | `rviz2` |
| **4** | Pemetaan labirin | `slam_toolbox` · `map_saver_cli` |
| **5** | Navigasi otonom | `topic_tools relay` · `nav2_bringup` |

---

### 1️⃣ Menjalankan Gazebo & Memunculkan Robot

```bash
ros2 launch ramabot sim_launch.py
```

> [!TIP]
> Tunggu hingga muncul pesan `Successfully spawned entity [ramabot]` dan kedua kontroler aktif.

### 2️⃣ Menjalankan Node Joystick (M5Stack Core Grey)

Jika menggunakan teleoperasi dari M5Stack:

```bash
ros2 run ramabot joystick_bridge_sim.py
```

<details>
<summary><b>🔀 Remap topik (jika diperlukan)</b></summary>

```bash
ros2 run ramabot joystick_bridge_sim.py --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped
```

</details>

### 3️⃣ Membuka RViz2

```bash
ros2 run rviz2 rviz2 --ros-args -p use_sim_time:=true
```

> [!TIP]
> Tambahkan `RobotModel`, `LaserScan`, dan `Map`. Atur **Fixed Frame** ke `odom` untuk pemetaan, atau `map` untuk navigasi.

### 4️⃣ Pemetaan Labirin (*Mapping* dengan SLAM Toolbox)

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
```

Jelajahi labirin menggunakan joystick hingga peta utuh. Setelah selesai, simpan peta:

```bash
mkdir -p ~/ramabot_ws/src/ramabot/maps
ros2 run nav2_map_server map_saver_cli -f ~/ramabot_ws/src/ramabot/maps/maze_map
```

> [!WARNING]
> Matikan node SLAM dan Joystick dengan `Ctrl+C` sebelum lanjut ke navigasi.

### 5️⃣ Navigasi Otonom (Nav2)

Hubungkan perintah `/cmd_vel` langsung ke kontroler roda:

```bash
ros2 run topic_tools relay /cmd_vel /diff_cont/cmd_vel_unstamped
```

Lalu, jalankan *stack* Nav2:

```bash
ros2 launch nav2_bringup bringup_launch.py \
  use_sim_time:=true \
  map:=$HOME/ramabot_ws/src/ramabot/maps/maze_map.yaml \
  params_file:=$HOME/ramabot_ws/src/ramabot/config/nav2_params.yaml
```

Gunakan **2D Pose Estimate** untuk inisialisasi posisi, lalu berikan tujuan dengan **2D Goal Pose** di RViz2.

---

<div align="center">

[⬆️ Kembali ke atas](#top)

</div>