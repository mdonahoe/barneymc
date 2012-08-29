"""
Heavily borrowed from www.wiki.vg/Protocol#0x33
"""
import struct
hexer = lambda b: struct.unpack('>B', b)[0]

# a dict (x,y,z) -> block id
world = dict()
AIR = 0
DIAMOND_ORE = 56
DIAMOND = 57
ENDER_CHEST = 130
TNT = 46
SAND = 12
DIRT = 3
STONE = 1
PLATE = 72
REDSTONE = 73
SIGN = 63
DOOR = 64
SPAWNER = 52
#interesting = (DOOR,ENDER_CHEST,SIGN,PLATE, SPAWNER)
EMERALD = 133
EMERALD_ORE = 129
interesting = (DIAMOND_ORE,)

block_names = {
    DIAMOND:'DIAMOND',
    SAND:'SAND',
    DIRT:'DIRT',
    STONE:'STONE',
}

blocks = dict()
interest = []

def extract_map(packet):
    keys = 'x_chunk,z_chunk,primary_bitmap,data'.split(',')
    args = [packet.data[arg] for arg in keys]
    chunky(*args)

def chunky(chunk_x, chunk_z, bitmask, chunk_data):
    # loop over 16x16x16 sections in the 16x256x16 chunk
    if len(interest) > 256: return
    for i in range(16):
        # skip chunks that arent included
        if not (bitmask & (1 << i)):
            continue
        cubic = chunk_data[i*4096:(i+1)*4096]
        L = len(cubic)
        assert L == 4096, 'too small: %s' % L
        for j, hb in enumerate(cubic):
            block_id = hexer(hb)
            x = chunk_x*16 + (j & 0x0F)
            y = i*16 + (j >> 8)
            z = chunk_z*16 + ((j & 0xF0) >> 4)
            # dont add air to map
            if block_id == AIR:
                continue
            #world[(x,y,z)] = block_id
            if block_id not in blocks:
                blocks[block_id] = 0
            blocks[block_id] += 1
            if block_id in interesting:
                interest.append((x,y,z))
                #print [hexer(q) for q in cubic]


def block_stats():
    d = [(v,k) for k,v in blocks.iteritems()]
    d.sort(reverse=True)
    for v,k in d:
        print block_names.get(k, k), v

