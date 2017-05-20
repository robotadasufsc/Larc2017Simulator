__author__ = 'will'
import numpy as np
from vreptest import vrep

class RobotInterface():
    """
    This is responsible for interfacing with the simulated robot
    """

    def __init__(self):
        vrep.simxFinish(-1)  # just in case, close all opened connectionsS
        self.clientID = vrep.simxStart("127.0.0.1", 19997, True, True, 5000,5)

        vrep.simxStopSimulation(self.clientID, vrep.simx_opmode_oneshot)
        vrep.simxStartSimulation(self.clientID, vrep.simx_opmode_oneshot)

        vrep.simxSynchronous(self.clientID, False)
        print("connected with id ", self.clientID)

        self.left_wheel = None
        self.right_wheel = None
        self.camera = None

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

    def setup(self):
        if self.clientID != -1:
            errorCode, handles, intData, floatData, array = vrep.simxGetObjectGroupData(
                self.clientID,
                vrep.sim_appobj_object_type,
                0,
                vrep.simx_opmode_oneshot_wait)
            data = dict(zip(array, handles))
            self.camera = [value for key, value in data.items() if "Vision" in key][0]
            self.left_wheel = [value for key, value in data.items() if "fl_wheel_joint" in key][0]
            self.right_wheel = [value for key, value in data.items() if "fr_wheel_joint" in key][0]
            vrep.simxGetVisionSensorImage(self.clientID, self.camera, 1, vrep.simx_opmode_streaming)
