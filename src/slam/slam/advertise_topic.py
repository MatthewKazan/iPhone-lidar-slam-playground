import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, \
    HistoryPolicy
from sensor_msgs.msg import CameraInfo, CompressedImage, Image, PointCloud2
from std_msgs.msg import String

# The RGB-D set the app publishes beside /input_pointcloud when its
# "Upload RGB + depth" toggle is on (lidar_ios_app/lidar/RGBDUploader.swift).
# All four carry the same header stamp per frame. Recorded by
# PointClouds2Subscriber when inputs are being saved; nothing else reads them.
RGBD_TOPICS = {
    '/rgbd/color/compressed': CompressedImage,
    '/rgbd/color/camera_info': CameraInfo,
    '/rgbd/depth': Image,
    '/rgbd/depth/camera_info': CameraInfo,
}



class TopicAdvertiser(Node):
    """
    This needs to exist to advertise the topics that the ios app will use.
    The websocket cannot publish to a topic unless it is advertised first
    """
    def __init__(self):
        super().__init__('topic_advertiser')
        reset_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # Advertise the topic 'input_pointcloud' with the PointCloud2 message type
        self.publisher_ = self.create_publisher(PointCloud2, '/input_pointcloud', 10)
        self.get_logger().info('input_pointcloud topic has been advertised')
        self.publisher1_ = self.create_publisher(String, '/reset', reset_qos)
        self.get_logger().info('reset topic has been advertised')
        self.rgbd_publishers = [self.create_publisher(msg_type, name, 10)
                                for name, msg_type in RGBD_TOPICS.items()]
        self.get_logger().info('rgbd topics have been advertised')


def main(args=None):
    rclpy.init(args=args)
    topic_advertiser = TopicAdvertiser()
    # Stay alive: rosbridge looks the type up in the graph on the app's first
    # publish, and a publisher that has exited is not in the graph.
    try:
        rclpy.spin(topic_advertiser)
    except KeyboardInterrupt:
        pass
    finally:
        topic_advertiser.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()