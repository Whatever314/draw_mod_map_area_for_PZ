from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
import getpass, os
import os.path as path
import sys, msvcrt

ALPHA = 0.6
CURRENT_USER = getpass.getuser()

def color_rgba(n, alpha):
    def plus(vec, d): return [vec[i] + d for i in range(len(vec))]

    first = [(255, 191, 191), (191, 255, 191), (191, 191, 255), 
             (255, 255, 191), (191, 255, 255), (255, 191, 255),
             (191, 255, 223), (255, 223, 191), (223, 191, 255),
             (223, 255, 191), (255, 191, 223), (191, 223, 255)]
    k = (n // 12) % 128
    b = n % 12
    k_bitlen = k.bit_length()
    k_bin = [int(bin(k)[1+k_bitlen-i]) for i in range(k_bitlen)]
    int_rgba = plus(first[b], -sum([k_bin[i]*2**(6-i) for i in range(k_bitlen)]))
    int_rgba.append(int(255*alpha))
    return tuple(int_rgba)

def get_loc_from_list(files_list):
    locs = []
    for f in files_list:
        if f[-10:] == ".lotheader":
            locs.append(tuple([int(x) for x in f[:-10].split("_")]))
    return list(set(locs))

def check_map_lots(map_path):
    res = True
    if path.isfile(path.join(map_path, "map.info")):
        with open(path.join(map_path, "map.info"), encoding="unicode_escape") as info_file:
            while True:
                line = info_file.readline().strip()
                if line:
                    if line[:5] == "lots=" and line[5:].strip() not in {"Muldraugh, KY", "Riverside, KY", "Rosewood, KY", "West Point, KY"}:
                        res = False
                        break
                else: break
    return res

def get_all_modmaps(mods_path):
    all_modmaps = {}
    for num in os.scandir(mods_path):
        temp_path = path.join(mods_path, num, "mods")
        for mod_path in os.scandir(temp_path):
            if mod_path.is_dir() and path.isdir(path.join(mod_path, "media", "maps")):
                lst = []
                for map_path in os.scandir(path.join(mod_path, "media", "maps")):
                    if check_map_lots(map_path):
                        for file_path in os.scandir(map_path): lst.append(file_path.name)
                locs = get_loc_from_list(lst)
                if locs:
                    info_dict = {}
                    info_dict["locs"] = locs
                    info_dict["path"] = mod_path.path
                    id = ""
                    with open(path.join(mod_path, "mod.info"),  encoding = 'unicode_escape') as f:
                        for line in f.readlines():
                            splitted_line = line.strip().split("=")
                            if splitted_line[0] == 'id': id = splitted_line[1]
                            if splitted_line[0] == "name": info_dict["name"] = splitted_line[1]
                    all_modmaps[id] = info_dict
    return all_modmaps

def get_maps_dict(save_path, all_modmaps_dict):
    lst = list(all_modmaps_dict)
    res_dic = {}
    with open(path.join(save_path, "mods.txt"), encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) > 6 and line[:6] == 'mod = ':
                if line[-1] == ',': line = line[:-1]
                id = line[6:]
                res_dic[id] = all_modmaps_dict[id]
                lst.remove(id)
    return res_dic

def draw_one_cell(loc, cell_width, color, draw_obj):
    x = cell_width*loc[0]
    y = cell_width*loc[1]
    draw_obj.rectangle((x, y, x+cell_width-1, y+cell_width-1), fill=color)
    return

def tag(loc, cell_width, text, font_obj, draw_obj):
    draw_obj.text((cell_width*loc[0]+int(font_obj.getlength("a")*0.3), cell_width*loc[1]), text, fill=(255, 255, 255, int(255*(ALPHA+1)/2)), font=font_obj, stroke_width=int(font_obj.getlength("a")*0.1), stroke_fill=(0, 0, 0, 255))
    return

def max_text_len(maps_dict, font_obj):
    return int(max(font_obj.getlength(maps_dict[id]["name"]) for id in maps_dict))

def draw_maps(maps_dict, cell_width, font_obj, map):
    def get_tag_locs(locs_list):
        res = []
        while locs_list:
            branch_min = locs_list.pop()
            current_branch = [branch_min]
            i = 0
            while i < len(locs_list):
                check_loc = locs_list[i]
                if {(check_loc[0]-1, check_loc[1]), 
                    (check_loc[0]+1, check_loc[1]), 
                    (check_loc[0], check_loc[1]-1), 
                    (check_loc[0], check_loc[1]+1)}.isdisjoint(set(current_branch)):
                    i += 1
                else:
                    current_branch.append(check_loc)
                    if check_loc < branch_min: branch_min = check_loc
                    del locs_list[i:i+1]
                    i = 0
            res.append(branch_min)
        return res

    def get_overlaps_dict(maps_dict):
        overlap_dict = {}
        no_overlap_dict = {}
        no_overlap_maps_dict = {}
        for id in maps_dict:
            for loc in maps_dict[id]["locs"]:
                l_in_o_d = loc in overlap_dict
                l_in_n_o_d = loc in no_overlap_dict
                if not (l_in_o_d or l_in_n_o_d):
                    no_overlap_dict[loc] = id
                else:
                    if not l_in_o_d:
                        overlap_dict[loc] = [maps_dict[no_overlap_dict[loc]]["name"]]
                        del no_overlap_dict[loc]
                    overlap_dict[loc].append(maps_dict[id]["name"])
        for loc in no_overlap_dict:
            id = no_overlap_dict[loc]
            if id not in no_overlap_maps_dict:
                no_overlap_maps_dict[id] = maps_dict[id].copy()
                no_overlap_maps_dict[id]["locs"] = [loc]
            else: no_overlap_maps_dict[id]["locs"].append(loc)
        return overlap_dict, no_overlap_maps_dict

    Xmax = max(max(loc[0] for loc in maps_dict[id]["locs"]) for id in maps_dict)
    Ymax = max(max(loc[1] for loc in maps_dict[id]["locs"]) for id in maps_dict)
    if Xmax > 65 or Ymax > 52:
        background = Image.new("RGBA", ((max(Xmax, 65)+1) * cell_width + max(0, max_text_len(maps_dict, font_obj)-cell_width), (max(Ymax, 52)+1) * cell_width), (0, 0, 0, 0))
        background.paste(map, (0, 0))
        map = background
    cover = Image.new("RGBA", map.size, color=(0, 0, 0, 0))
    cover_draw = ImageDraw.Draw(cover)

    ids_list = list((maps_dict[id]["name"], id) for id in maps_dict)
    ids_list.sort()
    ids_list = [tp[1] for tp in ids_list]
    overlap_dict, no_overlap_maps_dict = get_overlaps_dict(maps_dict)
    for map_index, map_id in enumerate(ids_list):
        if map_id in no_overlap_maps_dict:
            cell_color = color_rgba(map_index, ALPHA)
            for cell_loc in no_overlap_maps_dict[map_id]["locs"]: draw_one_cell(cell_loc, cell_width, cell_color, cover_draw)
            for tag_loc in get_tag_locs(no_overlap_maps_dict[map_id]["locs"]): tag(tag_loc, cell_width, no_overlap_maps_dict[map_id]["name"], font_obj, cover_draw)
    for overlap_loc in overlap_dict:
        draw_one_cell(overlap_loc, cell_width, (255, 0, 0, 255), cover_draw)
        cover_draw.multiline_text((cell_width*overlap_loc[0]+int(font_obj.getlength("a")*0.4), cell_width*overlap_loc[1]),
                                  "OVERLAP!!!\n"+'\n'.join(overlap_dict[overlap_loc]),
                                  fill=(255, 255, 0, 255),
                                  font=font_obj)
    output = Image.alpha_composite(map, cover)
    return output

def gen_legends(file_path, maps_dict, font_path):
    alpha = 1
    width = 40
    dist = int(width*0.4)
    font_obj = ImageFont.truetype(font_path, width)
    names_list = [maps_dict[id]["name"] for id in maps_dict]
    names_list.sort()
    img_width = width + dist*3 + int(max(font_obj.getlength(name) for name in names_list))+1
    img_height = len(names_list)*(width+dist) + dist
    img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    img_draw = ImageDraw.Draw(img)
    for i, name in enumerate(names_list):
        img_draw.rectangle((dist, dist+(width+dist)*i, dist+width-1, (dist+width)*(i+1)-1), color_rgba(i, alpha))
        img_draw.text((width+dist*2, (width+dist)*i+int((width+3)*0.25)), name, (255, 255, 255, 255), font_obj, stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(file_path)
    return img






if __name__ == "__main__":
    cell_width = 120
    width_in_cell = 66
    height_in_cell = 53
    current_dir = path.dirname(sys.argv[0])
    if not path.isdir(path.join(current_dir, "output")): os.mkdir(path.join(current_dir, "output"))
    map = Image.new("RGBA", (width_in_cell*cell_width, height_in_cell*cell_width))
    for i in range(2):
        for j in range(2):
            part_img = Image.open(path.join(current_dir, "resources", str(i)+"_"+str(j)+".png"))
            map.paste(part_img, (int(cell_width/2*width_in_cell*i), int(cell_width/2*height_in_cell*j)))
    for font_file in os.scandir(path.join(current_dir, "font")):
        font_path = font_file.path
        break
    font_default = ImageFont.truetype(font_path, size=int(max(10, cell_width / 4)))
    with open(path.join(current_dir, "config.txt")) as cfg_file:
        game_path = cfg_file.readline()[15:].strip()
        save_path = cfg_file.readline()[15:].strip()
    save = path.split(save_path)[1]
    mods_path = path.join(path.split(path.split(game_path)[0])[0], "workshop", "content", "108600")
    all_modmaps = get_all_modmaps(mods_path)
    modmaps_dict = get_maps_dict(save_path, all_modmaps)
    print("Working on \""+save+"\". Please wait.")
    output_img = draw_maps(modmaps_dict, cell_width, font_default, map)
    gen_legends(path.join(current_dir, "output", "legends_"+save+".png"), modmaps_dict, font_path)
    print("Exporting. This might take a few minutes.")
    output_img.save(path.join(current_dir, "output", save+".png"))
    print("Everything done! Open the \"output\" folder to see the picture and press any key to exit.")
    print(ord(msvcrt.getch()))

