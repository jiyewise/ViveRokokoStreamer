from ViveTrackerUpdater import ViveTrackerUpdater
from rokoko.test_connection import RokokoUpdater
from vive_rokoko_visualizer import ViveRokokoTrackerViewer
from fairmotion_vis import camera
from fairmotion_ops import conversions, math as fairmotion_math
from render_argparse import *
import numpy as np


class RokokoDataHelper():
	def __init__(self):
		# self.joints = ['hip', 'spine', 'chest', 'neck', 'head', 'leftShoulder', 'leftUpperArm', 'leftLowerArm', 'leftHand', 'rightShoulder', 'rightUpperArm', 'rightLowerArm', 'rightHand', 'leftUpLeg', 'leftLeg', 'leftFoot', 'leftToe', 'leftToeEnd', 'rightUpLeg', 'rightLeg', 'rightFoot', 'rightToe', 'rightToeEnd', 'leftThumbProximal', 'leftThumbMedial', 'leftThumbDistal', 'leftThumbTip', 'leftIndexProximal', 'leftIndexMedial', 'leftIndexDistal', 'leftIndexTip', 'leftMiddleProximal', 'leftMiddleMedial', 'leftMiddleDistal', 'leftMiddleTip', 'leftRingProximal', 'leftRingMedial', 'leftRingDistal', 'leftRingTip', 'leftLittleProximal', 'leftLittleMedial', 'leftLittleDistal', 'leftLittleTip', 'rightThumbProximal', 'rightThumbMedial', 'rightThumbDistal', 'rightThumbTip', 'rightIndexProximal', 'rightIndexMedial', 'rightIndexDistal', 'rightIndexTip', 'rightMiddleProximal', 'rightMiddleMedial', 'rightMiddleDistal', 'rightMiddleTip', 'rightRingProximal', 'rightRingMedial', 'rightRingDistal', 'rightRingTip', 'rightLittleProximal', 'rightLittleMedial', 'rightLittleDistal', 'rightLittleTip']
		self.left_hand_joint = ['leftHand', 'leftThumbProximal', 'leftThumbMedial', 'leftThumbDistal', 'leftThumbTip', 
							'leftIndexProximal', 'leftIndexMedial', 'leftIndexDistal', 'leftIndexTip', 
							'leftMiddleProximal', 'leftMiddleMedial', 'leftMiddleDistal', 'leftMiddleTip', 
							'leftRingProximal', 'leftRingMedial', 'leftRingDistal', 'leftRingTip', 
							'leftLittleProximal', 'leftLittleMedial', 'leftLittleDistal', 'leftLittleTip' ]
		self.left_hand_parent = [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0, 13, 14, 15, 0, 17, 18, 19]
		self.right_hand_joint = ['rightHand', 'rightThumbProximal', 'rightThumbMedial', 'rightThumbDistal', 'rightThumbTip', 
							'rightIndexProximal', 'rightIndexMedial', 'rightIndexDistal', 'rightIndexTip', 
							'rightMiddleProximal', 'rightMiddleMedial', 'rightMiddleDistal', 'rightMiddleTip', 
							'rightRingProximal', 'rightRingMedial', 'rightRingDistal', 'rightRingTip', 
							'rightLittleProximal', 'rightLittleMedial', 'rightLittleDistal', 'rightLittleTip']
		self.right_hand_parent = [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0, 13, 14, 15, 0, 17, 18, 19]

		self.tracker_offset = {}
		self.tracker_offset['left'] = np.array([0.0,0.0,0.0])
		self.tracker_offset['right'] = np.array([0.0,0.0,0.0])
		self.tracker_idx = {}
		self.tracker_idx['left'] = 0
		self.tracker_idx['right'] = 1
		self.joint_num = len(self.left_hand_joint)

	def get_joint_name_by_idx(self, idx, dir="left"):
		if dir == "left":
			return self.left_hand_joint[idx]
		else:
			return self.right_hand_joint[idx]

	def get_parent_joint_name(self, idx, dir="left"):
		parent_idx = self.left_hand_parent[idx] if dir == "left" else self.right_hand_parent[idx]
		return self.get_joint_name_by_idx(parent_idx)

	def get_joint_pos_by_key(self, rokoko_input, key):
		joint_dict = rokoko_input[key]
		p = np.array([joint_dict['position'][axis] for axis in ['x', 'y', 'z']])
		return p
	
	def get_joint_parent_pos_pair(self, rokoko_input, idx, dir="left"):
		cur_joint_key = self.left_hand_joint[idx] if dir == "left" else self.right_hand_joint[idx]
		parent_idx = self.left_hand_parent[idx] if dir == "left" else self.right_hand_parent[idx]
		if parent_idx == -1:
			return self.get_joint_pos_by_key(rokoko_input, cur_joint_key), None
		parent_key = self.left_hand_joint[parent_idx] if dir == "left" else self.right_hand_joint[parent_idx]
		return self.get_joint_pos_by_key(rokoko_input, cur_joint_key), self.get_joint_pos_by_key(rokoko_input, parent_key)

	def get_palm_pos(self, rokoko_input, dir="left"):
		key_joints = ['leftHand', 'leftIndexProximal', 'leftLittleProximal'] if dir == "left" else  ['rightHand', 'rightIndexProximal', 'rightLittleProximal']
		key_pos = []
		for joint in key_joints:
			joint_dict = rokoko_input[joint]
			p = np.array([joint_dict['position'][axis] for axis in ['x', 'y', 'z']])
			key_pos.append(p)
		midpoint = self.get_triangle_midpoint(key_pos[0], key_pos[1], key_pos[2])
		return midpoint 
	
	def calc_offset(self, rokoko_input, vive_input, dir="left"):
		palm_midpoint = self.get_palm_pos(rokoko_input=rokoko_input, dir=dir)
		p_offset = conversions.T2p(vive_input[self.tracker_idx[dir]]) - palm_midpoint
		self.tracker_offset[dir] = p_offset
		return p_offset

	def get_pos_offset(self, dir="left"):
		return self.tracker_offset[dir]

	def get_triangle_midpoint(self, p1, p2, p3):
		def midpoint_3d(p1, p2):
			return (p1 + p2)/2
		mid1 = midpoint_3d(p1, p2)
		mid2 = midpoint_3d(p1, p3)
		mid3 = midpoint_3d(p2, p3)
		return midpoint_3d(mid1, midpoint_3d(mid2, mid3))

class ViveRokokoUpdater():
	def __init__(self):
		self.rokoko_updater = RokokoUpdater()
		self.vive_tracker_updater = ViveTrackerUpdater()
		self.rokoko_helper = RokokoDataHelper()

		self.rokoko_current_result = None
		self.vive_current_result = []
	
	def update(self):
		self.rokoko_updater.update()
		self.vive_tracker_updater.update()
		self.rokoko_current_result = self.rokoko_updater.get_current_info()
		self.vive_current_result = self.vive_tracker_updater.get_current_info()
	
def main(args):
	updater = ViveRokokoUpdater()
	# Parse command line arguments
	# args = parse_arguments()

	# # Calculate interval based on the specified frequency
	# interval = 1 / args.frequency

	# # Initialize Vive Tracker and print discovered objects
	# v_tracker = ViveTrackerModule()
	# v_tracker.print_discovered_objects()

	# # Print tracker data
	# tracker_1 = v_tracker.devices["tracker_1"]
	# print_tracker_data(tracker_1, interval)

	cam = camera.Camera(
		pos=np.array(args.camera_position),
		origin=np.array(args.camera_origin),
		vup=np.array([0,1,0]),
		fov=45.0,
	)
	viewer = ViveRokokoTrackerViewer(
		updater=updater,
		play_speed=args.speed,
		scale=args.scale,
		thickness=args.thickness,
		render_overlay=args.render_overlay,
		hide_origin=args.hide_origin,
		title="Vive Viewer",
		cam=cam,
		size=(1920, 1280),
	)
	viewer.run()

if __name__ == "__main__":
	args = get_render_args().parse_args()
	main(args)


