import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'ramabot' 

    view_bot = LaunchConfiguration('view_bot')
    view_map = LaunchConfiguration('view_map')
    path_pkg = os.path.join(get_package_share_directory(package_name))
    rviz_map = os.path.join(path_pkg, 'rviz', 'map.rviz')
    rviz_bot = os.path.join(path_pkg, 'rviz', 'view_bot.rviz')

    node_rviz_map = Node(
        condition=IfCondition(view_map),
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d',rviz_map]
    )

    node_rviz_bot = Node(
        condition=IfCondition(view_bot),
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d',rviz_bot]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'view_bot',
            default_value='false',
            description=''
        ),
         DeclareLaunchArgument(
            'view_map',
            default_value='true',
            description=''
        ),
        node_rviz_map,
        node_rviz_bot
    ])
