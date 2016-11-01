import cybw

from squad import Squad

from time import sleep

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
            print ("Im here")
            #its called alot but its supposed to fill map with dots of certain color
            #so it makes sense its called alot
            #drawDotMap is an overloaded function of Drawdot but drawdot is not in CYBW
            #so maybe thats why it doesnt work, not sure though since it seems to work
            #but after alot of calls it breaks.
            
            Broodwar.drawDotMap(cybw.Position(x, y), drawColor)

squad = Squad()

print("Connecting...")
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
            elif unit.getType().getName == "Terran_Marine":
                squad.add(unit)

        events = Broodwar.getEvents()
        print(len(events))

    while Broodwar.isInGame():
        units    = Broodwar.self().getUnits()
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

        squad.update(Broodwar, events)

        if show_bullets:
            drawBullets()
        if show_visibility_data:
            drawVisibilityData()
        drawStats()
        Broodwar.drawTextScreen(cybw.Position(300, 0), "FPS: " +
            str(Broodwar.getAverageFPS()))
        client.update()
