import cv2
from interface import RobotInterface
from input.keylistener import KeyListener


interface = RobotInterface()

interface.gripper.move((0, 0, 0.02), False)
keys = KeyListener()


while True:
    img = interface.get_image_from_camera()
    cv2.imshow("target", img)
    ch = cv2.waitKey(5) & 0xFF

    left_speed = 0
    right_speed = 0
    speed = 3

    if ch == 27:
        break
    if keys['w']:
        left_speed += speed
        right_speed += speed
    if keys['s']:
        left_speed -= speed
        right_speed -= speed
    if keys['a']:
        left_speed -= speed
        right_speed += speed
    if keys['d']:
        left_speed += speed
        right_speed -= speed
    interface.set_left_speed(left_speed)
    interface.set_right_speed(right_speed)

    interface.gripper.move((0, 0, -0.001), False)

interface.stop()
cv2.destroyAllWindows()
