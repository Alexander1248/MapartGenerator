import json
import io
import math


class Block:
    def __init__(self, block_id, attributes, properties):
        self.block_id = block_id
        self.attributes = attributes
        self.properties = properties


class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def dst(self, col):
        l1, a1, b1 = self.to_lab()
        l2, a2, b2 = col.to_lab()
        return math.sqrt((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)

    def to_lab(self):
        x = (0.412453 * self.r + 0.357580 * self.g + 0.180423 * self.b) / 242.36628
        y = (0.212671 * self.r + 0.715160 * self.g + 0.072169 * self.b) / 255
        z = (0.019334 * self.r + 0.119193 * self.g + 0.950227 * self.b) / 277.63227
        l = 116 * lab_f(y) - 16
        a = 500 * (lab_f(x) - lab_f(y))
        b = 200 * (lab_f(y) - lab_f(z))
        return l, a, b


def lab_f(t):
    if t > 0.008856451679:
        return t**(1/3)
    return 7.787037037037 * t + 0.1379310344828


class Palette:
    def __init__(self):
        self.palette = {}

    def add(self, id: str, color0: Color, color1: Color, color2: Color, blocks):
        self.palette[id] = (color0, color1, color2, blocks)

    def __iter__(self):
        return iter(self.palette)

    def __len__(self):
        return len(self.palette)

    def __getitem__(self, key):
        return self.palette[key]


def decode_palette(path: str) -> Palette:
    with io.FileIO(path, mode='r') as file:
        print('Parsing palette...')
        dec = json.loads(file.read())
        palette = Palette()
        for data in dec:
            colors_json = data["colors"]
            blocks_json = data["blocks"]
            blocks = []
            for block_json in blocks_json:
                blocks.append(Block(block_json["id"], block_json["attributes"], block_json["properties"]))
            palette.add(
                data["id"],
                Color(colors_json[0]["r"], colors_json[0]["g"], colors_json[0]["b"]),
                Color(colors_json[1]["r"], colors_json[1]["g"], colors_json[1]["b"]),
                Color(colors_json[2]["r"], colors_json[2]["g"], colors_json[2]["b"]),
                blocks)

        print('Palette successfully parsed!')
        return palette


def decode_blocks(path: str):
    with io.FileIO(path, mode='r') as file:
        print('Parsing blocks...')
        data = file.readlines()
        blocks = {}
        for block in data:
            segments = block.decode()[:-2].split(' ')
            blocks[segments[0]] = (int(segments[1]), float(segments[2]), float(segments[3]))
        print('Blocks successfully parsed!')
        return blocks


def encode_blocks(path: str, blocks: dict):
    with io.FileIO(path, mode='w') as file:
        string = ''
        for block, data in blocks.items():
            string += f'{block} {data[0]} {data[1]} {data[2]}\r\n'
        file.write(string.encode())
        file.flush()
