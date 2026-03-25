import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, SetEnvironmentVariable


def generate_launch_description():
    pkg_share = get_package_share_directory('industrial_zone')
    world_file = os.path.join(pkg_share, 'worlds', 'industrial_zone.world')

    gui_arg = DeclareLaunchArgument(
        'gui', default_value='true',
        description='Launch Gazebo GUI'
    )

    # XDG_RUNTIME_DIR is required for Gazebo Transport (ZeroMQ)
    # to create communication sockets between server and GUI.
    set_xdg_runtime_dir = SetEnvironmentVariable(
        name='XDG_RUNTIME_DIR',
        value='/tmp/runtime-root'
    )

    launch_gazebo = ExecuteProcess(
        cmd=['gz', 'sim', world_file, '-r', '-v', '4'],
        output='screen',
        additional_env={
            'XDG_RUNTIME_DIR': '/tmp/runtime-root',
        }
    )

    return LaunchDescription([
        gui_arg,
        set_xdg_runtime_dir,
        launch_gazebo,
    ])
