__author__ = 'Patrick'


import numpy as np
import cv2

class OpencvPos():
    """
    Black magic of infinity opencv skils and food with lactose
    """

    def __init__(self):
        self.tags_name = ['Y.png', 'L.png', 'AR.png']
        # tags vector
        self.tags = [cv2.imread(name) for name in self.tags_name]
        # matrix vector
        self.matrix_size = 40
        self.mats = [self.create_mat_from_tag(tag, self.matrix_size) for tag in self.tags]
        # camera fov
        self.camera_fov = 60 # degrees


        self.errors = [[100,0] for i in self.tags]
        self.goods = [0 for i in self.tags]
        self.goods.append(0)

        print('tags_name', self.tags_name)
        print('tags', self.tags)
        print('mats', self.mats)

    def create_mat_from_tag(self, img, size):
        # Create a matrix to compare with our candidate
        mat = cv2.cvtColor(img.copy(), cv2.COLOR_RGB2GRAY)
        mat = cv2.resize(mat, (size, size))
        _, mat = cv2.threshold(mat, 127, 255, cv2.THRESH_BINARY)
        return mat

    def calc_row_perc(self, img):
        total_var = 0
        percentage_id = [0 for i in img]
        for i, _ in enumerate(percentage_id):
            percentage_id[i] = np.cov(img[i])
        total_var = np.sum(percentage_id)
        return np.array(percentage_id)/total_var

    def calc_img_eq_perc(self, ori, img):
        rows_perc = [self.calc_row_perc(ori), self.calc_row_perc(img)]
        perc_total = 0
        for i, _ in enumerate(rows_perc[0]):
            if rows_perc[0][i] == 0 or rows_perc[1][i] == 0:
                continue
            perc_total += rows_perc[0][i]*rows_perc[1][i]*(1-np.abs(np.sum(ori[i] - img[i]))/np.sum(ori[i]))
        return perc_total

    def get_position_from_image(self, img):
        # Get the grayscale image and find some edges
        gray = img.copy()
        edged = cv2.Canny(gray, 255/3, 255*2/3)

        # Keep only the most largest edges
        _, cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)

        tagCntVec = []
        # loop over our contours
        for cnt in cnts:
            # approximate the contour
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # A rec have four vertices (great logic champs)
            if len(approx) == 4:
                # We have a winner
                # add it in the vector to choose
                # the winner of the winners !
                tagCntVec.append(approx)

        # If nothing, break the law
        if len(tagCntVec) is 0:
            return (None, None, None, None, None)

        bestPerc = 0
        bestId = 0
        bestTagCnt = None
        bestWarp = None

        # We have our candidates to be the best tag detection
        # time to choose a winner
        for tagCnt in tagCntVec:
            # resize
            pts = tagCnt.reshape(4, 2)

            # create rect
            rect = np.zeros((4, 2), dtype = "float32")

            # the top-left point has the smallest sum whereas the
            # bottom-right has the largest sum
            s = pts.sum(axis = 1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]

            # compute the difference between the points -- the top-right
            # will have the minumum difference and the bottom-left will
            # have the maximum difference
            diff = np.diff(pts, axis = 1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]

            # Black magic of Brazilian capiroto
            # now that we have our rectangle of points, let's compute
            # the width of our new image
            (tl, tr, br, bl) = rect
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))

            # ...and now for the height of our new image
            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))

            # take the maximum of the width and height values to reach
            # our final dimensions
            maxWidth = max(int(widthA), int(widthB))
            maxHeight = max(int(heightA), int(heightB))

            # oh, so cute, a dwarf image !
            # burn it down, isn't a good match
            if (maxHeight*maxWidth < 40*40):
                continue
            #print('Area is: ', maxHeight*maxWidth)

            # construct our destination points which will be used to
            # map the rect to a top-down
            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype = "float32")

            # calculate the perspective transform matrix and warp
            # the perspective to grab the screen
            M = cv2.getPerspectiveTransform(rect, dst)
            warp = cv2.warpPerspective(gray, M, (maxWidth, maxHeight))
            pts = np.array([(0, 0, 0), (200, 0, 0), (0, 200, 0), (200, 200, 0)], dtype=np.float32)
            camera=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)

            # Define the camera distortion coefficients to be zero
            dist_coef = np.zeros(4)

            # Define the camera intrinsic matrix given the spec of based in iPhone camera
            # ps: No, I don't have one. I just need a camera matrix
            # http://ksimek.github.io/2013/08/13/intrinsic/
            # Maybe the problem with the perspective calc can be this poor matrix
            # Blame willian
            camera_matrix = np.float64([[2803, 0, 512/2],
                            [0, 2803, 512/2],
                            [0.0,0.0, 1.0]])

            # We have n points and want the perspective matrix.
            # Run Perspective-n-Point function !
            _, rvec, tvec = cv2.solvePnP(pts, rect, camera_matrix, dist_coef)

            # Calc. the difference between model and measurements
            rot_mat, _ = cv2.Rodrigues(rvec)
            homog_mat = np.concatenate((rot_mat, tvec), axis=1)
            proj_mat = np.dot(camera_matrix, homog_mat)
            image_points, _ = cv2.projectPoints(pts, rvec, tvec, camera_matrix, dist_coef)
            proj_points = image_points.squeeze()

            # This difference is used for restarting estimation from
            # known initial conditions when "bad" estimations occur
            coord_diff = np.linalg.norm(proj_points - rect)

            #TODO need to be tested
            #TODO need to be moved outside this loop
            # and computer with the best match
            # Estimated Euler angles
            _,_,_,rx,ry,rz,euler_angles = cv2.decomposeProjectionMatrix(proj_mat)
            if euler_angles.shape[1] == 1:
                euler_angles = euler_angles.squeeze()

            # Remove some noise
            warp = cv2.resize(warp,(40, 40))
            _, warp = cv2.threshold(warp, 127, 255, cv2.THRESH_BINARY)
            ## We can now compare
            perc = [0 for i in self.tags]
            lperc = 0
            ident = -1
            for i , _ in enumerate(self.tags):
                p = self.calc_img_eq_perc(self.mats[i], warp)
                if p == float('nan') or p == 0:
                    continue
                perc[i] = p*100.0
                if (self.errors[i][0] > perc[i]):
                    self.errors[i][0] = perc[i]
                if (self.errors[i][1] < perc[i]):
                    self.errors[i][1] = perc[i]
                if perc[i] > lperc:
                    lperc = perc[i]
                    ident = i
                    #print(lperc, self.tags_name[ident])

            if ident != -1:
                self.goods[ident] += 1
            else:
                self.goods[-1] += 1

            if bestPerc < lperc:
                bestPerc = lperc
                bestId = ident
                bestTagCnt = tagCnt
                bestWarp = warp

        #Debug code
        # print percentage between mismatches and nondetect tags
        '''
        for i, _ in enumerate(self.errors):
            print(self.tags_name[i], self.goods[i]*100/np.sum(self.goods[:-1]))
        print('None', self.goods[-1]*100/np.sum(self.goods))
        print(bestPerc, self.tags_name[bestId])
        '''

        tag_name = self.tags_name[bestId]
        image_size = img.shape
        image_center = np.divide(image_size,2)
        points = bestTagCnt
        tag_center = np.average(points, axis=0)
        tag_angle = (tag_center - image_center)*self.camera_fov/image_size

        tag_shape = (np.max(points, axis=0) - np.min(points, axis=0))[0]

        tag_angular_size = np.radians(tag_shape*self.camera_fov/image_size/2)

        tag_guesstimated_distance = 10/np.tan(tag_angular_size) # using qrcode size / 2

        return bestPerc, tag_name, self.mats[bestId], bestWarp, bestTagCnt, tag_angle, tag_guesstimated_distance
