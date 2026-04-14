from setuptools import find_packages, setup

package_name = 'keyboard'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[
        'setuptools',
        'evdev',
        'pygame',
    ],
    zip_safe=True,
    maintainer='karura',
    maintainer_email='karura@todo.todo',
    description='Keyboard input node for ROS 2',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'keyboard_node = keyboard.keyboard_node:main',
        ],
    },
)