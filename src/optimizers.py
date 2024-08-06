import math


def none(heightmap: dict, width: int, height: int):
    pass


def boundary(heightmap: dict, width: int, height: int):
    edited = True
    while edited:
        edited = False
        for pos, data in heightmap.items():
            if data[0] > 128 and data[1] > 0:
                m = data[0]
                z = pos[1]
                z -= 1
                while (pos[0], z) in heightmap:
                    if ((pos[0], z + 1) in heightmap and heightmap[pos[0], z][0] <
                            heightmap[pos[0], z + 1][0] - heightmap[pos[0], z][1]):
                        break
                    m = min(m, heightmap[pos[0], z][0])
                    z -= 1

                if m > 0:
                    end_z = z
                    for z in range(pos[1], end_z, -1):
                        data = heightmap[pos[0], z]
                        heightmap[pos[0], z] = (data[0] - 1, data[1], data[2])

                    edited = True


def dropout(heightmap: dict, width: int, height: int):
    edited = True
    while edited:
        edited = False
        for pos, data in heightmap.items():
            if data[0] <= 0:
                break
            if data[1] > 0:
                m = data[0]
                z = pos[1] - 1
                while (pos[0], z) in heightmap:
                    if ((pos[0], z + 1) in heightmap and heightmap[pos[0], z][0] <
                            heightmap[pos[0], z + 1][0] - heightmap[pos[0], z][1]):
                        break
                    m = min(m, heightmap[pos[0], z][0])
                    z -= 1
                end_z = z

                z = pos[1] + 1

                # TODO: Backflow
                # while (pos[0], z) in heightmap:
                #     if ((pos[0], z - 1) in heightmap and heightmap[pos[0], z - 1][0] <
                #             heightmap[pos[0], z][0] - heightmap[pos[0], z - 1][1]):
                #         break
                #     m = min(m, heightmap[pos[0], z][0])
                #     z += 1
                start_z = z - 1

                if z != pos[1] and m > 0:
                    for z in range(start_z, end_z, -1):
                        data = heightmap[pos[0], z]
                        heightmap[pos[0], z] = (data[0] - 1, data[1], data[2])
                    edited = True



def fast_boundary(heightmap: dict, width: int, height: int):
    edited = True
    while edited:
        edited = False
        for pos, data in heightmap.items():
            if data[0] > 128 and data[1] > 0:
                m = data[0]
                z = pos[1]
                z -= 1
                while (pos[0], z) in heightmap:
                    m = min(m, heightmap[pos[0], z][0])
                    z -= 1

                if m > 0:
                    end_z = z
                    for z in range(pos[1], end_z, -1):
                        data = heightmap[pos[0], z]
                        heightmap[pos[0], z] = (data[0] - (m + 7) // 8, data[1], data[2])

                    edited = True

def fast_dropout(heightmap: dict, width: int, height: int):
    edited = True
    while edited:
        edited = False
        for pos, data in heightmap.items():
            if data[0] > 0 and data[1] > 0:
                m = data[0]
                z = pos[1]
                z -= 1
                while (pos[0], z) in heightmap:
                    m = min(m, heightmap[pos[0], z][0])
                    z -= 1

                if m > 0:
                    end_z = z
                    for z in range(pos[1], end_z, -1):
                        data = heightmap[pos[0], z]
                        heightmap[pos[0], z] = (data[0] - (m + 7) // 8, data[1], data[2])
                    edited = True