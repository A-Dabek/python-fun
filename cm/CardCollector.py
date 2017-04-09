def getCardsBy(start_path, key_tag):
    import os
    processed_names = os.listdir(start_path)

    if not key_tag:
        return ""

    ret_str = ''
    for file_name in processed_names:
        if file_name[-4:] == ".txt":
            file = open(start_path + file_name)
            card_data = file.read()
            if card_data.find(key_tag) >= 0:
                ret_str += file_name + "\n"
    return ret_str


