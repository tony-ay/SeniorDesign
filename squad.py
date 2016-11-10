import cybw
from cybw import Position

# squad class
class Squad:
    def __init__(self,squad_num):
        self.units = []
        self.center = Position(0,0)
        self.Max_units=4
        self.current_units=0
        self.old_current_units=0
        self.squad_leader=None
        self.squad_number=squad_num
        self.reward=0.01
        self.killCounts=[]

    def add(self, unit):
        if self.squad_leader==None:
            self.squad_leader=unit
            self.units.append(unit)
            self.killCounts.append(0)
            self.updateCenter()
            self.current_units+=1
            self.old_current_units+=1
        elif self.current_units<self.Max_units:
            self.units.append(unit)
            self.killCounts.append(0)
            self.updateCenter()
            self.current_units+=1
            self.old_current_units+=1
        else:
            print("To many units in squad %d"%self.squad_number)

    def getNearbyEnemies(self):
        enemies = []
        nearby = self.squad_leader.getUnitsInRadius(self.squad_leader.getType().sightRange())
        for e in nearby:
            if e.getPlayer().getID() != self.squad_leader.getPlayer().getID():
                enemies.append(e)
        return enemies

    def getEnemyPosition(self, enemies):
        enemyPos = self.center
        if len(enemies) > 0:
            for e in enemies:
                enemyPos += e.getPosition()
            enemyPos /= len(enemies)
        return enemyPos

    def retreatFromPosition(self, position):
        sight = self.squad_leader.getType().sightRange()
        retreatVector = position - self.center
        retreatVector = Position(2*retreatVector.getX(), 2*retreatVector.getY())
        retreatPos = self.center - retreatVector
        self.move(retreatPos)

    def retreat(self, enemies):
        enemyPos = self.getEnemyPosition(enemies)
        self.retreatFromPosition(enemyPos)

    def getPosShift(self, position):
        xshift = self.center.getX() - position.getX()
        yshift = self.center.getY() - position.getY()
        return (xshift, yshift)

    def move(self, position):
        for unit in self.units:
            unit.move(position)

    def attackMove(self, position):
        print(position)
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
        
    def update(self, events):
        self.updateCenter()
        self.reward=0.01
        iterator=0
        for unit in self.units:
            if unit.getKillCount()>self.killCounts[iterator]:
                self.killCounts[iterator]= unit.getKillCount()
                self.reward=1
                print("Unit %d got a kill"%iterator)
            if unit.getHitPoints()<=0:
                self.current_units-=1
                self.reward=-1
                self.units.pop(iterator)
                #if squad leader died change3 saud leader
                if iterator==0:
                    self.sqaud_leader=self.units[0]
                
            iterator+=1
