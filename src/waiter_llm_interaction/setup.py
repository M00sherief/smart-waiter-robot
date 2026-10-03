from setuptools import find_packages, setup

package_name = 'waiter_llm_interaction'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mohamed',
    maintainer_email='sheriefmohamed539@gmail.com',
    description='Smart Autonomous Waiter robot package',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'asl_recognition = waiter_llm_interaction.asl_recognition:main',
            'voice_assistant = waiter_llm_interaction.voice_assistant:main',
            'mission_manager = waiter_llm_interaction.mission_manager:main',
            'order_manager = waiter_llm_interaction.order_manager:main',
        ],
    },
)
