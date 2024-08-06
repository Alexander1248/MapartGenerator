from litemapy import Region, BlockState
from nbtlib import Compound, String
import os


def build(path: str, heightmap: dict, max_h: int,
          width: int, height: int, name: str, support: str):
    os.makedirs("".join(seg + '/' for seg in path.rsplit('/')[:-1]), exist_ok=True)
    print('Generating litematica...')
    region = Region(0, 0, 0, width, max_h + 1, height + 1)
    for pos, block in heightmap.items():
        z = height - pos[1]
        if block[2].block_id == "_support_":
            region[pos[0], block[0], z] = BlockState(support)
            break
        if 'requires_support' in block[2].attributes and block[2].attributes['requires_support']:
            region[pos[0], block[0] - 1, z] = BlockState(support)

        nbt = Compound({'Name': String(block[2].block_id), 'Properties': Compound(block[2].properties)})
        region[pos[0], block[0], z] = BlockState.from_nbt(nbt)

    region.as_schematic(name, "MapGen",
                        "Generated By CLI Map Art Generator").save(f'{path}.litematic')
    print('Litematica generated!')
    print('Path:', os.path.abspath(path))
    pass
