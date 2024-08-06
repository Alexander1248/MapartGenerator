import math

from PIL import Image
from PIL.Image import Resampling
from src.decoders import Palette, Color, Block


def decode(path: str, palette: Palette, size: int, w: int, h: int, resample: Resampling, blocks: dict, stairs: bool):
    print('Loading image...')
    with Image.open(path) as image:
        print('Image loaded!')
        print('Image resizing...')
        data = []
        image = image.convert('RGBA')
        factor = 64 * (2 ** size)
        image = image.resize((factor * w, factor * h), resample=resample)
        width, height = image.size
        print('Image resized!')
        print('Generating id matrix...')
        for y in range(height):
            line = []
            for x in range(width):
                r, g, b, a = image.getpixel((x, y))
                if a < 128:
                    line.append(None)
                else:
                    col = Color(r, g, b)
                    min_id = None
                    min_block = None
                    min_layer = 0
                    min_dst = float("inf")

                    for col_id in palette:
                        c0 = palette[col_id][0]
                        c1 = palette[col_id][1]
                        c2 = palette[col_id][2]
                        col_blocks = palette[col_id][3]
                        priority = float("-inf")
                        selected_block = None
                        for block in col_blocks:
                            if block.block_id in blocks:
                                block_data = blocks[block.block_id]
                                if block_data[0] > 0 and block_data[1] > priority:
                                    priority = block_data[1]
                                    selected_block = block

                        if selected_block is None:
                            continue
                        block_data = blocks[selected_block.block_id]
                        scaling_factor = math.exp(-0.1 * block_data[2])
                        dst = col.dst(c1) * scaling_factor
                        if dst < min_dst:
                            min_id = col_id
                            min_block = selected_block
                            min_layer = 0
                            min_dst = dst

                        if stairs:
                            dst = col.dst(c0) * scaling_factor
                            if dst < min_dst:
                                min_id = col_id
                                min_block = selected_block
                                min_layer = -1
                                min_dst = dst

                            dst = col.dst(c2) * scaling_factor
                            if dst < min_dst:
                                min_id = col_id
                                min_block = selected_block
                                min_layer = 1
                                min_dst = dst

                    if min_id is None:
                        exit('Not enough resources!')
                    old = blocks[min_block.block_id]
                    blocks[min_block.block_id] = (old[0] - 1, old[1], old[2])
                    line.append((min_id, min_block, min_layer))
            data.append(line)
        print('ID matrix generated!')
        return data, width, height


def heightmap(data: list, width: int, height: int, generator, optimizer):
    h = [0 for _ in range(width)]
    heightmap = {}
    min_h = 0
    max_h = 0
    print('Generating heightmap...')
    for y in range(height):
        for x in range(width):
            if data[y][x] is None:
                continue
            col_id, block, direction = data[y][x]
            heightmap[x, y] = (h[x], direction, block)
            h[x] = generator(h[x], direction)
            min_h = min(min_h, h[x])
            max_h = max(max_h, h[x])

    for x in range(width):
        if (x, height - 1) in heightmap:
            heightmap[x, height] = (h[x], 0, Block("_support_", {}, {}))

    for key in heightmap:
        old = heightmap[key]
        heightmap[key] = (old[0] - min_h, old[1], old[2])
    for x in range(width):
        h[x] -= min_h

    print('Heightmap generated!')
    print('Optimizing heightmap...')
    optimizer(heightmap, width, height)
    print('Heightmap optimization done!')

    max_h = 0
    for blocks in heightmap.values():
        max_h = max(max_h, blocks[0])
    return heightmap, max_h


def generate_preview(path: str, data: list, heightmap: dict, max_h: int, width: int, height: int,
                     palette: Palette):
    print('Preview generation started...')
    preview = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    elevation = Image.new('RGBA', (width, height + 1), (0, 0, 0, 0))
    direction = Image.new('RGBA', (width, height + 1), (0, 0, 0, 0))
    direction_computed = Image.new('RGBA', (width, height + 1), (0, 0, 0, 0))
    for y in range(height):
        for x in range(width):
            if data[y][x] is None:
                preview.putpixel((x, y), (0, 0, 0, 0))
                continue
            color = palette[data[y][x][0]][data[y][x][2] + 1]
            preview.putpixel((x, y), (color.r, color.g, color.b, 255))

    for pos, block in heightmap.items():
        g = int(255 * block[0] / (max_h + 1))
        elevation.putpixel((pos[0], pos[1]), (g, g, g, 255))
        g = int(255 * (1 - block[1]) / 3)
        direction.putpixel((pos[0], pos[1]), (g, g, g, 255))

        if (pos[0], pos[1] + 1) in heightmap:
            g = heightmap[pos[0], pos[1] + 1][0] - block[0]
            if g < 0:
                g = -1
            elif g > 0:
                g = 1
            g = int(255 * (1 - g) / 3)
            direction_computed.putpixel((pos[0], pos[1]), (g, g, g, 255))

    preview.save(f'{path}_color.png')
    elevation.save(f'{path}_height.png')
    direction.save(f'{path}_dir.png')
    direction_computed.save(f'{path}_dir_c.png')
    print('Preview generation done!')

# z axis any scaling factor
# data from negative
