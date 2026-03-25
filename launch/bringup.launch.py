"""
Wrapper launch file for robotnik_simulation_bringup/bringup_complete.launch.py
pre-configured for the industrial_zone world with rbkairos.

Defaults are loaded from config/bringup.yaml — edit that file to change
the configuration without touching this launch file.

CLI arguments (key:=value) override YAML values.

Map loading: the bringup starts localization with the default demo_map,
then a delayed service call loads the actual map from this package.
This follows the workflow described in the robotnik_simulation README.

Usage:
    ros2 launch industrial_zone bringup.launch.py
    ros2 launch industrial_zone bringup.launch.py use_gui:=false
"""

import os
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    ExecuteProcess,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    industrial_zone_share = get_package_share_directory('industrial_zone')
    bringup_share = get_package_share_directory('robotnik_simulation_bringup')

    # Load defaults from YAML config
    config_file = os.path.join(industrial_zone_share, 'config', 'bringup.yaml')
    with open(config_file, 'r') as f:
        cfg = yaml.safe_load(f) or {}

    # world_path: use YAML override if present, otherwise resolve from package
    default_world = cfg.get(
        'world_path',
        os.path.join(industrial_zone_share, 'worlds', 'industrial_zone.world'),
    )

    # Map: resolve absolute path from map_package + map_path
    map_package = cfg.get('map_package', 'mi_zona_industrial_description')
    map_path = cfg.get('map_path', 'maps/zona_industrial/Mapa_v2.yaml')
    map_absolute = os.path.join(get_package_share_directory(map_package), map_path)

    # Declare arguments — YAML values are the defaults, CLI overrides them
    declared_args = [
        DeclareLaunchArgument('robot',
                              default_value=str(cfg.get('robot', 'rbkairos')),
                              description='Robot name'),
        DeclareLaunchArgument('robot_model',
                              default_value=str(cfg.get('robot_model', 'rbkairos_plus')),
                              description='Robot model variant'),
        DeclareLaunchArgument('low_performance_simulation',
                              default_value=str(cfg.get('low_performance_simulation', False)).lower(),
                              description='Enable low performance mode'),
        DeclareLaunchArgument('world_path',
                              default_value=str(default_world),
                              description='Path to the world file'),
    ]

    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_share, 'launch', 'bringup_complete.launch.py')
        ),
        launch_arguments={
            'robot': LaunchConfiguration('robot'),
            'robot_model': LaunchConfiguration('robot_model'),
            'low_performance_simulation': LaunchConfiguration('low_performance_simulation'),
            'world_path': LaunchConfiguration('world_path'),
        }.items(),
    )

    # Load our map via service call after localization is up.
    # Localization starts at T+10s in bringup_complete, so T+13s gives it time to initialize.
    load_map = TimerAction(
        period=13.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'ros2', 'service', 'call',
                    '/robot/map_server/load_map',
                    'nav2_msgs/srv/LoadMap',
                    f'{{"map_url": "{map_absolute}"}}',
                ],
                output='screen',
            )
        ],
    )

    return LaunchDescription(declared_args + [bringup, load_map])
