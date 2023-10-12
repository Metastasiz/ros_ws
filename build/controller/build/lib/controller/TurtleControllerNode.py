#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from turtlesim.srv import SetPen
from functools import partial

class TurtleControllerNode(Node):
	def __init__(self):
		super().__init__("turtle_controller")
		self.prev_x_ = 0
		self.pose_subscriber_ = self.create_subscription(
			Pose, "/turtle1/pose", self.pose_callback, 10)
		self.cmd_vel_pub_ = self.create_publisher(
			Twist, "/turtle1/cmd_vel",10)
		self.get_logger().info("Turtle Controller has been started")

	def pose_callback(self, pose: Pose):
		cmd = Twist()
		timeModifer = 1.0
		turnBackDistance = 2.0
		turnBackModifier = 5.0
		maxDistance = 11
		minDistance = 0
		if pose.x > maxDistance - turnBackDistance or pose.x < minDistance + turnBackDistance or pose.y > maxDistance - turnBackDistance or pose.y < minDistance + turnBackDistance:
			cmd.linear.x = 1.0*turnBackModifier*timeModifer
			cmd.angular.z = 0.85*turnBackModifier*timeModifer
		else:
			cmd.linear.x = 5.0*timeModifer
			cmd.angular.z = 0.0*timeModifer
		self.cmd_vel_pub_.publish(cmd)

		if pose.x > (maxDistance-minDistance)/2 and self.prev_x_ <= (maxDistance-minDistance)/2:
			self.prev_x_ = pose.x
			self.get_logger().info("Set color to red")
			self.callservice_set_pen(255,0,0,3,0)
		if pose.x <= (maxDistance-minDistance)/2 and self.prev_x_ > (maxDistance-minDistance)/2:
			self.prev_x_ = pose.x
			self.get_logger().info("Set color to green")
			self.callservice_set_pen(0,255,0,3,0)

	def callservice_set_pen(self, r,g,b,width,off):
		client = self.create_client(
			SetPen, "/turtle1/set_pen")
		while not client.wait_for_service(1.0):
			self.logger.warn("waiting for service...")

		request = SetPen.Request()
		request.r = r
		request.g = g
		request.b = b
		request.width = width
		request.off = off

		future = client.call_async(request)
		future.add_done_callback(partial(self.callback_set_pen))

	def callback_set_pen(self, future):
		try: 
			response = future.result()
		except Exception as e:
			self.get_logger().error("Service call failed: %r" % (e,))

def main(args=None):
	rclpy.init(args=args)
	node = TurtleControllerNode()
	rclpy.spin(node)
	rclpy.shutdown()