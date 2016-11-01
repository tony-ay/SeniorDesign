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

    def attackMove(self, position):
        for unit in  self.units:
            unit.attack(position)

    def updateCenter(self):
        self.center = Position(0,0)
        for unit in self.units:
            self.center += unit.getPosition()
        self.center /= len(self.units)

    def update(self, bw, events):
    	for e in events:
    		if e.getType() == cybw.EventType.UnitShow:
    			unit = e.getUnit()
    			if unit.getPlayer().getID() != bw.self().getID():
    				bw << "Enemy unit " << unit << " spotted" << "\n"