
class Navigator():

    states = ["WHERETHEFUCKAMI",]


    def __init__(self, interface):
        self.state = self.states[0]
        self.interface = interface

    def iterate(self, tag_name, tag_angle, tag_distance, sensors):
        print(self.state)
        if self.state == "WHERETHEFUCKAMI":

            # TODO: replace with a decent controller
            if not (tag_name is None):
                if tag_name == "Y.png":

                    # TODO: we need to avoid abruptal direction changes on the wheels, as the escs have
                    # a required timeout

                    if tag_angle is not None and tag_angle[0] > 4:
                        self.interface.set_right_speed(-0.5)
                        self.interface.set_left_speed(0.5)
                    elif tag_angle is not None and tag_angle[0] < -4:
                        self.interface.set_right_speed(0.5)
                        self.interface.set_left_speed(-0.5)
                    else:
                        self.interface.set_right_speed(0.5)
                        self.interface.set_left_speed(0.5)

                    if sensors['fr'][0]:
                        #got to a wall?
                        self.state = "GETHEFUCKINGCUP"

                else:
                    print(tag_name, tag_name is None)
                    print("FUCK, GOT ", tag_name, tag_name is not None, type(tag_name))
                    self.state = "GENERALIZEDCHAOS"


        if self.state == "GETTHEFUCKINGCUP":
            print("should be trying to get the cup, now")