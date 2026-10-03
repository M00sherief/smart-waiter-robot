#!/bin/bash
# usage: ./make_stub.sh <package> <node_name>
WS=~/gradprojWORKSPACE
PKG=$1
NODE=$2
DIR=$WS/src/$PKG/$PKG
CLASS=$(echo $NODE | sed -r 's/(^|_)([a-z])/\U\2/g')

cat > $DIR/$NODE.py << EOF
import rclpy
from rclpy.node import Node


class $CLASS(Node):
    def __init__(self):
        super().__init__('$NODE')
        self.get_logger().info('$NODE started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = $CLASS()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
EOF

sed -i "/console_scripts/a\\            '$NODE = $PKG.$NODE:main'," $WS/src/$PKG/setup.py
echo "Created $NODE in $PKG"
