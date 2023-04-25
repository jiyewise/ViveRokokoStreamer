# Copyright (c) Facebook, Inc. and its affiliates.

import argparse
import numpy as np
import os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from fairmotion_vis import camera, gl_render, glut_viewer
from fairmotion_utils import constants
from fairmotion_ops import conversions
# from fairmotion.data import bvh, asfamc
# from fairmotion.ops import conversions, math, motion as motion_ops
# from fairmotion.utils import utils

from IPython import embed
# import yaml

class ViveRokokoTrackerViewer(glut_viewer.Viewer):

    def __init__(
        self,
        updater,
        # config,
        play_speed=1.0,
        scale=1.0,
        thickness=1.0,
        render_overlay=False,
        hide_origin=False,
        **kwargs,
    ):
        # Load vive tracker updater
        self.updater = updater
        # vis related info
        self.is_update = False
        self.cur_time = 0.0
        self.play_speed = 1.0
        super().__init__(**kwargs)

    def keyboard_callback(self, key):
        if key == b"s":
            self.is_update = True
            self.cur_time = 0.0
            self.time_checker.begin()
        if key == b" ":
            self.is_update = not self.is_update
        else:
            return False
        return True
    
    def render_body_points(self):
        # dict_keys(['hip', 'spine', 'chest', 'neck', 'head', 'leftShoulder', 'leftUpperArm', 'leftLowerArm', 'leftHand', 'rightShoulder', 'rightUpperArm', 'rightLowerArm', 'rightHand', 'leftUpLeg', 'leftLeg', 'leftFoot', 'leftToe', 'leftToeEnd', 'rightUpLeg', 'rightLeg', 'rightFoot', 'rightToe', 'rightToeEnd', 'leftThumbProximal', 'leftThumbMedial', 'leftThumbDistal', 'leftThumbTip', 'leftIndexProximal', 'leftIndexMedial', 'leftIndexDistal', 'leftIndexTip', 'leftMiddleProximal', 'leftMiddleMedial', 'leftMiddleDistal', 'leftMiddleTip', 'leftRingProximal', 'leftRingMedial', 'leftRingDistal', 'leftRingTip', 'leftLittleProximal', 'leftLittleMedial', 'leftLittleDistal', 'leftLittleTip', 'rightThumbProximal', 'rightThumbMedial', 'rightThumbDistal', 'rightThumbTip', 'rightIndexProximal', 'rightIndexMedial', 'rightIndexDistal', 'rightIndexTip', 'rightMiddleProximal', 'rightMiddleMedial', 'rightMiddleDistal', 'rightMiddleTip', 'rightRingProximal', 'rightRingMedial', 'rightRingDistal', 'rightRingTip', 'rightLittleProximal', 'rightLittleMedial', 'rightLittleDistal', 'rightLittleTip'])
        if self.updater.rokoko_current_result:
            offset = self.updater.rokoko_helper.calc_offset(rokoko_input=self.updater.rokoko_current_result, vive_input=self.updater.vive_current_result, dir="left")
            for index in range(self.updater.rokoko_helper.joint_num):
                p, parent_p = self.updater.rokoko_helper.get_joint_parent_pos_pair(self.updater.rokoko_current_result, index, dir="left")
                gl_render.render_sphere(conversions.p2T(p+offset), r=0.003, color=[1,0,0])
                if parent_p is not None:
                    gl_render.render_cone(parent_p+offset, p+offset, r=0.002)

    def render_tracker(self):
        for t in self.updater.vive_current_result:
            gl_render.render_sphere(t, r=0.01)
            gl_render.render_transform(t, scale=0.07, use_arrow=True, line_width=2.0)
    
    def render_callback(self):
        if self.is_update:
            self.updater.update()
        self.render_tracker()
        self.render_body_points()

        gl_render.render_ground(
            size=[100, 100],
            color=[0.8, 0.8, 0.8],
            axis="y",
            origin=True,
            use_arrow=True,
            fillIn=True
        )

    def idle_callback(self):
        if not self.is_update:
            return
        time_elapsed = self.time_checker.get_time(restart=False)
        self.cur_time += self.play_speed * time_elapsed
        self.time_checker.begin()

    def overlay_callback(self):
        # if self.render_overlay:
        w, h = self.window_size
        gl_render.render_text(
            f"Press S to start tracking",
            pos=[0.05 * w, 0.05 * h],
            font=GLUT_BITMAP_TIMES_ROMAN_24,
        )

        gl_render.render_text(
            f"Time: {self.cur_time}",
            pos=[0.05 * w, 0.95 * h],
            font=GLUT_BITMAP_TIMES_ROMAN_24,
        )


def main(args):

    cam = camera.Camera(
        pos=np.array(args.camera_position),
        origin=np.array(args.camera_origin),
        vup=np.array([0,1,0]),
        fov=45.0,
    )
    viewer = ViveTrackerViewer(
        config=config,
        play_speed=args.speed,
        scale=args.scale,
        thickness=args.thickness,
        render_overlay=args.render_overlay,
        hide_origin=args.hide_origin,
        title="Vive & Rokoko Real Time Viewer",
        cam=cam,
        size=(1920, 1280),
    )
    viewer.run()

