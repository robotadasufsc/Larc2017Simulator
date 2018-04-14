import cv2
from interface import RobotInterface
from input.keylistener import KeyListener
from opencvpos import OpencvPos
from navigator import Navigator
import sys

def paint_tag(img, tag_image, tag_detec):
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.polylines(img, [points], True, (0, 255, 255))
    tag_image = cv2.cvtColor(tag_image, cv2.COLOR_GRAY2RGB)
    tag_detec = cv2.cvtColor(tag_detec, cv2.COLOR_GRAY2RGB)
    img[0:tag_image.shape[1], img.shape[0] - tag_image.shape[0]:img.shape[0]] = tag_image
    img[tag_image.shape[1]:tag_image.shape[1] + tag_detec.shape[1],
    img.shape[0] - tag_image.shape[0]:img.shape[0]] = tag_detec
    return img

interface = RobotInterface()
opencvpos = OpencvPos()

interface.gripper.move((0, 0, 0.02), False)
keys = KeyListener()
navigator = Navigator(interface)

manual_mode = False

while True:
    img = interface.get_image_from_camera()
    sensors = interface.read_sensors()
    tag_angle = None
    tag_distance = None
    tag_name = None
    tag_image = None
    try:
        perc, tag_name, tag_image, tag_detec, points, tag_angle, tag_distance = opencvpos.get_position_from_image(img)
        img = paint_tag(img, tag_image, tag_detec)
        print(tag_angle, tag_distance)

    except Exception as e:
        import traceback
        print('Error in opencvpos!', e)
        traceback.print_exc(file=sys.stdout)
        pass

    cv2.imshow("target", img)
    ch = cv2.waitKey(5) & 0xFF

    left_speed = 0
    right_speed = 0
    speed = 3

    if ch == 27:
        break

    if manual_mode:
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
    else:
        navigator.iterate(tag_name, tag_angle, tag_distance, sensors, tag_image)

interface.stop()
cv2.destroyAllWindows()
