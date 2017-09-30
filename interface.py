__author__ = 'will'
import numpy as np
from vreptest import vrep
import time
from math import sqrt

class Gripper:
    """
    Represents the robot's gripper, responsible for moving it.
    """

    def __init__(self, clientID):
        self.clientID = clientID
        _, self.gripper_camera = vrep.simxGetObjectHandle(clientID, "gripper_cam",
                                                          vrep.simx_opmode_blocking)
        _, self.gripper_target = vrep.simxGetObjectHandle(clientID, "gripper_target",
                                                          vrep.simx_opmode_blocking)
        _, self.gripper_resting= vrep.simxGetObjectHandle(clientID, "gripper_resting_position",
                                                          vrep.simx_opmode_blocking)

    def move(self, coords, incremental=True):
        """
        Moves the gripper to (left, away, up)
        :param coords: position to move to(if not incremental) or to increase (if incremental)
        :param incremental: relative to actual position
        """
        if incremental:
            vrep.simxSetObjectPosition(self.clientID, self.gripper_target, self.gripper_target,
                                       coords, vrep.simx_opmode_oneshot)
        else:
            vrep.simxSetObjectPosition(self.clientID, self.gripper_target, self.gripper_resting,
                                       coords, vrep.simx_opmode_oneshot)


class RobotInterface():
    """
    This is responsible for interfacing with the simulated robot
    """

    def __init__(self):
        vrep.simxFinish(-1)  # just in case, close all opened connectionsS
        self.clientID = vrep.simxStart("127.0.0.1", 19997, True, True, 5000,5)

        vrep.simxStopSimulation(self.clientID, vrep.simx_opmode_oneshot)
        time.sleep(0.5)
        vrep.simxStartSimulation(self.clientID, vrep.simx_opmode_oneshot)

        vrep.simxSynchronous(self.clientID, False)
        print("connected with id ", self.clientID)

        self.left_wheel = None
        self.right_wheel = None
        self.camera = None
        self.gripper = None

        self.proximity = {'fr': None,
                          'fl': None,
                          'rr': None,
                          'rl': None}

        self.setup()
        self.lastimageAcquisitionTime = 0

    def finish_iteration(self):
        vrep.simxSynchronousTrigger(self.clientID)

    def set_right_speed(self, speed):
        """
        seta velocidade da roda direita
        :param speed:
        :return:
        """
        vrep.simxSetJointTargetVelocity(self.clientID, self.right_wheel, speed,
                                        vrep.simx_opmode_oneshot)

    def set_left_speed(self, speed):
        """
        seta velocidade da roda esquerda
        :param speed:
        :return:
        """
        vrep.simxSetJointTargetVelocity(self.clientID, self.left_wheel, speed,
                                        vrep.simx_opmode_oneshot)

    def _read_camera(self):
        data = vrep.simxGetVisionSensorImage(self.clientID, self.camera, 1, vrep.simx_opmode_buffer)
        if data[0] == vrep.simx_return_ok:
            return data
        return None

    def get_image_from_camera(self):
        """
        Loads image from camera.
        :return:
        """
        img = None
        while not img:  img = self._read_camera()
        size = img[1][0]
        img = np.flipud(np.array(img[2], dtype='uint8').reshape((size, size)))

        return img

    def get_position_from_handle(self, handle):
        """
        Return [position, orientation] of handle
        :param handle:
        :return:
        """
        pos = [[],[]]
        _, pos[0] = vrep.simxGetObjectPosition(self.clientID, handle, - 1, vrep.simx_opmode_streaming)
        _, pos[1] = vrep.simxGetObjectOrientation(self.clientID, handle, - 1, vrep.simx_opmode_streaming)
        return pos

    def stop(self):
        vrep.simxStopSimulation(self.clientID, vrep.simx_opmode_oneshot_wait)

    def read_sensors(self):
        """
        Reads all infrared sensors
        Returns a dictionary: { sensor: (Bool detected, detectedDistance)}
        """
        ret = {}
        for sensor, handle in self.proximity.items():
            _, detectionState, position, _, _  = vrep.simxReadProximitySensor(self.clientID, handle, vrep.simx_opmode_oneshot_wait)
            if not detectionState:
                position = (0, 0, 0)
            distance = sqrt(sum([coord**2 for coord in position]))
            ret[sensor] = (detectionState, distance)
        return ret

    def setup(self):
        if self.clientID != -1:
            _, self.camera = vrep.simxGetObjectHandle(self.clientID, "Vision_sensor", vrep.simx_opmode_blocking)
            _, self.left_wheel = vrep.simxGetObjectHandle(self.clientID, "fl_wheel_joint", vrep.simx_opmode_blocking)
            _, self.right_wheel = vrep.simxGetObjectHandle(self.clientID, "fr_wheel_joint", vrep.simx_opmode_blocking)

            for sensor in ['fr','fl','rr','rl']:
                _, handle = vrep.simxGetObjectHandle(self.clientID, "{0}_proximity".format(sensor), vrep.simx_opmode_blocking)
                self.proximity[sensor] = handle

            vrep.simxGetVisionSensorImage(self.clientID, self.camera, 1, vrep.simx_opmode_streaming)
            self.gripper = Gripper(self.clientID)