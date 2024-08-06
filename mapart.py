import argparse
from PIL.Image import Resampling

import src

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        prog='MapArtGenerator',
        description='Generate mapart litematica from image'
    )
    arg_parser.add_argument('--image', '-i', type=str, required=True,
                            help='Input image filepath')
    arg_parser.add_argument('--blocks', '-b', type=str, required=True,
                            help='Block count list filepath')
    arg_parser.add_argument('--output', '-o', type=str,
                            help='Output filepath')

    arg_parser.add_argument('--map-size', '-ms', type=int, default=1,
                            choices=[1, 2, 3, 4],
                            help='Size of map (default: 1)')
    arg_parser.add_argument('--width', '-mw', type=int, default=1,
                            help='Width in maps (default: 1)')
    arg_parser.add_argument('--height', '-mh', type=int, default=1,
                            help='Height in maps (default: 1)')
    arg_parser.add_argument('--resampling', '-r', type=str, default='BICUBIC',
                            choices=['NEAREST', 'BILINEAR', 'BICUBIC',
                                     'BOX', 'LANCZOS', 'HAMMING'],
                            help='Image resampling method (default: BICUBIC)')
    arg_parser.add_argument('--support', '-s', type=str, default="minecraft:stone",
                            help='Support block id (default: minecraft:stone)')
    arg_parser.add_argument('--palette', '-p', type=str, default='1.20',
                            choices=['1.20'],
                            help='Version of palette (default: 1.20)')
    arg_parser.add_argument('--update', '-u', action='store_true',
                            help='Update block count list')
    arg_parser.add_argument('--preview', '-v', type=str,
                            help='Preview image filepath')
    arg_parser.add_argument('--name', '-n', type=str, default="MapArt",
                            help='Litematica name (default: MapArt)')
    arg_parser.add_argument('--generator', '-g', type=str,
                            choices=['plain', 'stairs', 'boundary', 'fast_boundary', 'dropout', 'fast_dropout'], default='dropout',
                            help='Litematica layering generator type (default: boundary)')
    args = arg_parser.parse_args()
    print('Generating mapart...')
    palette = src.decode_palette(f'palettes/{args.palette}.json')
    blocks = src.decode_blocks(args.blocks)

    if args.resampling == 'NEAREST':
        resampling = Resampling.NEAREST
    elif args.resampling == 'BILINEAR':
        resampling = Resampling.BILINEAR
    elif args.resampling == 'BICUBIC':
        resampling = Resampling.BICUBIC
    elif args.resampling == 'BOX':
        resampling = Resampling.BOX
    elif args.resampling == 'LANCZOS':
        resampling = Resampling.LANCZOS
    elif args.resampling == 'HAMMING':
        resampling = Resampling.HAMMING
    else:
        exit('Invalid resampling type')

    data, width, height = src.decode(args.image, palette, args.map_size, args.width,
                                     args.height, resampling, blocks, args.generator != 'plain')

    if args.generator == 'plain':
        h, max_h = src.heightmap(data, width, height, src.generators.plain, src.optimizers.none)
    elif args.generator == 'stairs':
        h, max_h = src.heightmap(data, width, height, src.generators.stairs, src.optimizers.none)
    elif args.generator == 'boundary':
        h, max_h = src.heightmap(data, width, height, src.generators.stairs, src.optimizers.boundary)
    elif args.generator == 'fast_boundary':
        h, max_h = src.heightmap(data, width, height, src.generators.stairs, src.optimizers.fast_boundary)
    elif args.generator == 'dropout':
        h, max_h = src.heightmap(data, width, height, src.generators.stairs, src.optimizers.dropout)
    elif args.generator == 'fast_dropout':
        h, max_h = src.heightmap(data, width, height, src.generators.stairs, src.optimizers.fast_dropout)
    else:
        exit('Invalid generator type')

    if args.preview:
        src.generate_preview(args.preview, data, h, max_h, width, height, palette)

    path = args.output
    if path is None:
        path = args.image.rsplit('.', 1)[0]
    src.build(path, h, max_h, width, height, args.name, args.support)

    if args.update:
        src.encode_blocks(args.blocks, blocks)
