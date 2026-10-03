Arduino Bridge
  PUBLISH:   ToF/Proximity_left
             ToF/Proximity_right
  SUBSCRIBE: CMD_VEL

Camera
  PUBLISH:   Camera/RGB/Raw
             Camera/Depth/Raw
             Camera/DepthPoints

Battery Monitor
  PUBLISH:   Battery/Status

IMU Data
  PUBLISH:   IMU DATA

Audio/IO
  PUBLISH:   Audio/Raw
  SUBSCRIBE: Audio/Output


App Bridge
  PUBLISH:   App/Goal
  SUBSCRIBE: Mission/Status
             Battery/Status

Power Manager
  PUBLISH:   Power/Alert
  SUBSCRIBE: App/Goal
             Battery/Status


Order Manager
  PUBLISH:   Order/Status
  SUBSCRIBE: Order/New

LLM
  PUBLISH:   Order/New
             Speech/Synthesis
  SUBSCRIBE: Speech/Recognize

Speech to Text
  PUBLISH:   Speech/Recognize
  SUBSCRIBE: Audio/Raw

Text to Speech
  PUBLISH:   Audio/Output
  SUBSCRIBE: Speech/Synthesis

Mission Manager
  PUBLISH:   Mission/Status
             INITIAL POSE
  SUBSCRIBE: App/Goal
             Battery/Status
             Power/Alert
             Order/New
             Order/Status
             Speech/Recognize


Local Costmap
  PUBLISH:   LocalCostmap/Costmap
  SUBSCRIBE: ToF/Proximity_left
             ToF/Proximity_right
             Camera/DepthPoints

Global Costmap
  PUBLISH:   GlobalCostmap/Costmap
  SUBSCRIBE: SCAN
             MAP

Planner
  PUBLISH:   PLAN
  SUBSCRIBE: GlobalCostmap/Costmap

Controller
  PUBLISH:   CMD_VEL
  SUBSCRIBE: LocalCostmap/Costmap
             PLAN
             Odom/Filtered

Behavioral Tree Navigator
  PUBLISH:   Pose_Reached
  SUBSCRIBE: AMCL_POSE


Laser Scan
  PUBLISH:   SCAN
  SUBSCRIBE: Camera/DepthPoints

EKF
  PUBLISH:   Odom/Filtered
             TF
  SUBSCRIBE: IMU DATA
             ODOM


AMCL
  PUBLISH:   AMCL_POSE
             PARTICLE CLOUD
             TF
  SUBSCRIBE: SCAN
             MAP
             INITIAL POSE

SLAM_Toolbox
  PUBLISH:   MAP
             TF
  SUBSCRIBE: SCAN
             ODOM

Map Server
  PUBLISH:   MAP
