def getCardName(img_source, verbose=False):
    import ImageProcessing
    ImageProcessing.processImageFor(img_source, dark_pixels=True, threshold=0.2)
    ret_str = ImageProcessing.readTextFromImage(img_source)
    if verbose:
        print(ret_str)
        ImageProcessing.showImg(img_source)
    return ret_str


def getCardCost(img_source, verbose=False):
    import ImageProcessing
    img = ImageProcessing.duplicateImg(img_source)
    ImageProcessing.processImageFor(img, dark_pixels=True, threshold=0.1)
    ret_str = ImageProcessing.readTextFromImage(img, only_digits=True)
    if verbose:
        print(ret_str)
        ImageProcessing.showImg(img)
    return 'Cost:' + ret_str[0]


def getCardColor(img_source, verbose=False):
    import ImageProcessing
    mean_hue = ImageProcessing.processImageFor(img_source, mean_hue=True)
    import CardData
    ret_str = CardData.matchHueTo(mean_hue, type=True)
    if verbose:
        print(ret_str, mean_hue)
        ImageProcessing.showImg(img_source)
    return 'Color:' + ret_str


def getCardRarity(img_source, verbose=False):
    import ImageProcessing
    mean_hue = ImageProcessing.processImageFor(img_source, mean_hue=True)
    import CardData
    ret_str = CardData.matchHueTo(mean_hue, rarity=True)
    if verbose:
        print(ret_str, mean_hue)
        ImageProcessing.showImg(img_source)
    return 'Rarity:' + ret_str


def getCardSkills(img_source, img_source_val, verbose=False):
    import ImageProcessing
    crop_w, crop_h = img_source.size
    val_crop_w, val_crop_h = img_source_val.size
    ImageProcessing.processImageFor(img_source, threshold=0.6, light_letters=True)
    ImageProcessing.processImageFor(img_source_val, light_letters=True, threshold=0.6)
    ret_string = ""
    import CardData
    for i in range(3):
        img_part = img_source.crop(map(int, (0, crop_h * i / 3.0, crop_w, crop_h * (i + 1) / 3.0)))
        img_part_val = img_source_val.crop(map(int, (0, val_crop_h * i / 3.0, val_crop_w, val_crop_h * (i + 1) / 3.0)))
        text = ImageProcessing.readTextFromImage(img_part)
        text_matched = CardData.fuzzyMatch(text, 0.65)
        text_val = ImageProcessing.readTextFromImage(img_part_val, only_digits=True)
        if text_val:
            text_val = text_val
        if text:
            ret_string += 'Skill:' + text_matched + " " + text_val + "\n"
    if verbose:
        print(ret_string)
        ImageProcessing.showImg(img_source)
        ImageProcessing.showImg(img_source_val)
    return ret_string


def getCardType(img_source, verbose=False):
    import ImageProcessing
    ImageProcessing.processImageFor(img_source, dark_pixels=True, threshold=0.2)
    ret_str = ImageProcessing.readTextFromImage(img_source)
    type = ['Ally', 'Equip', 'Armor']
    import difflib
    for t in type:
        ratio = difflib.SequenceMatcher(None, a=t, b=ret_str).ratio()
        if ratio > 0.5:
            ret_str = t
    if verbose:
        print(ret_str)
        ImageProcessing.showImg(img_source)
    return 'Type:' + ret_str + '\n'


def getCardDurability(img_source, verbose=False):
    import ImageProcessing
    ImageProcessing.processImageFor(img_source, light_letters=True, threshold=0.65)
    ret_str = ImageProcessing.readTextFromImage(img_source, only_digits=True)
    if verbose:
        print(ret_str)
        ImageProcessing.showImg(img_source)
    return 'Hp:' + ret_str


def getCardLevel(img_source, verbose=False):
    import ImageProcessing
    mean_hue = ImageProcessing.processImageFor(img_source, mean_hue=True)
    import CardData
    ret_str = CardData.matchHueTo(mean_hue, level=True)
    if verbose:
        print(ret_str, mean_hue)
        ImageProcessing.showImg(img_source)
    return 'Lvl:' + ret_str


def processRawCards(start_path):
    from os import listdir
    from PIL import Image
    raw_names = listdir(start_path)

    for file_name in raw_names:
        # load a raw card
        raw_card = Image.open(start_path + file_name)
        width, height = raw_card.size
        # split image into parts
        import cm.ImageProcessing as ImageProcessing
        ImageProcessing.showImg(raw_card)
        img_card_name = raw_card.crop(map(int, (width * .15, height * .04, width * .85, height * .115)))
        img_card_cost = raw_card.crop(map(int, (width * .03, height * .063, width * .14, height * .155)))
        img_card_color = raw_card.crop(map(int, (width * .465, height * .035, width * 0.54, height * .045)))
        img_card_skills = raw_card.crop(map(int, (width * .20, height * .6, width * .65, height * .885)))
        img_card_skills_value = raw_card.crop(map(int, (width * .75, height * .6, width * .95, height * .885)))
        img_card_rarity = raw_card.crop(map(int, (width * .05, height * .9, width * .13, height * .965)))
        img_card_type = raw_card.crop(map(int, (width * .135, height * .90, width * .4, height * .965)))
        img_card_durability = raw_card.crop(map(int, (width * .60, height * .88, width * .85, height * .985)))
        img_card_level = raw_card.crop(map(int, (width * .48, height * .91, width * .53, height * .95)))
        # prepare card data
        card_name = getCardName(img_card_name)
        card_data = ""
        card_data += getCardCost(img_card_cost) + "\n"
        card_data += getCardColor(img_card_color) + "\n"
        card_data += getCardRarity(img_card_rarity) + "\n"
        card_data += getCardSkills(img_card_skills, img_card_skills_value)
        card_data += getCardType(img_card_type)
        card_data += getCardDurability(img_card_durability)
        if card_data.find('Ally') >= 0:
            card_data += getCardLevel(img_card_level) + "\n"
        # save data
        import ImageProcessing
        round_corners = ImageProcessing.addCorners(raw_card, 20)
        if len(card_name[0:-1]) < 4:
                card_name = "Unreadable "
        round_corners.save('processed/' + card_name[0:-1] + ".png")
        #text_file = open('processed/' + card_name[0:-1] + ".txt", "w+")
        print(card_name, card_data)
        #text_file.write(card_data)
        #text_file.close()
