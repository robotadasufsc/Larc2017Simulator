import cv2
from interface import RobotInterface

interface = RobotInterface()

interface.set_left_speed(10.0)
interface.set_right_speed(10.0)
interface.gripper.move((0, 0, 0.02), False)

while True:
    img = interface.get_image_from_camera()
    cv2.imshow("target", img)
    ch = cv2.waitKey(5) & 0xFF
    if ch == 27:
        break
    interface.gripper.move((0, 0, -0.001), False)

interface.stop()
cv2.destroyAllWindows()
