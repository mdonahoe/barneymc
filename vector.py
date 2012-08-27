import math
class Vector(object):
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def __add__(self, other):
        assert isinstance(other, Vector), 'bad type'
        return Vector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )
    def __sub__(self, other):
        assert isinstance(other, Vector), 'bad type'
        other = other * -1
        return self + other
    def __mul__(self, c):
        return Vector(
            self.x * c,
            self.y * c,
            self.z * c
        )
    __rmul__ = __mul__

    def mag(self):
        m2 = self.x * self.x + self.y * self.y + self.z * self.z
        return math.sqrt(m2)

    def norm(self):
        d = 1.0 / self.mag()
        return d*self

    def __repr__(self):
        return '<%s>' % ','.join(str(x) for x in (self.x,self.y,self.z))
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        raise NotImplementedError

if __name__ == '__main__':
    x = Vector(1,2,3)
    print 2*x
    print 2*x - x
