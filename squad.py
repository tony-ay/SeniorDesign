import cybw
from cybw import Position

# squad class
class Squad:
    def __init__(self):
        self.units = []
        self.center = Position(0,0)

    def add(self, unit):
        self.units.append(unit)
        self.updateCenter()

    def getPosShift(self, position):
        xshift = self.center.getX() - position.getX()
        yshift = self.center.getY() - position.getY()
        return (xshift, yshift)

    def attackMove(self, position):
        for unit in  self.units:
            unit.attack(position)

    def attackShift(self, shift):
        for unit in  self.units:
            unit.attack(Position(shift[0] + unit.getPosition().getX(), shift[1] + unit.getPosition().getY()))

    def updateCenter(self):
        self.center = Position(0,0)
        for unit in self.units:
            self.center += unit.getPosition()
        self.center /= len(self.units)

    def update(self, bw, events):
        self.updateCenter()
        for e in events:
            if e.getType() == cybw.EventType.UnitShow:
                unit = e.getUnit()
                if unit.getPlayer().getID() != bw.self().getID():
                    bw << "Enemy unit " << unit << " spotted" << "\n"