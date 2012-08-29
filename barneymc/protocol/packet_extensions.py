from data_types import *
import chunk

extensions = {}
def extension(ident):
    def inner(cl):
        extensions[ident] = cl
        return cl
    return inner

@extension(0x17)
class Extension17:
    @classmethod
    def decode_extra(self, packet, bbuff):
        if packet.data['thrower_entity_id'] > 0:
            packet.data['x2'] = unpack(bbuff, 'short')
            packet.data['y2'] = unpack(bbuff, 'short')
            packet.data['z2'] = unpack(bbuff, 'short')

    @classmethod
    def encode_extra(self, packet):
        append = ''
        if packet.data['thrower_entity_id'] > 0:
            for i in ('x2','y2','z2'):
                append += pack('short', packet.data[i])
        return append

@extension(0x1D)
class DestroyEntity:
    @classmethod
    def decode_extra(self, packet, bbuff):
        count = int(packet.data['entity_count'])
        for i in range(count):
            eid = unpack(bbuff, "int")

@extension(0x33)
class Extension33:
    @classmethod
    def decode_extra(self, packet, bbuff):
        packet.data['data'] = unpack_array_fast(bbuff, 'ubyte', packet.data['data_size'])
        del packet.data["data_size"]
        chunk.extract_map(packet)


    @classmethod
    def encode_extra(self, packet):
        packet.data['data_size'] = len(packet.data['data'])
        return pack_array_fast('ubyte', packet.data['data'])

@extension(0x34)
class Extension34:
    @classmethod
    def decode_extra(self, packet, bbuff):
        packet.data["blocks"] = []
        for i in range(packet.data['record_count']):
            data = unpack(bbuff, 'uint')
            block = {
                'metadata': (data     )   & 0xF,
                'type':     (data >> 4)  & 0xFFF,
                'y':        (data >> 16) & 0xFF,
                'z':        (data >> 24) & 0xF,
                'x':        (data >> 28) & 0xF}
            packet.data["blocks"].append(block)
        del packet.data["data_size"]

    @classmethod
    def encode_extra(self, packet):
        packet.data['record_count']  = len(packet.data['blocks'])
        packet.data['data_size'] = 4 * len(packet.data['blocks'])
        append = ''
        for block in packet.data['blocks']:
            append += pack('uint',
                (block['metadata']  ) +
                (block['type'] <<  4) +
                (block['y']    << 16) +
                (block['z']    << 24) +
                (block['x']    << 28))
        return append

@extension(0x38)
class MapChunkBulk:
    @classmethod
    def decode_extra(self, packet, bbuff):
        import zlib
        L = packet.data['data_len']
        chunk_data = zlib.decompress(bbuff.read(L))
        """
Each part is 10240 * n + 256 bytes.
n is the number of sections in the current chunk
(this is the number of flags set in the primary bitmap).
10240 is the amount of bytes for each chunk without add bitmap,
256 bytes are used for biomes.
"""
        j = 0
        for i in range(packet.data['chunk_count']):
            cx = unpack(bbuff, 'int')
            cz = unpack(bbuff, 'int')
            primary_bitmap = unpack(bbuff, 'short')
            add_bitmap = unpack(bbuff, 'short')

            # count the ones
            n = bin(primary_bitmap).count('1')

            # length of this chunk (wihout 'add' data)
            k = 10240 * n + 256

            # this chunk's data
            d = chunk_data[j:j+k]
            j+=k

            chunk.chunky(cx,cz,primary_bitmap,d)


@extension(0x3C)
class Explosion:
    @classmethod
    def decode_extra(self, packet, bbuff):
        records = unpack_array_fast(bbuff, 'byte', packet.data['records']*3)
        i = 0
        packet.data["blocks"] = []
        while i < packet.data['records']*3:
            packet.data["blocks"].append(dict(zip(('x','y','z'), records[i:i+3])))
            i+=3
        # remove the 3 unknown floats
        unpack(bbuff, "float")
        unpack(bbuff, "float")
        unpack(bbuff, "float")

    @classmethod
    def encode_extra(self, packet):
        packet.data['data_size'] = len(packet.data['blocks'])
        array = []
        for i in packet.data['blocks']:
            array += [i['x'], i['y'], i['z']]

        return pack_array_fast('byte', array)

@extension(0x68)
class Extension68:
    @classmethod
    def decode_extra(self, packet, bbuff):
        packet.data["slots_data"] = unpack_array(bbuff, 'slot', packet.data["data_size"])
        del packet.data["data_size"]

    @classmethod
    def encode_extra(self, packet):
        packet.data['data_size'] = len(packet.data['slots_data'])
        return pack_array('slot', packet.data['slots_data'])

@extension(0x82)
class Extension82:
    @classmethod
    def decode_extra(self, packet, bbuff):
        packet.data["text"] = []
        for i in range(4):
            packet.data["text"].append(packet.data.pop("line_%s" % (i+1)))

    @classmethod
    def encode_extra(self, packet):
        for i in range(4):
            packet.data["line_%s" % (i+1)] = packet.data["text"][i]
        del packet.data["text"]
        return ''

@extension(0x83)
class Extension83:
    @classmethod
    def decode_extra(self, packet, bbuff):
        packet.data["data"] = unpack_array_fast(bbuff, 'ubyte', packet.data['data_size'])
        del packet.data["data_size"]

    @classmethod
    def encode_extra(self, packet):
        packet.data['data_size'] = len(packet.data['data'])
        return pack_array_fast('ubyte', packet.data['data'])

@extension(0xFA)
class ExtensionFA:
    @classmethod
    def decode_extra(self, packet, bbuff):
        packet.data["data"] = unpack_array_fast(bbuff, 'byte', packet.data['data_size'])
        del packet.data["data_size"]

    @classmethod
    def encode_extra(self, packet):
        packet.data['data_size'] = len(packet.data['data'])
        return pack_array_fast('byte', packet.data['data'])

"""
@extention(0xFD)
class EncryptionKeyRequest:
    @classmethod
    def decode_extra(self, packet, bbuff):
        l = unpack
        packet.data["pubkey"] = unpack_array_fast(bbuff, 'byte', packet.data
"""
