def prepareRawCards(start_path):
    from os import listdir
    from skimage import measure, io
    from PIL import Image
    ss_names = listdir(start_path)
    for file_name in ss_names:
        # load a screenshot
        raw_ss = io.imread(start_path + file_name)
        # get binary image
        binary_raw_ss = (raw_ss[:, :, 2] + raw_ss[:, :, 1] + raw_ss[:, :, 0]) == 0
        # get contours
        raw_contours = measure.find_contours(binary_raw_ss, 0.5)
        frame_contours = []
        max_width = 0
        # find card frames
        for c in raw_contours:
            current_w = max(c[:, 1]) - min(c[:, 1])
            if current_w > max_width:
                if current_w - max_width > 5:
                    frame_contours = [c]
                else:
                    frame_contours.append(c)
                max_width = current_w
            elif current_w == max_width:
                frame_contours.append(c)
        # crop original image into cards
        for c, ind in zip(frame_contours, range(0, len(frame_contours))):
            bbox = (int(min(c[:, 1])), int(min(c[:, 0])), int(max(c[:, 1])), int(max(c[:, 0])))
            img_to_crop = Image.open(start_path + file_name).crop(bbox)
            img_to_crop.save("raw/" + str(ind) + str(file_name))
