import sys
import time
import argparse
from fairmotion_utils import constants
from vive.track import ViveTrackerModule
from IPython import embed
from render_argparse import *
from vive_visualizer import ViveTrackerViewer
from fairmotion_vis import camera
from fairmotion_ops import conversions, math as fairmotion_math
import numpy as np

def parse_arguments():
    parser = argparse.ArgumentParser(description="Vive Tracker Pose Data Display")
    parser.add_argument("-f", "--frequency", type=float, default=30.0,
                        help="Frequency of tracker data updates (in Hz). Default: 30 Hz")
    return parser.parse_args()

def print_tracker_data(tracker, interval):
    # Continuously print tracker pose data at the specified interval
    while True:
        start_time = time.time()

        # Get pose data for the tracker device and format as a string
        pose_data = " ".join(["%.4f" % val for val in tracker.get_pose_euler()])

        # Print pose data in the same line
        print("\r" + pose_data, end="")

        # Calculate sleep time to maintain the desired interval
        sleep_time = interval - (time.time() - start_time)

        # Sleep if necessary
        if sleep_time > 0:
            time.sleep(sleep_time)

class ViveTrackerUpdater():
    def __init__(self):
        self.vive_tracker_module = ViveTrackerModule()
        self.vive_tracker_module.print_discovered_objects()

        self.fps = 30
        self.device_key = "tracker"
        self.tracking_devices = self.vive_tracker_module.return_selected_devices(self.device_key)
        self.tracking_result = []

        # TODO make first frame comes to [0, 1, 0]
        self.is_first_frame = False
        self.origin = constants.eye_T()
        self.origin[:3,3] = np.array([0.0,1.0,0.0])
        self.origin_inv = constants.eye_T()

    # TODO add fps (not sleeping)
    def update(self, print=False):
        self.tracking_result = [self.origin_inv @ self.tracking_devices[key].get_T() for key in self.tracking_devices]
        if not self.is_first_frame:
            first_pos = self.tracking_result[0]
            first_pos[:3,:3] = constants.eye_R() # if flip rotation, env axis flips too
            self.origin_inv = self.origin @ fairmotion_math.invertT(first_pos)
            self.is_first_frame = True
        if print:
            for r in self.tracking_result:
                print(f"\r{r}", end="")
                
    def get_current_info(self):
        return self.tracking_result

def main(args):
    cam = camera.Camera(
        pos=np.array(args.camera_position),
        origin=np.array(args.camera_origin),
        vup=np.array([0,1,0]),
        fov=45.0,
    )
    viewer = ViveTrackerViewer(
        v_track_updater=ViveTrackerUpdater(),
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
