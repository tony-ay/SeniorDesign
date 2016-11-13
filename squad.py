import cybw
from cybw import Position

from random import randint

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, vec):
        return Vec2(self.x + vec.x, self.y + vec.y)

    def __sub__(self, vec):
        return Vec2(self.x - vec.x, self.y - vec.y)

    def __mul__(self, vec):
        return Vec2(self.x * vec.x, self.y * vec.y)

    def __div__(self, vec):
        return Vec2(self.x * vec.x, self.y * vec.y)

    def getPosition(self):
        return Position(self.x, self.y)

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
        self.last_squad_leader=True

    def add(self, unit):
        if self.squad_leader==None:
            self.units.append(unit)
            self.squad_leader=unit
            self.killCounts.append(0)
            self.updateCenter()
            self.current_units+=1
            self.old_current_units+=1
            print(self.units)
        elif self.current_units<self.Max_units:
            self.units.append(unit)
            self.killCounts.append(0)
            self.updateCenter()
            self.current_units+=1
            self.old_current_units+=1
            print(self.units)
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
        enemyPos = Position(0,0)
        if len(enemies) > 0:
            for e in enemies:
                enemyPos += e.getPosition()
            enemyPos /= len(enemies)
            return enemyPos
        else:
            return self.center

    def retreatFromPosition(self, position):
        edge =self.squad_leader.getType().sightRange()

        retreatVector = self.center - position
        retreatVector *= 2
        
        mw = cybw.Broodwar.mapWidth()*32
        mh = cybw.Broodwar.mapHeight()*32
        shift = 500
        
        if self.center.getX() < edge:
            retreatVector.setY(-shift)
        elif self.center.getX() > mw - edge:
            retreatVector.setY(shift)
        if self.center.getY() < edge:
            retreatVector.setX(shift)
        elif self.center.getY() > mh - edge:
            retreatVector.setX(-shift)

        retreatPos = self.center + retreatVector
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
        #print(position)
        for unit in  self.units:
            unit.attack(position)

    def attackShift(self, shift):
        for unit in  self.units:
            unit.attack(Position(shift[0] + unit.getPosition().getX(), shift[1] + unit.getPosition().getY()))

    def explore(self):
        amt = 1000
        shift = Position(randint(-amt, amt), randint(-amt, amt))
        pos = self.center + shift
        self.move(pos)

    def updateCenter(self):
        self.center = Position(0,0)
        for unit in self.units:
            self.center += unit.getPosition()
        if len(self.units)>0:
            self.center /= len(self.units)
            
    def update(self, events):
        
        self.reward=0.01
        iterator=0
        for unit in self.units:
            #print(iterator)
            if not unit.exists() :
                #if list has somethhing in it
                if len(self.units)>1:
                    #if squad leader died change sqaud leader
                    if unit== self.squad_leader :
                        print(self.squad_leader)
                        
                        self.units.remove(unit)
                        
                        self.squad_leader=self.units[0]
                       
                        print(self.squad_leader)
                        
                    else:
                        self.units.remove(unit)
                
                    self.current_units-=1
                    self.reward=-1
                elif len(self.units)==1 :
                    if self.last_squad_leader:
                        self.last_squad_leader=False
                        self.reward=-1
            elif unit.getKillCount()>self.killCounts[iterator]:
                self.killCounts[iterator]= unit.getKillCount()
                self.reward=1
                print("Unit %d got a kill"%iterator)
            
            iterator+=1
        self.updateCenter()
   
