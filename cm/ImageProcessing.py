def processImageFor(img_source, mean_hue=False, high_value=False, threshold=0, dark_pixels=False, light_letters=False):
    crop_data = img_source.load()
    crop_w, crop_h = img_source.size
    hue = 0
    import colorsys
    for x in range(crop_w):
        for y in range(crop_h):
            t = crop_data[x, y]
            hsv = colorsys.rgb_to_hsv(t[0] / 255.0, t[1] / 255.0, t[2] / 255.0)
            hue += hsv[0] * 360
            if high_value:
                if hsv[2] < 0.80:
                    crop_data[x, y] = (0, 0, 0, 255)
            if dark_pixels:
                if hsv[1] < threshold and hsv[2] < threshold:
                    crop_data[x, y] = (0, 0, 0, 255)
                else:
                    crop_data[x, y] = (255, 255, 255, 255)
            elif light_letters:
                if hsv[1] < 0.01 and hsv[2] >= threshold:
                    crop_data[x, y] = (0, 0, 0, 255)
                else:
                    crop_data[x, y] = (255, 255, 255, 255)

    if mean_hue:
        return hue / (crop_h * crop_w)
    return 0


def showImg(img_source):
    from matplotlib import pyplot as plt
    plt.imshow(img_source)
    plt.show()


def duplicateImg(img_source):
    crop_data = img_source.load()
    crop_w, crop_h = img_source.size
    pixels = list(img_source.getdata())
    pix_added = 0
    for y in range(crop_h):
        pix_row_added = 0
        for x in range(crop_w):
            pixels.insert(crop_w + y * crop_w + pix_added, crop_data[x, y])
            pix_added += 1
            pix_row_added += 1
    from PIL import Image
    img_source = Image.new(img_source.mode, (crop_w * 2, crop_h))
    img_source.putdata(pixels)
    return img_source


def readTextFromImage(img_source, only_digits=False):
    import pytesseract
    import re
    text = pytesseract.image_to_string(img_source, lang="eng")
    textlines = text.splitlines()
    ret_string = ""
    for line in textlines:
        if only_digits:
            text_filtered = re.sub("[Oo]", '0', line)
            text_filtered = re.sub("[^0-9]", '', text_filtered)
        else:
            text_filtered = re.sub("[^A-Za-z]+", '', line)
        if line:
            ret_string += text_filtered + '\n'
    return ret_string


def removeNoise(img_source, w_sample, h_sample):
    width, height = img_source.size
    data = img_source.load()
    for y in range(height):
        for x in range(width):
            if data[x, y] > 128:
                continue
            total = 0
            for c in range(x, width):
                if data[c, y] < 128:
                    total += 1
                else:
                    break
            if total <= w_sample:
                for c in range(total):
                    data[x + c, y] = 255
            x += total
    for x in range(width):
        for y in range(height):
            if data[x, y] > 128:
                continue
            total = 0
            for c in range(y, height):
                if data[x, c] < 128:
                    total += 1
                else:
                    break
            if total <= h_sample:
                for c in range(total):
                    data[x, y + c] = 255
            y += total


def subImg(img, template, verbose=False, threshold=0.75):
    import cv2
    from cv2 import cv
    method = cv.CV_TM_SQDIFF_NORMED
    result = cv2.matchTemplate(template, img, method)
    mn, _, mnloc, _ = cv2.minMaxLoc(result)
    mpx, mpy = mnloc
    trows, tcols = img.shape[:2]
    cv2.rectangle(img, (mpx, mpy), (mpx + tcols, mpy + trows), (0, 0, 255), 2)
    from matplotlib import pyplot as plt
    if verbose:
        plt.imshow(img)
        plt.show()
        print("subImg ratio value:" + mn)
    if mn > threshold:
        return True
    return False


def addCorners(img, rad):
    from PIL import Image, ImageDraw
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    w, h = img.size
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    img.putalpha(alpha)
    return img
