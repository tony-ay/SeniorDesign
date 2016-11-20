import cybw
from cybw import Position

from PIL import ImageGrab

import skimage as skimage1
from skimage import transform, color, exposure
from skimage.transform import rotate
from skimage.viewer import ImageViewer
import numpy

from squad import Squad
from DQN import DQN,VDQN

from time import time, sleep
from random import randint

client = cybw.BWAPIClient
Broodwar = cybw.Broodwar

def reconnect():
    while not client.connect():
        sleep(0.5)

def showPlayers():
    players = Broodwar.getPlayers()
    for player in players:
        Broodwar << "Player [" << player.getID() << "]: " << player.getName(
            ) << " is in force: " << player.getForce().getName() << "\n"

def showForces():
    forces = Broodwar.getForces()
    for force in forces:
        players = force.getPlayers()
        Broodwar << "Force " << force.getName() << " has the following players:\n"
        for player in players:
            Broodwar << "  - Player [" << player.getID() << "]: " << player.getName() << "\n"

def drawStats():
    line = 0
    allUnitTypes = cybw.UnitTypes.allUnitTypes()
    Broodwar.drawTextScreen(cybw.Position(5, 0), "I have " +
        str(Broodwar.self().allUnitCount())+" units:")
    for unitType in allUnitTypes:
        count = Broodwar.self().allUnitCount(unitType)
        if count > 0:
            line += 1
            statStr = "- "+str(count)+" "+str(unitType)
            Broodwar.drawTextScreen(cybw.Position(5, 12*line), statStr)

def drawBullets():
    bullets = Broodwar.getBullets()
    for bullet in bullets:
        p = bullet.getPosition()
        velocityX = bullet.getVelocityX()
        velocityY = bullet.getVelocityY()
        lineColor = cybw.Colors.Red
        textColor = cybw.Text.Red
        if bullet.getPlayer == Broodwar.self():
            lineColor = cybw.Colors.Green
            textColor = cybw.Text.Green
        Broodwar.drawLineMap(p, p+cybw.Position(velocityX, velocityY), lineColor)
        Broodwar.drawTextMap(p, chr(textColor) + str(bullet.getType()))

def drawVisibilityData():
    #Gilberto: This function does not work. It breaks python. Not sure why.
    wid = Broodwar.mapWidth()
    hgt = Broodwar.mapHeight()
    for x in range(wid):
        for y in range(hgt):
            drawColor = cybw.Colors.Red
            if Broodwar.isExplored(tileX=x, tileY=y):
                if Broodwar.isVisible(tileX=x, tileY=y):
                    drawColor = cybw.Colors.Green
                else:
                    drawColor = cybw.Colors.Blue
            #used to test how many times this function was called

            #its called alot but its supposed to fill map with dots of certain color
            #so it makes sense its called alot
            #drawDotMap is an overloaded function of Drawdot but drawdot is not in CYBW
            #so maybe thats why it doesnt work, not sure though since it seems to work
            #but after alot of calls it breaks.

            Broodwar.drawDotMap(cybw.Position(x, y), drawColor)
def combatDQN_input(squad,bw):
    #takes combat squad leader unit and returns
    in_sight=False
    #print(squad_leader)
    number_of_enemy_units=0
    number_of_friendly_units=0
    closest_enemy=None
    distance_to_enemy=99999
    total_enemy_Hitpoints=0
    total_friendly_Hitpoints=0
    sett=squad.squad_leader.getUnitsInRadius(squad.squad_leader.getType().sightRange())
    total_enemies = []
    for s in sett:
        if s.getPlayer().getID() != bw.self().getID():
            #number of enemy units in range
            in_sight =True
            number_of_enemy_units+=1
            squad.add_enemy(s)
            #distance to closest enemy
            tmp = squad.squad_leader.getDistance(s)
            if tmp<distance_to_enemy:
                distance_to_enemy=tmp
                closest_enemy=s
            #total health of all enemy units in range
            total_enemy_Hitpoints+=s.getHitPoints()
            total_enemies.append(s)
        if s.getPlayer().getID() == bw.self().getID():
            #number of friendly units in range
            number_of_friendly_units+=1
            total_friendly_Hitpoints+=s.getHitPoints()
    #print(sett)
    #print(number_of_enemy_units)
    #print(distance_to_enemy)
    #print(closest_enemy)
    #print(total_enemy_Hitpoints)
    #print(number_of_freindly_units)

    #Units own health
    own_health=squad.squad_leader.getHitPoints()
    #print(own_health)
    #print(in_sight)
    if squad.squad_number==2:
        squad.update_reward(total_enemies)
    return in_sight, number_of_enemy_units, number_of_friendly_units, distance_to_enemy, closest_enemy, total_enemy_Hitpoints,total_friendly_Hitpoints,own_health,total_enemies


#'?' : (Any character) To train the network from scratch(will overwrite any previous save points)
#'RT': To train the network from last save point(explore,observation,and epsilon reset)
#'R' : To run network with out training or resetting save points
TYPE='T'

# 0 : Runs DQN only when in combat(can change rewards inside code fore decleration of squad)
# 1 : Runs DQN at all times(can change rewards inside code fore decleration of squad)
# 2 : Runs DQN ar all times with different rewards than 1(rewards are calculated inside squad.update_rewards())
# 3 : Runs DQN with image. Make sure to have BroodWar in Windowed mode.
DQNVER=2




if DQNVER==0 or DQNVER==1 or DQNVER==2:
    Combatmodel= DQN(TYPE,DQNVER)
elif DQNVER==3:
    Combatmodel = VDQN(TYPE,DQNVER)

print("Connecting...")
once=True
reconnect()
while True:
    print("waiting to enter match")
    while not Broodwar.isInGame():
        client.update()
        if not client.isConnected():
            print("Reconnecting...")
            reconnect()
    print("starting match!")
    Broodwar.sendText( "Hello world from python!")
    Broodwar.printf( "Hello world from python!")

    
    

    squad = Squad(DQNVER)
    ratioW=(Broodwar.mapWidth()*32)/80
    ratioH=(Broodwar.mapHeight()*32)/80
    
    
    # need newline to flush buffer
    Broodwar << "The map is " << Broodwar.mapName() << ", a " \
        << len(Broodwar.getStartLocations()) << " player map" << " \n"

    # Enable some cheat flags
    Broodwar.enableFlag(cybw.Flag.UserInput)

    show_bullets = False
    show_visibility_data = False

    if Broodwar.isReplay():
        Broodwar << "The following players are in this replay:\n"
        players = Broodwar.getPlayers()
        # TODO add rest of replay actions

    else:
        Broodwar << "The matchup is " << Broodwar.self().getRace() << " vs " << Broodwar.enemy().getRace() << "\n"
        # send each worker to the mineral field that is closest to it
        units    = Broodwar.self().getUnits()
        minerals  = Broodwar.getMinerals()
        print("got", len(units), "units")
        print("got", len(minerals), "minerals")
        for unit in units:
            if unit.getType().isWorker():
                closestMineral = None
                # print("worker")
                for mineral in minerals:
                    if closestMineral is None or unit.getDistance(mineral) < unit.getDistance(closestMineral):
                        closestMineral = mineral
                if closestMineral:
                    unit.rightClick(closestMineral)
            elif unit.getType().isResourceDepot():
                unit.train(Broodwar.self().getRace().getWorker())
            elif unit.getType().getName() == "Terran_Marine":
                squad.add(unit)

        events = Broodwar.getEvents()
        #print(len(events))

    ctr = 200

    while Broodwar.isInGame():
        events = Broodwar.getEvents()
        for e in events:
            eventtype = e.getType()
            if eventtype == cybw.EventType.MatchEnd:
                if e.isWinner():
                    Broodwar << "I won the game\n"
                else:
                    Broodwar << "I lost the game\n"
            elif eventtype == cybw.EventType.SendText:
                if e.getText() == "/show bullets":
                    show_bullets = not show_bullets
                elif e.getText() == "/show players":
                    showPlayers()
                elif e.getText() == "/show forces":
                    showForces()
                elif e.getText() == "/show visibility":
                    show_visibility_data = not show_visibility_data
                else:
                    Broodwar << "You typed \"" << e.getText() << "\"!\n"
            elif eventtype == cybw.EventType.ReceiveText:
                Broodwar << e.getPlayer().getName() << " said \"" << e.getText() << "\"\n"
            elif eventtype == cybw.EventType.PlayerLeft:
                Broodwar << e.getPlayer().getName() << " left the game.\n"
            elif eventtype == cybw.EventType.NukeDetect:
                if e.getPosition() is not cybw.Positions.Unknown:
                    Broodwar.drawCircleMap(e.getPosition(), 40,
                        cybw.Colors.Red, True)
                    Broodwar << "Nuclear Launch Detected at " << e.getPosition() << "\n"
                else:
                    Broodwar << "Nuclear Launch Detected.\n"
            elif eventtype == cybw.EventType.UnitCreate:
                if not Broodwar.isReplay():
                    Broodwar << "A " << e.getUnit() << " has been created at " << e.getUnit().getPosition() << "\n"
                else:
                    if(e.getUnit().getType().isBuilding() and
                      (e.getUnit().getPlayer().isNeutral() == False)):
                        seconds = Broodwar.getFrameCount()/24
                        minutes = seconds/60
                        seconds %= 60
                        Broodwar.sendText(str(minutes)+":"+str(seconds)+": "+e.getUnit().getPlayer().getName()+" creates a "+str(e.getUnit().getType())+"\n")
            elif eventtype == cybw.EventType.UnitDestroy:
                if not Broodwar.isReplay():
                    Broodwar << "A " << e.getUnit() << " has been destroyed at " << e.getUnit().getPosition() << "\n"
            elif eventtype == cybw.EventType.UnitMorph:
                if not Broodwar.isReplay():
                    Broodwar << "A " << e.getUnit() << " has been morphed at " << e.getUnit().getPosition() << "\n"
                else:
                    # if we are in a replay, then we will print out the build order
                    # (just of the buildings, not the units).
                    if e.getUnit().getType().isBuilding() and not e.getUnit().getPlayer().isNeutral():
                        seconds = Broodwar.getFrameCount()/24
                        minutes = seconds/60
                        seconds %= 60
                        Broodwar << str(minutes) << ":" << str(seconds) << ": " << e.getUnit().getPlayer().getName() << " morphs a " << e.getUnit().getType() << "\n"
            elif eventtype == cybw.EventType.UnitShow:
                if not Broodwar.isReplay():
                    Broodwar << e.getUnit() << " spotted at " << e.getUnit().getPosition() << "\n"
            elif eventtype == cybw.EventType.UnitHide:
                if not Broodwar.isReplay():
                    Broodwar << e.getUnit() << " was last seen at " << e.getUnit().getPosition() << "\n"
            elif eventtype == cybw.EventType.UnitRenegade:
                if not Broodwar.isReplay():
                    Broodwar << e.getUnit() << " is now owned by " << e.getUnit().getPlayer() << "\n"
            elif eventtype == cybw.EventType.SaveGame:
                Broodwar << "The game was saved to " << e.getText() << "\n"

        squad.update(events)
        
        
        #for e in events:
        #if e.getType() == cybw.EventType.UnitShow:
        #unit = e.getUnit()
        #if unit.getPlayer().getID() != Broodwar.self().getID():
        
        #for every squad
        in_sight,number_of_enemy_units,number_of_friendly_units, distance_to_enemy, closest_enemy, total_enemy_Hitpoints, total_friendly_Hitpoints, own_health, total_enemies=combatDQN_input(squad,Broodwar)
        #input to DQN for action(correct reward is implimented in sqaud update function)
        
        if DQNVER==0:
            if in_sight:
                a_t=Combatmodel.trainNetwork(squad.reward, number_of_enemy_units, number_of_friendly_units, distance_to_enemy, total_enemy_Hitpoints, total_friendly_Hitpoints, own_health)
                #DQN then decides to attack or retreat
                if a_t[0]==1:
                    #attack closest_enemy
                    #print("Here")
                    squad.attackMove(closest_enemy.getPosition())     
                elif a_t[1]==1:
                    #retreat
                    #print("Not Here")
                    squad.retreat(squad.getNearbyEnemies())
                else:
                    #do nothing
                    print("do nothing")
        
        
            if ctr > 250:
                ctr = 0
                squad.explore()
            else:
                ctr += 1
        elif DQNVER==1 or DQNVER==2:
            a_t=Combatmodel.trainNetwork(squad.reward, number_of_enemy_units, number_of_friendly_units, distance_to_enemy, total_enemy_Hitpoints, total_friendly_Hitpoints, own_health)
            if a_t[0]==1:
                #attack closest_enemy
                if in_sight:
                    squad.attackMove(closest_enemy.getPosition())     
            elif a_t[1]==1:
                #retreat
                squad.retreat(squad.getNearbyEnemies())
            elif a_t[2]==1:
                #explore
                squad.explore()
            else:
                #do nothing
                print("do nothing")
        elif DQNVER==3:
            #get image
            image1=ImageGrab.grab(bbox=(491,759,748,1016))
            #image1.show()
            #sleep(5)
            image = numpy.array(image1)
            image = skimage1.transform.resize(image,(80,80))
            image=skimage1.color.rgb2gray(image)
            image = skimage1.exposure.rescale_intensity(image,out_range=(0,255))
            
            
            
            Combatmodel.trainNetwork(squad.reward,image)
            #use Combatmodel.a_t and Combatmodel.place to get action and do it
            
            
            if Combatmodel.place<6400:
                #chose to move
                x=Combatmodel.place%80
                y=Combatmodel.place/80
                squad.move(Position( ratioW*x,ratioH*y ))
            elif Combatmodel.place>=6400 and Combatmodel.place <12800:
                #chose to attackmove
                x=(Combatmodel.place-6400)%80
                y=(Combatmodel.place-6400)/80
                squad.attackMove(Position(ratioW*x,ratioH*y))
            else:
                print("do nothing")
        else:
            print("Inproper DQNVER input")
        """
        if ctr > 5:
            ctr = 0
            squad.retreat(squad.getNearbyEnemies())
        else:
            ctr += 1
        """

        screen_pos = squad.center - Position(320, 240)
        Broodwar.setScreenPosition(screen_pos)

        if show_bullets:
            drawBullets()
        if show_visibility_data:
            drawVisibilityData()
        drawStats()
        Broodwar.drawTextScreen(cybw.Position(300, 0), "FPS: " +
            str(Broodwar.getAverageFPS()))
        client.update()
