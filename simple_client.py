import asyncore
from vector import Vector
from random import random
import re
ptypes = {}

from barneymc.protocol.packet import *
from barneymc.protocol import bound_buffer
from barneymc.net import client

xyz = 'x,y,z'.split(',')
dxyz = 'dx,dy,dz'.split(',')

extractor = lambda ks, d: [d[k] for k in ks]
vec_from_data = lambda d: Vector(*extractor(xyz, d))
dvec_from_data = lambda d: Vector(*extractor(dxyz, d))

class Player(object):
    all = dict()
    def __init__(self, eid, name, pos):
        self.eid = eid
        self.name = name
        self.pos = pos
        self.all[eid] = self

    def move(self, dpos):
        self.pos = self.pos + dpos

    def set_position_and_look(self, data):
        self.pos = vec_from_data(data)
        # todo: look

    def __repr__(self):
        return '(%s) %s %s' % (self.eid,self.name,self.pos)

    def get_position_and_look(self):
        """create data object for sending"""
        return dict(
            x=self.pos.x,
            y=self.pos.y,
            z=self.pos.z,
            stance=self.pos.y + 0.5,
            yaw=0,
            pitch=0,
            on_ground=True
        )


class SimpleClient(client.Client):
    spawned = False
    last_pos = None
    me = None
    target_player = 'mdonahoe'
    def __init__(self, **settings):
        self.handlers = {
            0x00: self.reflect, #Echos the packet back to the server
            0x01: self.parselogin,
            0x03: self.get_chat,
            0x0d: self.positionandlook,
            0x1F: self.rel_update_player,
            0x21: self.rel_update_player,
            0x14: self.create_player,
            0x22: self.update_player, #teleport
            0xfd: self.login,
            0xfa: self.print_plugin,
            0xff: self.disconnect}

        client.Client.__init__(self, **settings)

        self.connect2()

        data = dict([(k,self.settings[k]) for k in ('username', 'host', 'port')])
        data['protocol'] = 39
        self.send_packet(Packet(ident=0x02, data=data))

    def create_player(self, packet):
        # named player
        eid = packet.data['entity_id']
        name = packet.data['player_name']
        v = vec_from_data(packet.data)
        v = (1.0/32) * v
        p = Player(eid,name,v)
        print p
        if name == self.target_player:
            self.chat('time to die, '+name)

    def get_chat(self, packet):
        text = packet.data['text']
        username = re.match(r'<(.*?)>', text)
        if not username: return
        username = username.groups()[0]
        if username == 'bot':
            print 'skip self'
            return
        self.chat('i hate ' + username)
        self.target_player = username

    def attack(self, player):
        data = dict()
        data['subject_entity_id'] = self.me.eid
        data['object_entity_id'] = player.eid
        data['left_click'] = True
        self.send_packet(Packet(ident=0x07, data=data))

    def chat(self, text):
        self.send_packet(Packet(ident=0x03, data=dict(text=text)))

    def login(self, packet):
        print 'logging in'
        self.send_packet(Packet(ident=0xcd, data=dict(payload=0)))

    def parselogin(self, packet):
        print 'logged in'
        eid = packet.data['entity_id']
        self.me = Player(eid,self.settings['username'],Vector(0,0,0))

    def print_plugin(self, packet):
        print packet.data['channel'], len(packet.data['data'])

    def update_player(self, packet):
        entity = packet.data['entity_id']
        if entity not in Player.all:
            return
        p = Player.all[entity]
        pos = (1.0/32) * vec_from_data(packet.data)
        p.pos = pos
        if p.name == self.target_player:
            dv = (p.pos - self.me.pos).norm()
            self.me.move(dv)
            print p, self.me
            self.send_packet(Packet(ident=0x0D, data=self.me.get_position_and_look()))

    def rel_update_player(self, packet):
        entity = packet.data['entity_id']
        if entity not in Player.all:
            return
        p = Player.all[entity]
        dpos = (1.0/32) * dvec_from_data(packet.data)
        p.move(dpos)
        if p.name == self.target_player:
            dv = (p.pos - self.me.pos).norm()
            self.me.move(dv)
            print p, self.me
            self.send_packet(Packet(ident=0x0D, data=self.me.get_position_and_look()))
            if dv.mag() < 4:
                print 'attack!'
                self.attack(p)

    def default_handler(self, packet):
        #print names[packet.ident], packet.data.keys()
        ptypes[packet.ident] = ptypes.get(packet.ident, 0) + 1

    def positionandlook(self, packet):
        self.print_packet(packet)
        self.me.set_position_and_look(packet.data)
        self.reflect(packet)
        if not self.spawned:
            self.spawned = True
            print 'Spawned!'
        else:
            print 'server pos correction'
            self.me.move(Vector(*[2*random() - 1 for _ in range(3)]))
            self.me.move(Vector(0,1,0))

    def disconnect(self, packet):
        self.close()


if __name__ == '__main__':
    client = SimpleClient(host='localhost', username='bot', debug_out = True)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        client.close()

    x = [(v,names[k]) for k,v in ptypes.iteritems()]
    x.sort()
    for v,k in x:
        print k,v
