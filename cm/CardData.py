def matchHueTo(hue_value, rarity=False, level=False, type=False):
    min_diff = 360 ** 2
    match_key = ""
    match_sec_key = ""
    crossing_matches = False
    if rarity:
        dictionary = hue_rare_tags
    elif level:
        dictionary = hue_lvl_tags
    elif type:
        dictionary = hue_type_tags
        crossing_matches = True

    for k, v in dictionary.items():
        diff = (hue_value - v) ** 2
        if diff < min_diff:
            min_diff = diff
            match_key = k
            match_sec_key = ""
        if crossing_matches:
            for k2, v2 in dictionary.items():
                if v2 == v or v2 == 0.0 or v == 0.0:
                    continue
                diff = (hue_value - ((v + v2) / 2.0)) ** 2
                if diff < min_diff:
                    min_diff = diff
                    match_key = k
                    match_sec_key = " and " + k2
    ret_str = match_key + match_sec_key
    return ret_str


hue_type_tags = {"war": 4.6,
                 "chaos": 267.0,
                 "chance": 40.3,
                 "balance": 197.7,
                 "nature": 100.9,
                 "generic": 0.0}

hue_rare_tags = {"Common": 17.0,
                 "Uncommon": 152.0,
                 "Rare": 38.0,
                 "Epic": 187.5}

hue_lvl_tags = {"Lv0": 40.5,
                "Lv1": 22.3,
                "Lv2": 99.5,
                "Lv3": 45.5,
                "Lv4": 175.0}


def fuzzyMatch(word, threshold):
    if len(word) < 3:
        return ""
    import difflib
    for c in popular_indexes:
        ratio = difflib.SequenceMatcher(None, a=c, b=word).ratio()
        if ratio > threshold:
            return c
    for c in minion_features:
        ratio = difflib.SequenceMatcher(None, a=c, b=word).ratio()
        if ratio > threshold:
            popular_indexes.append(c)
            return c
    return word


from os import listdir

minion_features = [i[0:-4] for i in listdir("features/")]
popular_indexes = []
