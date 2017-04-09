from skimage import io, measure, exposure, transform
from matplotlib import pyplot as plt
from scipy import math
from scipy import ndimage
import numpy as np


def new_get_contours(img_source):
    img_gamma = exposure.adjust_gamma(img_source[:, :, 2], 2.0) < 50
    img_closing = ndimage.morphology.binary_closing(img_gamma, iterations=3, structure=np.ones((5, 5))).astype(np.int)
    contours = measure.find_contours(img_closing, 0.99)
    return img_closing, contours


def new_get_boardless_contours(img_source, ll=0, thickness=5):
    img_boardless_res = erase_line(img_source, ll=ll, thickness=thickness)
    contours = measure.find_contours(img_boardless_res, 0.99)
    return img_boardless_res, contours


def new_detect_boards(contours, too_small=0.00):
    max_w = 0
    max_h = 0
    boards_coords = []
    for c in contours:
        w = max(c[:, 1]) - min(c[:, 1])
        h = max(c[:, 0]) - min(c[:, 0])
        cx = sum(c)[1] / len(c)
        cy = sum(c)[0] / len(c)
        changes_done = False
        if w < max_w * too_small or h < max_h * too_small:
            continue
        for i in range(0, len(boards_coords)):
            # current is inside stored
            bound_left = cx >= boards_coords[i][0] - boards_coords[i][2] / 2
            bound_right = cx <= boards_coords[i][0] + boards_coords[i][2] / 2
            bound_up = cy >= boards_coords[i][1] - boards_coords[i][3] / 2
            bound_down = cy <= boards_coords[i][1] + boards_coords[i][3] / 2
            if bound_left and bound_right and bound_up and bound_down:
                boards_coords[i][4] += 1
                changes_done = True
                break
            # stored is inside current (swap)
            bound_left = boards_coords[i][0] >= cx - w / 2
            bound_right = boards_coords[i][0] <= cx + w / 2
            bound_up = boards_coords[i][1] >= cy - w / 2
            bound_down = boards_coords[i][1] <= cy + w / 2
            if bound_left and bound_right and bound_up and bound_down:
                boards_coords[i][0] = cx
                boards_coords[i][1] = cy
                boards_coords[i][2] = w
                boards_coords[i][3] = h
                boards_coords[i][4] += 1
                changes_done = True
                break
        if not changes_done:
            boards_coords.append([cx, cy, w, h, 0])
        if w > max_w:
            max_w = w
        if h > max_h:
            max_h = h
    res_boards_coords = []
    for b in boards_coords:
        if b[2] < max_w * too_small or b[3] < max_h * too_small:
            continue
        res_boards_coords.append(b)
    return res_boards_coords


def line_eq(line):
    sp, fp = line
    if sp[0] == fp[0]:
        return 'ver', 0
    tangent = float(fp[1] - sp[1]) / (fp[0] - sp[0])
    return tangent, sp[1] - tangent * sp[0]


def line_len(line):
    sp, fp = line
    return math.sqrt((fp[1] - sp[1]) ** 2 + (fp[0] - sp[0]) ** 2)


def erase_line(img_source, ll=0, thickness=0):
    img_res = img_source
    img_properties = img_res.shape
    lines = transform.probabilistic_hough_line(img_res, line_gap=25, line_length=ll)
    for line in lines:
        p0, p1 = line
        eq_a, eq_b = line_eq(line)
        if eq_a == 'ver':
            for i in range(p0[1], p1[1] + 1):
                img_res[i, p0[0]] = 0
        else:
            for i in np.linspace(p0[0], p1[0], line_len(line) / thickness):
                val = eq_a * i + eq_b
                for ix in range(-thickness, thickness + 1):
                    for iy in range(-thickness, thickness + 1):
                        cord_y = int(val) + ix
                        cord_x = int(i) + iy
                        if img_properties[0] <= cord_y or cord_y < 0 or cord_x >= img_properties[1] or cord_x < 0:
                            continue
                        img_res[cord_y, cord_x] = 0
    return img_res


fig = plt.figure()
fig.subplots_adjust(left=0.0, top=1.0, right=1.0, bottom=0.0, wspace=0.0, hspace=0.0)

index = 0  # index of current
offset = 0  # offset for an image ID
img_ids = 4  # number of images
img_in_row = 2  # images in a row
img_jpgs = [io.imread('/root/PycharmProjects/equations/tictac/tic' + str(i + offset) + '.jpg') for i in range(1, img_ids + 1)]  # image collection

object_means = []
for img in img_jpgs:
    print('image no.', index, 'displayed')
    ax_plot = fig.add_subplot(img_ids / img_in_row, img_in_row, 1 + index)
    ax_plot.imshow(img, cmap='gray')
    ax_plot.axis('off')
    index += 1  # iteration counter

    # process image to get a board position
    img_proc, bcont = new_get_contours(img)
    boards_data = new_detect_boards(bcont, too_small=0.25)

    # erase lines and get objects
    img_proc, cont = new_get_boardless_contours(img_proc, ll=int(boards_data[0][2] * 0.25), thickness=3)

    # process contours
    processed_contours = [[] for _ in range(0, len(boards_data) + 1)]  # [[cx, cy, w, h, contours], [], [], ...]
    for c in cont:
        # calculate basic properties and board, object is located in
        center_x = sum(c)[1] / len(c)
        center_y = sum(c)[0] / len(c)
        obj_w = max(c[:, 1]) - min(c[:, 1])
        obj_h = max(c[:, 0]) - min(c[:, 0])

        board_id = len(boards_data) # assume that object does not belong to any board
        for i in range(0, len(boards_data)):
            b = boards_data
            b_left = center_x >= b[i][0] - b[i][2] / 2
            b_right = center_x <= b[i][0] + b[i][2] / 2
            b_up = center_y >= b[i][1] - b[i][3] / 2
            b_down = center_y <= b[i][1] + b[i][3] / 2
            if b_left and b_right and b_up and b_down:
                board_id = i # unless we find a match
                break
        processed_contours[board_id].append([center_x, center_y, obj_w, obj_h, c])

    # detect objects
    detected_objects = [[] for _ in range(0, len(boards_data))]
    for board_pc in range(0, len(processed_contours) - 1):
        for pc in processed_contours[board_pc]:
            # give up on objects too small for its board
            factor_edge = 0.05
            if pc[2] < boards_data[board_pc][2] * factor_edge or pc[3] < boards_data[board_pc][3] * factor_edge:
                continue
            if pc[2] > boards_data[board_pc][2] * 0.75 or pc[3] > boards_data[board_pc][3] * 0.75:
                continue

            # calculate angle intervals
            angle_probes = 45
            angle_segment = [0 for _ in range(0, angle_probes)]
            for point in pc[4]:
                # if possible...
                dx = point[1] - pc[0]
                if dx == 0:
                    continue
                dy = point[0] - pc[1]
                # ..calculate atan and convert into degree measure
                rad_angle = math.atan(dy / dx) * 180 / math.pi
                if dx < 0 > dy:
                    rad_angle = 270 - rad_angle
                if dx < 0 <= dy:
                    rad_angle = 270 - rad_angle
                if dx >= 0 > dy:
                    rad_angle = 90 - rad_angle
                if dx >= 0 <= dy:
                    rad_angle = 90 - rad_angle
                angle_segment[int(rad_angle / (360 / angle_probes))] += 1

            object_avg = sum(angle_segment) / len(angle_segment)
            variance = 0
            for i in angle_segment:
                variance += (i - object_avg) ** 2
            variance = float(variance) / (len(angle_segment))
            # each object gets new field - variance
            pc.append(variance)
            # and the entire object is put into new list
            detected_objects[board_pc].append(pc)

    # begin board calculations
    for ind, board in zip(range(0, len(detected_objects)), detected_objects):
        # plot and decide board state
        not_dynamic_anymore_threshold = 100
        board_state = [['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']]
        for c in board:
            if c[5] >= not_dynamic_anymore_threshold:
                mark = 'X'
                ax_plot.plot(c[4][:, 1], c[4][:, 0], color='green')
            else:
                mark = 'O'
                ax_plot.plot(c[4][:, 1], c[4][:, 0], color='purple')
            # read the logical position form the physical position in an image
            x_diff = boards_data[ind][0] - c[0]
            y_diff = boards_data[ind][1] - c[1]
            w_perc = math.fabs(x_diff) / boards_data[ind][2]
            h_perc = math.fabs(y_diff) / boards_data[ind][3]
            row_detected = 0
            col_detected = 0
            # object is in the center if its not further than 10% of the board size
            if w_perc < 0.10:
                col_detected = 1
            else:
                if x_diff < 0:
                    col_detected = 2
                else:
                    col_detected = 0
            if h_perc < 0.10:
                row_detected = 1
            else:
                if y_diff < 0:
                    row_detected = 2
                else:
                    row_detected = 0
            board_state[row_detected][col_detected] = mark
            print(row_detected, col_detected, mark, c[5])
        print(board_state)
# display the figure
plt.axis('off')
plt.show()

