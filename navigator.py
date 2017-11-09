
import cv2

class Navigator():

    states = ["WHERETHEFUCKAMI",]

    def __init__(self, interface):
        self.state = self.states[0]
        self.interface = interface
        self.find_glass = False

    def iterate(self, tag_name, tag_angle, tag_distance, sensors, tag_image):
        print(self.state, tag_name)
        if self.state == "WHERETHEFUCKAMI":

            # TODO: replace with a decent controller
            if not (tag_name is None):
                if tag_name == "Y.png":

                    # TODO: we need to avoid abruptal direction changes on the wheels, as the
                    # escs have a required timeout
                    speed = 1
                    if tag_angle is not None and tag_angle[0] > 4:
                        self.interface.set_right_speed(- speed)
                        self.interface.set_left_speed(speed)
                    elif tag_angle is not None and tag_angle[0] < -4:
                        self.interface.set_right_speed(speed)
                        self.interface.set_left_speed(-speed)
                    else:
                        self.interface.set_right_speed(speed)
                        self.interface.set_left_speed(speed)

                    if sensors['fr'][0]:
                        #got to a wall?
                        #self.state = "GETHEFUCKINGCUP"
                        pass
                    print("distance:", tag_distance)
                else:
                    print(tag_name, tag_name is None)
                    print("FUCK, GOT ", tag_name, tag_name is not None, type(tag_name))
                    self.state = "GENERALIZEDCHAOS"
                    self.interface.set_left_speed(0)
                    self.interface.set_right_speed(0)
                    cv2.imshow("fail", tag_image)
        if self.state == "GETTHEFUCKINGCUP":
            print("should be trying to get the cup, now")