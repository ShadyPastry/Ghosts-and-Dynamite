# Henry Woodrow (hwoodrow)
# 15-112 Section G
# Term Project

from tkinter import *
import math, random, time, os, copy

# Keywords: DEBUGGING, IDEA, MOVE, INTERESTING

#
# Shapes
#

class Shape(object):
    def __init__(self, center, w, h):
        self.position = center
        
        self.isImage = False
        self.width = w
        self.height = h
        self.bboxCornerRadius = 2 + ((w**2 + h**2)**0.5)//2
        
        self.ID = "Dummy"
    
    # Returns left, top, right, bottom.
    def getCanvasBoundaries(self, hMargin=0, vMargin=0):
        x, y = self.position.coords()
        halfW, halfH = self.width//2, self.height//2
        
        return [x-halfW-hMargin, y-halfH-vMargin, 
                x+halfW+hMargin, y+halfH+vMargin]
    
    # Returns left, top, right, bottom.
    def getCanvasBoundariesAsLines(self, hMargin=0, vMargin=0):
        topLeft, topRight, botLeft, botRight = self.getCanvasCorners(hMargin, 
                                                   vMargin)
        
        leftLine = Line(topLeft, botLeft)
        topLine = Line(topLeft, topRight)
        rightLine = Line(topRight, botRight)
        botLine = Line(botLeft, botRight)
        
        return [leftLine, topLine, rightLine, botLine]
    
    # Returns topLeft, topRight, botLeft, and botRight as Vector2's
    def getCanvasCorners(self, hMargin=0, vMargin=0):
        left, top, right, bot = self.getCanvasBoundaries(hMargin, vMargin)
        corners = [Vector2(left, top), Vector2(right, top), 
                   Vector2(left, bot), Vector2(right, bot)]
        return corners
    
    def erase(self, data):
        data.canvas.delete(self.ID)
    
    def distanceTo(self, other):
        return self.position.distanceTo(other.position)
    
    @staticmethod
    def deltaDraw(data, sprite):
        if not sprite.isImage:
            left, top, right, bot = sprite.getCanvasBoundaries()
            data.canvas.coords(sprite.ID, (left, top, right, bot))
        else:
            data.canvas.coords(sprite.ID, sprite.position.coords())
    
    # Duplicated from lab1 and slightly modified
    @staticmethod
    def rectangleRectangleCollision(rect1, rect2):
        if (rect1.distanceTo(rect2) > 
            rect1.bboxCornerRadius + rect2.bboxCornerRadius):
            return False
        
        x1, y1 = rect1.position.coords()
        w1, h1 = rect1.width, rect1.height
        
        x2, y2 = rect2.position.coords()
        w2, h2 = rect2.width, rect2.height
        
        # Top left corners' coordinates
        left1, top1 = x1 - w1/2, y1 - h1/2
        left2, top2 = x2 - w2/2, y2 - h2/2
        
        wLeft = w1 if left1 < left2 else w2
        hAbove = h1 if top1 < top2 else h2
        
        xLeft, xRight = min(left1, left2), max(left1, left2)
        yAbove, yBelow = min(top1, top2), max(top1, top2)
        
        # Right rectangle's left edge left of the other's right edge
        horizontalOverlap = (xRight <= xLeft + wLeft)
        
        # Lower rectangle's top edge is above other's bottom edge
        verticalOverlap = (yBelow <= yAbove + hAbove)
        
        return verticalOverlap and horizontalOverlap
    
    @staticmethod
    def rectangleCircleCollision(rect, circ):
        if (rect.distanceTo(circ) > rect.bboxCornerRadius + circ.radius):
            return False
        
        rectX, rectY = rect.position.coords()
        circX, circY = circ.position.coords()
        
        # Closest point on the rectangle's border
        nearestX = max(rectX-rect.width//2, min(circX, rectX+rect.width//2))
        nearestY = max(rectY-rect.height//2, min(circY, rectY+rect.height//2))
        
        # If the closest point is in the circle, there's a collision
        return circ.pointInSelf(Vector2(nearestX, nearestY))
    
    @staticmethod
    def circleCircleCollision(circ1, circ2):
        return circ1.distanceTo(circ2) < circ1.radius + circ2.radius

class Circle(Shape):
    def __init__(self, center, r):
        super().__init__(center, 2*r, 2*r)
        self.radius = r
    
    # Returns whether other is touching self
    def isTouching(self, other):
        if isinstance(other, Rectangle):
            return Shape.rectangleCircleCollision(other, self)
        elif isinstance(other, Circle):
            return Shape.circleCircleCollision(self, other)
    
    def pointInSelf(self, point, margin=0):
        return point.distanceTo(self.position) <= self.radius + margin

class CircleSprite(Circle):
    def __init__(self, data, center, r, color="white", image=None):
        super().__init__(center, r)
        if image == None:
            self.ID = data.canvas.create_oval(self.getCanvasBoundaries(), 
                fill=color, width=0, disabledfill="")
        else:
            self.isImage = True
            self.ID = data.canvas.create_image(center.coords(), image=image)
        self.test = Circle(center, r)
    
    # Given a list of others that have a sprite object, returns which ones 
    # are touching self.
    def touchedOthers(self, others, useTestSprite=False):
        result = set()
        for other in others:
            if (useTestSprite and self.test.isTouching(other.sprite) and 
                not self is other.sprite):
                result.add(other)
            elif self.isTouching(other.sprite) and not self is other.sprite:
                result.add(other)
        
        return result

class Rectangle(Shape):
    def __init__(self, center, w, h):
        super().__init__(center, w, h)
    
    # Returns whether other is touching self
    def isTouching(self, other):
        if isinstance(other, Rectangle):
            return Shape.rectangleRectangleCollision(other, self)
        elif isinstance(other, Circle):
            return Shape.rectangleCircleCollision(self, other)
    
    def pointInSelf(self, point):
        x, y = point.coords()
        left, top, right, bot = self.getCanvasBoundaries()
        return left <= x <= right and top <= y <= bot

class RectangleSprite(Rectangle):
    def __init__(self, data, center, w, h, color="white", image=None):
        super().__init__(center, w, h)
        if image == None:
            self.ID = data.canvas.create_rectangle(self.getCanvasBoundaries(), 
                fill=color, width=0, disabledfill="")
        else:
            self.isImage = True
            self.ID = data.canvas.create_image(center.coords(), image=image)
        self.test = Rectangle(center, w, h)
    
    # Given a list of others that have a sprite object, returns which ones 
    # are touching self.
    def touchedOthers(self, others, useTestSprite=False):
        result = set()
        for other in others:
            if (useTestSprite and self.test.isTouching(other.sprite) and 
                not self is other.sprite):
                result.add(other)
            elif self.isTouching(other.sprite) and not self is other.sprite:
                result.add(other)
        
        return result

class Waypoint(Circle):
    def __init__(self, data, owner, position):
        super().__init__(position, 2)
        self.owner = owner
        data.waypoints.add(self)
        self.ID = None
        self.position = position
        self.alive = True
    
    def __repr__(self):
        return str(self.position)
    
    def onTimerFired(self, data):
        ownerTargets = self.owner.targets
        
        if not self in ownerTargets: data.deadSprites.add(self)
        
        if self.distanceTo(self.owner) < 5 or not self.owner.alive:
            self.alive = False
            if self in ownerTargets:
                ownerTargets.remove(self)
        
#
# Lifeforms
#

class Lifeform(object):
    def __init__(self, data, pos):
        data.lifeforms.add(self)
        
        self.touchedLifeforms = set()
        self.touchedWalls = set()
        
        self.position = pos
        
        self.alive = True
        self.moving = False
        self.turning= False
        self.forward = True
        self.ccw = True
        
        self.weapon = Spike(self, self.cooldownLength)
        self.cooldownTimeLeft = 0
        self.speed = self.maxSpeed
        self.turnSpeed = self.maxTurnSpeed
        self.HP = self.maxHP
        
        self.lookVector = Vector2.EAST.copy()
        
        # Draws the lookVector.
        direction = pos + self.lookVector*(self.sprite.bboxCornerRadius)
        selfX, selfY = self.position.coords()
        dirX, dirY = direction.coords()
        # self.lookVectorID = data.canvas.create_line(selfX, selfY, dirX, dirY)
        self.lookVectorID = data.canvas.create_line(dirX, dirY, dirX+2, dirY+2, 
                                width=3)
    
    def distanceTo(self, other):
        return self.position.distanceTo(other.position)
    
    def kill(self, data):
        self.alive = False
        self.sprite.erase(data)
        data.canvas.delete(self.lookVectorID)
        data.deadSprites.add(self)
        data.canvas.delete("waypointConnection" + str(self.sprite.ID))
    
    def onTimerFired(self, data):
        self.onTickMove(data)
        self.onTickRotate(data)
        
        if self.HP <= 0: self.kill(data)
        
        if self.cooldownTimeLeft > 0:
            self.cooldownTimeLeft = max(0,self.cooldownTimeLeft-data.timerDelay)
        
        # On average, speed recovers by 1 pixelPerSecond every second
        if self.speed < self.maxSpeed:
            if returnsTrueOncePerNSeconds(data, 1):
                self.speed = min(self.speed + 1, self.maxSpeed)
        
        # On average, recovers hpRegen hitpoints every second
        if self.HP < self.maxHP:
            if returnsTrueOncePerNSeconds(data, 1):
                self.HP = min(self.HP + self.hpRegen, self.maxHP)
        
        # data.canvas.coords(self.image, self.position.coords())
        self.deltaDraw(data)
    
    def deltaDraw(self, data):
        # Redraws the lookVector
        direction = (self.sprite.position + 
                     self.lookVector*(self.sprite.bboxCornerRadius))
        dirX, dirY = direction.coords()
        selfX, selfY = self.position.coords()
        # data.canvas.coords(self.lookVectorID, (selfX, selfY, dirX, dirY))
        data.canvas.coords(self.lookVectorID, (dirX, dirY, dirX+2, dirY+2))
        
        # Updates the sprite's position on screen
        Shape.deltaDraw(data, self.sprite)
    
    def takeDamage(self, data, amount):
        self.HP = max(0, self.HP - amount)
        if amount != 0:
            x, y = self.position.coords()
            y -= self.sprite.height//2
            ID = data.canvas.create_text(x, y, text=str(amount), 
                font="Arial 8 bold", fill="black")
            data.canvas.after(1000, data.canvas.delete, ID)
    
    #
    # Movement
    #
    
    # Pixels per timerFired
    def moveDistance(self, data):
        return self.speed/data.timerFiredsPerSecond
    
    # Radians per timerFired
    def turnDistance(self, data):
        return self.turnSpeed/data.timerFiredsPerSecond
    
    def onTickMove(self, data):
        if self.moving: self.move(data, self.moveDistance(data))
    
    def onTickRotate(self, data):
        if self.turning: self.rotate(self.turnDistance(data))
    
    def move(self, data, dist):
        startX, startY = self.position.coords()
        
        moveVector = self.lookVector*dist
        
        if self.forward: self.position += moveVector
        else: self.position -= moveVector
        self.sprite.position = self.position
        
        if not self.isLegalPosition(data, updateTouched=True):
            
            # Creates a sliding effect
            newX, newY = self.position.coords()
            
            # Try reverting only the x movement...
            self.position.x = startX
            self.sprite.position = self.position
            
            # If still not legal, then try reverting only the y movement...
            if not self.isLegalPosition(data):
                self.position.x, self.position.y = newX, startY
                self.sprite.position = self.position
            
                # If still not legal, then revert both
                if not self.isLegalPosition(data):
                    self.position.x, self.position.y = startX, startY
                    self.sprite.position = self.position
    
    def rotate(self, deltaAngle):
        self.lookVector.rotate(self.position, deltaAngle, self.ccw)
    
    def nearbyOthers(self, others, radius):
        result = set()
        for other in others:
            if not self is other and self.distanceTo(other) <= radius:
                result.add(other)
        
        return result
    
    def isLegalPosition(self, data, useTestSprite=False, updateTouched=False):
        touchedWalls = self.sprite.touchedOthers(data.walls, useTestSprite)
        touchedLifeforms = self.sprite.touchedOthers(data.lifeforms, 
                               useTestSprite)
        
        if updateTouched:
            self.touchedWalls = touchedWalls
            self.touchedLifeforms = touchedLifeforms
        
        return len(touchedWalls) + len(touchedLifeforms) == 0
    
    # Returns whether other would collide with self moving from start to end
    def isBlockingOther(self, data, other, start, end):
        left, top, right, bot = self.sprite.getCanvasBoundaries()
        w, h = other.sprite.width, other.sprite.height
        
        xLeft, xRight = min(start.x, end.x), max(start.x, end.x)
        yTop, yBot = min(start.y, end.y), max(start.y, end.y)
        
        if ((xLeft > right or xRight < left) or 
            (yTop > bot or yBot < top)):
            return False
        
        # Move the test sprite, not the actual sprite.
        other = other.sprite.test
        
        boundaryLines = self.sprite.getCanvasBoundariesAsLines()
        startToEndLine = Line(start, end)
        
        m = other.bboxCornerRadius
        for boundaryLine in boundaryLines:
            intersection = startToEndLine.getIntersection(boundaryLine)
            
            if intersection == None: continue
            
            if not (start.x-m < intersection.x < end.x+m or 
                    end.x-m < intersection.x < start.x+m): continue
            
            if not (start.y-m < intersection.y < end.y+m or 
                    end.y-m < intersection.y < start.y+m): continue
            
            other.position = intersection
            if other.isTouching(self.sprite): return True
        
        return False
    
#
# Lifeforms (enemies)
#

class Enemy(Lifeform):
    def __init__(self, data, pos):
        super().__init__(data, pos)
        data.enemies.add(self)
        
        self.targets = [data.player]
        self.target = data.player
        
        self.moving = True
        self.turning = True
        
        self.hitByPlayer = False
    
    def initPossibleWaypoints(self, data):
        if type(self).waypointGraph != None: return
        
        waypointGraph = Graph(weightFunc=Vector2.distanceTo)
        
        margins = (2+self.sprite.width//2, 2+self.sprite.height//2)
        test = self.sprite.test
        
        # Waypoints are set outwards of walls' corners
        for wall in data.walls:
            outerPoints = wall.sprite.getCanvasCorners(margins[0], margins[1])
            
            # Only include waypoints that are legal positions
            for point in outerPoints:
                test.position = point
                x, y = test.position.coords()
                if (0 < x < data.canvasWidth-data.menuWidth and 
                    0 < y < data.canvasHeight and 
                    len(self.sprite.touchedOthers(data.walls, True)) == 0):
                    waypointGraph.addVertex(point)
        
        # Only connect waypoints that don't have a wall between them
        filterFunc = lambda v1, v2: not self.wallsAreBlockingPath(data, v1, v2)
        waypointGraph.connectAll(filterFunc)
        
        type(self).waypointGraph = waypointGraph
    
    def kill(self, data):
        super().kill(data)
        if self.hitByPlayer:
            money = type(self).value
            exp = money
            data.player.money += money
            data.exp += exp
            data.enemiesKilled += 1
    
    def onTimerFired(self, data):
        super().onTimerFired(data)
        self.updateTarget(data)
        
        tag = "waypointConnection" + str(self.sprite.ID)
        data.canvas.delete(tag)
        
        if data.debugging:
            data.canvas.create_line(self.targets[0].position.coords(), 
                self.position.coords(), tag=tag)
            for i in range(1, len(self.targets)):
                data.canvas.create_line(self.targets[i-1].position.coords(), 
                    self.targets[i].position.coords(), 
                    tag=tag)
        
        if not self.alive:
            data.canvas.delete("waypointConnection" + str(self.sprite.ID))
    
    def onTickRotate(self, data):
        if self.turning: self.turnTowardsTarget(data)
    
    def turnTowardsTarget(self, data):
        lookVector = self.lookVector
        target = self.target
        selfToTarget = self.target.position - self.position
        
        angleToTarget = lookVector.angleBetween(selfToTarget)
        
        self.ccw = angleToTarget < 0
        
        # So the enemy doesn't turn past the target.
        # It turns more slowly once it's within maxError radians.
        maxError = math.radians(2)
        if abs(angleToTarget) > self.turnDistance(data):
            self.rotate(self.turnDistance(data))
        elif abs(angleToTarget) > maxError:
            self.rotate(maxError/data.timerFiredsPerSecond)
    
    def updateTarget(self, data):
        player = data.player
        
        if not self.wallsAreBlockingPath(data, self.position, player.position):
            self.targets = [player]
        elif self.wallsAreBlockingPath(data, self.position, 
            self.target.position):
            self.avoidWalls(data)
    
        lastTargetIndex = len(self.targets)-1
        if lastTargetIndex > 0: # i.e. If there is more than one target
            if not self.wallsAreBlockingPath(data, self.position, 
                                             self.targets[1].position):
                self.targets.pop(0)
            
            elif self.wallsAreBlockingPath(data, 
                self.targets[lastTargetIndex-1].position, player.position):
                self.avoidWalls(data)
        
        self.target = self.targets[0]
    
    def avoidWalls(self, data):
        selfPos = self.position
        
        start, end = self.findOptimumEndpoints(data, selfPos, 
                     data.player.position, type(self).waypointGraph.vertices)
        
        # Don't update the path
        if start == None or end == None: return
        
        path = type(self).waypointGraph.estimateLeastWeightedPath(start, end)
        
        # Converts path to a list of waypoints
        path = list(map(lambda pos: Waypoint(data, self, pos), path))
        
        # Player is always the last target
        self.targets = path + [data.player]
    
    # Check that walls do not block the path between adjacent points
    def isLegalPath(self, data, path):
        for end in range(1, len(path)):
            if self.wallsAreBlockingPath(data, path[end-1], path[end]):
                return False
        return True
    
    # Given start, end, and a list of points, returns the best approximation of 
    # start and end in points
    def findOptimumEndpoints(self, data, start, end, points):
        startCell = getCellFromPosition(data, start)
        endCell = getCellFromPosition(data, end)
        endpointsDict = type(self).optimumEndpoints
        
        originalStart, originalEnd = start, end
        start = endpointsDict.get(startCell, False)
        end = endpointsDict.get(endCell, False)
        
        if start == False:
            start = originalStart
            smallestDistance = None
            
            # Find the closest reachable waypoint to start
            for point in points:
                distance = originalStart.distanceTo(point)
                if smallestDistance == None or distance < smallestDistance:
                    if self.wallsAreBlockingPath(data, originalStart, point):
                        continue
                    start = point
                    smallestDistance = distance
            
            # D:
            if not start in points: start = None
        
        if end == False:
            end = originalEnd
            smallestDistance = None
            
            # Find the closest waypoint to end that can reach end
            for point in points:
                distance = originalEnd.distanceTo(point)
                if smallestDistance == None or distance < smallestDistance:
                    if self.wallsAreBlockingPath(data, originalEnd, point):
                        continue
                    end = point
                    smallestDistance = distance
            
            # D:
            if not end in points: end = None
        
        # if isinstance(self, Explosive):
        #     data.canvas.create_line(originalStart.coords(), start.coords(),
        #     fill="red")
        endpointsDict[startCell] = start
        
        # if isinstance(self, Explosive):
        #     data.canvas.create_line(originalEnd.coords(), end.coords(),
        #     fill="red")
        endpointsDict[endCell] = end
        
        return start, end
    
    # Given start, end, and a list of points, returns the best approximation of 
    # start and end in points for the purposes of pathfinding
    def findOptimumPoint(self, data, start, end, points):
        
        smallestDistance = None
        optimumPoint = None
        
        # Find the closest waypoint to end that can be reached from start
        for point in points:
            if self.wallsAreBlockingPath(data, start, point): continue
            distance = end.distanceTo(point)
            
            if smallestDistance == None or distance < smallestDistance:
                optimumPoint = point
                smallestDistance = distance
        
        if optimumPoint == None:
            # DEBUGGING
            print("Line 652: Awww", 
                  findNearestPoint(end, points).coords())
            
            return findNearestPoint(end, points)
        
        return optimumPoint
    
    def wallsAreBlockingPath(self, data, start, end):
        for wall in data.walls:
            if wall.isBlockingOther(data, self, start, end): return True
        
        return False
    
    # IDEA: Turn speed depends on distance to enemy
    def turnAwayFromEnemies(self, data):
        selfPos = self.position
        
        visionDistance = 30
        visionRadius = 5
        visionAngle = math.radians(100)
        
        avoidee = None
        closestDistance = None
        
        for other in data.enemies:
            # Don't avoid self
            if other is self: continue
            
            # Subtract self.sprite.bboxCornerRadius to account for self's size
            # Subtract other.sprite.bboxCornerRadius to account for other's size
            distance = (self.distanceTo(other) - self.sprite.bboxCornerRadius - 
                other.sprite.bboxCornerRadius)
            
            # Don't avoid far away enemies
            if distance > visionDistance: continue
            
            selfToEnemy = other.position - selfPos
            if distance > visionRadius:
                
                if abs(selfToEnemy.angleBetween(self.lookVector)) > visionAngle:
                    continue
                
                # Don't avoid enemies who aren't blocking self's path
                if not other.isBlockingOther(data, self, selfPos, 
                    self.target.position):
                    continue
            
            if avoidee == None or distance < closestDistance:
                closestDistance = distance
                avoidee = other
        
        # If there's something to avoid, start avoiding.  If not, then stop.
        if avoidee != None:
            # Always avoid Explosives since they won't avoid self
            if (not isinstance(avoidee, Explosive) and 
                self.distanceTo(self.target) < avoidee.distanceTo(self.target)):
                self.turning = True
            else:
                self.turning = False
        else:
            self.turning = True
            return
        
        # targetToSelf = selfPos - self.target.position
        # targetToAvoidee = avoidee.position - self.target.position
        
        selfToTarget = self.target.position - selfPos
        selfToAvoidee = avoidee.position - selfPos
        
        self.ccw = selfToTarget.angleBetween(selfToAvoidee) > 0
        
        # INTERESTING: < 0 creates a clustering effect :o
        # self.ccw = self.lookVector.crossProduct(avoidee.lookVector) > 0
        
        turnDist = math.radians(4)
        # turnDist = self.turnDistance(data)
        
        self.rotate(turnDist)

# Doesn't turn away from enemies.  This is meant to be a "slow and dumb but 
# very powerful"-type enemy.  It still plots paths around walls.
class Explosive(Enemy):
    def __init__(self, data, pos):
        self.sprite = RectangleSprite(data, pos, Explosive.width, 
            Explosive.height, Explosive.color, image=Explosive.image)
        super().__init__(data, pos)
    
    def onTimerFired(self, data):
        super().onTimerFired(data)
        if len(self.touchedLifeforms) > 0:
            self.weapon.activate(data)
            self.kill(data)
    
    def kill(self, data):
        super().kill(data)
        data.canvas.delete(self.image)
        Explosion(data, self.position)
        
# Turns away from nearby enemies and plots paths around walls.
class Zombie(Enemy):
    def __init__(self, data, pos):
        self.sprite = CircleSprite(data, pos, Zombie.radius, Zombie.color, 
            image=Zombie.image)
        super().__init__(data, pos)
    
    def onTimerFired(self, data):
        super().onTimerFired(data)
        self.turnAwayFromEnemies(data)
        if len(self.touchedLifeforms) > 0: self.weapon.activate(data)

#
# Lifeforms (player)
#

class Player(Lifeform):
    def __init__(self, data, pos):
        self.sprite = CircleSprite(data, pos, Player.radius, Player.color, 
            image=Player.image)
        super().__init__(data, pos)
        self.money = 0
        
        self.weapon = Wand(self)
        self.firingAtCursor = False
        self.firingAtLookVector = False
    
    def kill(self, data):
        super().kill(data)
        data.gameOver = True
    
    def onTimerFired(self, data):
        super().onTimerFired(data)
        if self.firingAtCursor:
            x = data.canvas.winfo_pointerx() - data.canvas.winfo_rootx()
            y = data.canvas.winfo_pointery() - data.canvas.winfo_rooty()
            self.weapon.activate(data, Vector2(x, y))
        elif self.firingAtLookVector:
            self.weapon.activate(data, self.position + self.lookVector)
    
    def onKeyPressed(self, data, keysym):
        k = keysym
        if k == "Up" or k == "w":
            self.moving, self.forward = True, True
        elif k == "Down" or k == "s":
            self.moving, self.forward = True, False
        elif k == "Left" or k == "a":
            self.turning, self.ccw = True, True
        elif k == "Right" or k == "d":
            self.turning, self.ccw = True, False
        elif k == "z" or k == "m":
            self.firingAtLookVector = True
    
    def onKeyReleased(self, data, keysym):
        k = keysym
        if k == "Up" or k == "Down" or k == "w" or k == "s":
            self.moving = False
        elif k == "Left" or k == "Right" or k == "a" or k =="d":
            self.turning = False
        elif k == "z" or k == "m":
            self.firingAtLookVector = False
    
    def onLeftMousePressed(self, data, x, y):
        if not self.firingAtLookVector:
            self.firingAtCursor = True
    
    def onLeftMouseReleased(self, data, x, y):
        self.firingAtCursor = False

#
# Terrain
#

class Terrain(object):
    def __init__(self, data, pos):
        data.terrain.add(self)
        
        self.alive = True
        self.position = pos
    
    # Returns whether other would collide with self moving from start to end
    def isBlockingOther(self, data, other, start, end):
        left, top, right, bot = self.sprite.getCanvasBoundaries()
        w, h = other.sprite.width, other.sprite.height
        hMargin, vMargin = w//2, h//2
        
        xLeft, xRight = min(start.x, end.x)-hMargin, max(start.x, end.x)+hMargin
        yTop, yBot = min(start.y, end.y)-vMargin, max(start.y, end.y)+vMargin
        
        if ((xLeft > right or xRight < left) or 
            (yTop > bot or yBot < top)):
            return False
        
        # Move the test sprite, not the actual sprite.
        other = other.sprite.test
        
        boundaryLines = self.sprite.getCanvasBoundariesAsLines()
        startToEndLine = Line(start, end)
        
        for boundaryLine in boundaryLines:
            intersection = startToEndLine.getIntersection(boundaryLine)
            
            if intersection == None: continue
            
            if not (start.x-hMargin < intersection.x < end.x+hMargin or 
                    end.x-hMargin < intersection.x < start.x+hMargin): continue
            
            if not (start.y-vMargin < intersection.y < end.y+vMargin or 
                    end.y-vMargin < intersection.y < start.y+vMargin): continue
            
            other.position = intersection
            if other.isTouching(self.sprite): return True
        
        return False
    
    def onTimerFired(self, data): pass
    
    def destroy(self, data):
        self.sprite.erase(data)
        self.alive = False
        data.deadSprites.add(self)

class Wall(Terrain):
    def __init__(self, data, pos, w, h, fixed=False):
        super().__init__(data, pos)
        data.walls.add(self)
        self.sprite = RectangleSprite(data, pos, w, h, Wall.color)
        self.fixed = fixed
    
    def destroy(self, data):
        if self.fixed: return
        else: super().destroy(data)

class DamageTile(Terrain):
    def __init__(self, data, pos, spriteClass, dimensions, color, damageFunc):
        super().__init__(data, pos)
        self.sprite = spriteClass(data, pos, dimensions, color=color)
        self.damageFunc = damageFunc
        self.cooldownLength = 500
        self.cooldownTimeLeft = 0
        
        self.touchedLifeforms = set()
    
    def onTimerFired(self, data):
        super().onTimerFired(data)
        
        if self.cooldownTimeLeft > 0:
            self.cooldownTimeLeft = max(0,self.cooldownTimeLeft-data.timerDelay)
        else:
            self.touchedLifeforms = self.sprite.touchedOthers(data.lifeforms)
            for other in self.touchedLifeforms:
                damage = self.damageFunc(other)
                if damage == 0: continue
                other.takeDamage(data, damage)
                self.cooldownTimeLeft = self.cooldownLength

class Explosion(DamageTile):
    def __init__(self, data, pos):
        super().__init__(data, pos, CircleSprite, Explosion.radius, 
            Explosion.color, lambda other: 250)
        self.age = 0
    
    def onTimerFired(self, data):
        super().onTimerFired(data)
        
        if self.age > 0.05: self.destroy(data)
        else: self.age += data.timerDelay/1000

#
# Maps
#

# Duplicated from hw10 and slightly modified
def initHFractalMap(data):
    depth = 2
    
    xc = (data.canvasWidth-data.menuWidth)//2
    yc = data.canvasHeight//2
    
    vMargin = 30
    hMargin = 10
    w = (data.canvasWidth-data.menuWidth)//2 - hMargin
    h = data.canvasHeight//2 - vMargin
    
    drawHFractal(data, xc, yc, w, h, depth)

# Omits the middle horizontal bar so the inside of the map can be crossed
def drawH(data, xc, yc, w, h):
    canvas = data.canvas
    
    xcLeft = xc - w/2
    xcRight = xc + w/2
    # ycTop = yc - h/2
    # ycBot = yc + h/2
    
    wallThickness = 7
    
    # Middle horizontal bar
    # Wall(data, Vector2(xc, yc), w, wallThickness)
    
    # Left vertical bar
    Wall(data, Vector2(xcLeft, yc), wallThickness, h)
    
    # Right vertical bar
    Wall(data, Vector2(xcRight, yc), wallThickness, h)

def drawHFractal(data, xc, yc, w, h, level):
    drawH(data, xc, yc, w, h)
    if level > 0:
        # New H's are half the width and height
        w /= 2
        h /= 2
        xcLeft = xc - w
        xcRight = xc + w
        ycTop = yc - h
        ycBot = yc + h
        
        # Draw an H at the top left, top right, bottom left, and bottom right
        drawHFractal(data, xcLeft, ycTop, w, h, level-1)
        drawHFractal(data, xcRight, ycTop, w, h, level-1)
        drawHFractal(data, xcLeft, ycBot, w, h, level-1)
        drawHFractal(data, xcRight, ycBot, w, h, level-1)

#
# Weapon
#

class Weapon(object):
    def __init__(self, owner, cooldown):
        self.equipped = True
        
        self.cooldown = cooldown
        self.minCooldown = 250
        self.owner = owner
        self.power = 0
    
    def purchaseUpgrade(self, cost):
        remainingMoney = self.owner.money - cost
        if remainingMoney < 0: return False
        else: self.owner.money = remainingMoney
        return True
    
    def upgradePower(self):
        cost = 5
        if self.purchaseUpgrade(cost): self.power += 1
    
    def upgradeCooldown(self):
        if self.cooldown <= self.minCooldown:
            self.cooldown = self.minCooldown
            return False
        cost = 10
        if self.purchaseUpgrade(cost): self.cooldown -= 20
    
    def activate(self):
        if self.owner.cooldownTimeLeft > 0: return False
        self.owner.cooldownTimeLeft = self.cooldown
        return True
    
    def calculateDamage(self, defender, attacker=None):
        # DEBUGGING
        # return 0
        
        if attacker == None: attacker = self.owner
        
        if attacker is defender: return 0
        
        ATK = attacker.strength + (self.power)**0.75
        DEF = defender.defence
        
        # No damage dealt if the attacker or defender is already dead
        if attacker.HP < 0 or defender.HP < 0: return 0
        
        # Damage formula depends on how large the gap between ATK and DEF is
        cutoff1 = 10
        
        powerGap = ATK - DEF
        if powerGap <= 0:
            return random.randint(1, 10) # Ignores multipliers
        elif powerGap <= cutoff1:
            baseDamage = cutoff1 + powerGap**2
        else:
            baseDamage = powerGap*cutoff1
        
        damage = int(baseDamage)
        
        # DEBUGGING
        if damage < 0: print("Negative damage?!  D:")
        
        # print("Line 908: ", damage, " damage dealt.")
        return max(0, damage)
    
# Enemy weapon.  Simply damage whatever it touches.
class Spike(Weapon):
    def __init__(self, owner, cooldown):
        super().__init__(owner, cooldown)
    
    # Friendly fire is intentional
    def activate(self, data, attacker=None):
        if not super().activate(): return False
        for other in self.owner.touchedLifeforms:
            damage = self.calculateDamage(other, attacker)
            other.takeDamage(data, damage)

# Player weapon.  Shoots projectiles
class Wand(Weapon):
    initialCooldown = 500 # milliseconds
    def __init__(self, owner):
        super().__init__(owner, Wand.initialCooldown)
        self.bullets = 1.0
        self.maxBullets = 8
        
        self.bulletSize = 3
        self.maxBulletSize = 7
        
        self.bulletSpeed = 100 # pixels per second
        self.maxBulletSpeed = 150 # pixels per second
        
        self.bulletDuration = 500 # milliseconds
        self.maxBulletDuration = 1600 # milliseconds
    
    def upgradeBullets(self):
        if self.bullets >= self.maxBullets:
            self.bullets = self.maxBullets
            return False
        cost = 10
        if self.purchaseUpgrade(cost): self.bullets += 0.1
    
    def upgradeBulletSize(self):
        if self.bulletSize >= self.maxBulletSize: return False
        cost = 5
        if self.purchaseUpgrade(cost): self.bulletSize += 1
    
    def upgradeBulletSpeed(self):
        if self.bulletSpeed >= self.maxBulletSpeed : return False
        cost = 5
        if self.purchaseUpgrade(cost): self.bulletSpeed += 1
    
    def upgradeBulletDuration(self):
        if self.bulletDuration >= self.maxBulletDuration:return False
        cost = 5
        if self.purchaseUpgrade(cost): self.bulletDuration += 25 # milliseconds
    
    # Creates a projectile at owner's position moving towards a target position
    def activate(self, data, target):
        if not super().activate(): return False
        owner = self.owner
        ownerPos = owner.position
        direction = (target - ownerPos).unit()
        
        if random.random() <= self.bullets%1: bullets = math.ceil(self.bullets)
        else: bullets = math.floor(self.bullets)
        
        damageFunc = lambda defender: self.calculateDamage(defender, 
                                          attacker=self.owner)
        
        # Can fire multiple bullets in a fan shape
        for i in range(1, bullets+1):
            rotation = i//2 * math.radians(45)
            if i%2 == 0: rotation *= -1
            
            tempDir = direction.copy()
            tempDir.rotate(ownerPos, rotation)
            
            Projectile(data, owner, ownerPos, tempDir, self.bulletSize, 
                self.bulletSpeed, self.bulletDuration, damageFunc)

class Projectile(DamageTile):
    def __init__(self, data, owner, pos, direction, size, speed, duration, 
        damageFunc):
            
        super().__init__(data, pos, CircleSprite, size, "snow", damageFunc)
        
        self.owner = owner
        self.direction = direction
        self.speed = speed
        self.duration = duration
        self.age = 0
    
    # Pixels per timerFired
    def moveDistance(self, data):
        return self.speed/data.timerFiredsPerSecond
    
    def onTickMove(self, data):
        self.move(self.moveDistance(data))
    
    def move(self, dist):
        self.position += self.direction*dist
        self.sprite.position = self.position
        
    def onTimerFired(self, data):
        super().onTimerFired(data)
        if isinstance(self.owner, Player):
            for hitObject in self.touchedLifeforms:
                if isinstance(hitObject, Enemy):
                    hitObject.hitByPlayer = True
        self.onTickMove(data)
        Shape.deltaDraw(data, self.sprite)
        
        if self.age >= self.duration: self.destroy(data)
        self.age += data.timerDelay
    
#
# Generic helpers
#

def almostEqual(d1, d2, epsilon=10**-7):
    return (abs(d2 - d1) < epsilon)

def findNearestPoint(point, otherPoints):
    if len(otherPoints) == 0: return None
    nearestDistance = None
    for otherPoint in otherPoints:
        dist = (otherPoint - point).magnitude()
        if nearestDistance == None or dist < nearestDistance:
            nearestDistance = dist
            nearestPoint = otherPoint
    
    return nearestPoint

def getCellFromPosition(data, v):
    x, y = v.coords()
    row = y//data.rowHeight
    col = x//data.colWidth
    return (row, col)

# Duplicated from:
# http://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html#memoization
def powerset(a):
    if (len(a) == 0):
        return [[]]
    else:
        allSubsets = [ ]
        for subset in powerset(a[1:]):
            allSubsets += [subset]
            allSubsets += [[a[0]] + subset]
        return allSubsets

def randomlyPlaceEnemy(data, enemyClass):
    maxAttempts = 50
    # So enemies don't spawn unreasonably close to the player or each other
    minDistFromOthers = 100
    edgeMargin = 50
    
    # Does nothing if it fails too many times
    for i in range(maxAttempts):
        randX = random.randrange(edgeMargin, 
                    data.canvasWidth-edgeMargin-data.menuWidth)
        randY = random.randrange(edgeMargin, data.canvasHeight-edgeMargin)
        
        newEnemy = addEnemy(enemyClass, data, Vector2(randX, randY))
        
        if (not newEnemy.isLegalPosition(data) or 
            len(newEnemy.nearbyOthers(data.lifeforms, minDistFromOthers)) > 0):
                
            data.lifeforms.discard(newEnemy)
            data.enemies.discard(newEnemy)
            newEnemy.alive = False
            data.canvas.delete(newEnemy.lookVectorID)
            newEnemy.sprite.erase(data)
        else:
            if enemyClass.waypointGraph == None:
                newEnemy.initPossibleWaypoints(data)
            return True
        
    return False

def addEnemy(enemyClass, data, pos):
    enemy = enemyClass(data, pos)
    return enemy

def placeWall(data, pos, width, height):
    for wall in data.walls:
        if wall.sprite.pointInSelf(pos): return False
    x, y = pos.coords()
    right = x+width//2
    if right > data.canvasWidth-data.menuWidth: return False
    w = Wall(data, pos, width, height)
    if w.sprite.isTouching(data.player.sprite):
        w.destroy(data)
        return False

def removeWall(data, pos):
    for wall in data.walls:
        if wall.sprite.pointInSelf(pos): wall.destroy(data)

# Assumes it's being called every timerFired
# ON AVERAGE, it returns true once per n seconds
def returnsTrueOncePerNSeconds(data, n):
    a = random.randrange(int(data.timerFiredsPerSecond*n))
    return a == 0

def updateLevel(data):
    if data.exp >= data.expToProgress:
        data.level += 1
        data.exp -= data.expToProgress
        data.expToProgress = 50 + data.level*(2*random.random() - 1)
        
        l = data.level
        for enemyType in data.enemyTypes:
            enemyType.strength += l%2
            enemyType.defence += l%2
            enemyType.maxSpeed += 1
            enemyType.maxHP += 100
            if data.spawnInterval != 6.0:
                data.spawnInterval = max(6.0, data.spawnInterval-0.1)

#
# Buttons
#

def upgradePowerButtonPressed(data):
    data.player.weapon.upgradePower()

def upgradeCooldownButtonPressed(data):
    if data.player.weapon.upgradeCooldown() == False:
        data.upgradeCooldownButton.configure(state=DISABLED, 
            text="Cooldown MAXED")

def upgradeBulletsButtonPressed(data):
    if data.player.weapon.upgradeBullets() == False:
        data.upgradeBulletsButton.configure(state=DISABLED, 
            text="Bullets MAXED")

def upgradeBulletSizeButtonPressed(data):
    if data.player.weapon.upgradeBulletSize() == False:
        data.upgradeBulletSizeButton.configure(state=DISABLED, 
            text="Bullet Size MAXED")

def upgradeBulletSpeedButtonPressed(data):
    if data.player.weapon.upgradeBulletSpeed() == False:
        data.upgradeBulletSpeedButton.configure(state=DISABLED, 
            text="Bullet Speed MAXED")

def upgradeBulletDurationButtonPressed(data):
    if data.player.weapon.upgradeBulletDuration() == False:
        data.upgradeBulletDurationButton.configure(state=DISABLED, 
            text="Bullet Duration MAXED")

def startGameButtonPressed(data):
    if data.gameStarted:
        resetGame(data)
        return
    
    data.spawnEnemiesButton.configure(state=ACTIVE)
    data.startGameButton.configure(state=DISABLED)
    
    # Can't edit walls once the game starts
    if data.editingWalls: data.editingWallsButton.invoke()
    data.hFractalMapButton.configure(state=DISABLED)
    data.editingWallsButton.configure(state=DISABLED)
    data.wallWidthEntry.configure(state=DISABLED)
    data.wallHeightEntry.configure(state=DISABLED)
    data.clearWallsButton.configure(state=DISABLED)
    
    data.startGameButton.configure(text="LOADING: Please wait")
    
    def temp1():
        for enemyType in data.enemyTypes:
            randomlyPlaceEnemy(data, enemyType)
        
        for newEnemy in data.enemies:
            data.deadSprites.add(newEnemy)
            newEnemy.alive = False
            data.canvas.delete(newEnemy.lookVectorID)
            newEnemy.sprite.erase(data)
        
        data.startGameButton.configure(text="Reset game")
        def temp2():
            data.gameStarted = True
            data.startGameButton.configure(state=NORMAL)
        data.canvas.after(1000, temp2)
    
    data.canvas.after(10, temp1)

def resetGame(data):
    oldWalls = copy.deepcopy(data.walls)
    for terrain in data.terrain:
        terrain.destroy(data)
    
    for lifeform in data.lifeforms:
        lifeform.kill(data)
    
    for corpse in data.deadSprites:
        for group in [data.terrain, data.lifeforms, data.waypoints, 
                      data.enemies, data.walls]:
            group.discard(corpse)
    
    for enemyType in data.enemyTypes:
        enemyType.waypointGraph = None
    
    data.canvas.delete("all")
    
    init(data)
    for wall in oldWalls:
        if not wall.fixed: Wall(data, wall.position, wall.sprite.width, 
                               wall.sprite.height)

def spawnEnemiesButtonPressed(data):
    if len(data.enemies) >= 10: return False
    
    if data.gameOver:
        enemyTypes = data.enemyTypes
    elif data.level == 0:
        enemyTypes = [Explosive]
    elif data.level == 1:
        enemyTypes = [Zombie]
    else:
        enemyTypes = data.enemyTypes
    
    enemyType = random.sample(enemyTypes, 1)
    randomlyPlaceEnemy(data, enemyType[0])

def gameStatsButtonPressed(data):
    data.gameStatsButton.configure(state=DISABLED)
    data.helpButton.configure(state=NORMAL)
    data.returnToGameButton.configure(state=NORMAL)
    
    # Pauses the game
    if not data.paused: data.pauseButton.invoke()
    data.pauseButton.configure(state=DISABLED)
    
    data.startGameButton.configure(state=DISABLED)
    data.spawnEnemiesButton.configure(state=DISABLED)
    data.hFractalMapButton.configure(state=DISABLED)
    data.editingWallsButton.configure(state=DISABLED)
    data.wallWidthEntry.configure(state=DISABLED)
    data.wallHeightEntry.configure(state=DISABLED)
    data.clearWallsButton.configure(state=DISABLED)
    
    data.screen = data.STATS

def pauseButtonPressed(data):
    data.paused = not data.paused
    text = "Pause" if not data.paused else "Unpause"
    data.pauseButton.configure(text=text)

def helpButtonPressed(data):
    data.gameStatsButton.configure(state=NORMAL)
    data.helpButton.configure(state=DISABLED)
    data.returnToGameButton.configure(state=NORMAL)
    
    # Pauses the game
    if not data.paused: data.pauseButton.invoke()
    data.pauseButton.configure(state=DISABLED)
    
    data.startGameButton.configure(state=DISABLED)
    data.spawnEnemiesButton.configure(state=DISABLED)
    data.hFractalMapButton.configure(state=DISABLED)
    data.editingWallsButton.configure(state=DISABLED)
    data.wallWidthEntry.configure(state=DISABLED)
    data.wallHeightEntry.configure(state=DISABLED)
    data.clearWallsButton.configure(state=DISABLED)
    
    data.screen = data.HELP

def returnToGameButtonPressed(data):
    data.returnToGameButton.configure(state=DISABLED)
    
    data.gameStatsButton.configure(state=NORMAL)
    data.helpButton.configure(state=NORMAL)
    data.pauseButton.configure(state=NORMAL)
    data.startGameButton.configure(state=NORMAL)
    
    if not data.gameStarted:
        # Unpause if the game hasn't started
        if data.paused: data.pauseButton.invoke()
        
        data.hFractalMapButton.configure(state=NORMAL)
        data.editingWallsButton.configure(state=NORMAL)
        data.wallWidthEntry.configure(state=NORMAL)
        data.wallHeightEntry.configure(state=NORMAL)
        data.clearWallsButton.configure(state=NORMAL)
    else:
        data.spawnEnemiesButton.configure(state=NORMAL)
    
    data.screen = data.GAME

def hFractalMapButtonPressed(data):
    for wall in data.walls:
        if not wall.fixed: wall.destroy(data)
    initHFractalMap(data)

def editingWallsButtonPressed(data):
    data.editingWalls = not data.editingWalls
    active = "On" if data.editingWalls else "Off"
    text = "Editing walls: %s" %(active)
    data.editingWallsButton.configure(text=text)

def clearWallsButtonPressed(data):
    for wall in data.walls: wall.destroy(data)

#
# Initialization
#

def initMenuPlayerDisplay(data):
    canvas = data.canvas
    menuLeft = data.canvasWidth - data.menuWidth + 10
    menuRight = data.canvasWidth - 10
    menuCenter = data.canvasWidth - data.menuWidth//2
    menuBottom = data.canvasHeight//2 - 20
    menuTop = 100
    
    data.HPDisplay = canvas.create_text(menuLeft, menuBottom, anchor=W, 
        font="Arial 12 bold", fill="green", 
        text="HP: %d/%d" %(data.player.HP, data.player.maxHP))
    
    data.moneyDisplay = canvas.create_text(menuCenter, menuBottom, anchor=W, 
        font="Arial 12 bold", fill="goldenrod", 
        text="Money: %d" %(data.player.money))
    
    buttonW, buttonH = 75, 50
    hMargin, vMargin = 5, 20
    
    def upgradeCooldownPressed(): upgradeCooldownButtonPressed(data)
    data.upgradeCooldownButton = Button(canvas, text="Reduce Cooldown", 
        wraplength=buttonW, bg="pale turquoise", command=upgradeCooldownPressed)
    canvas.create_window(menuLeft, menuTop, anchor=W, width=buttonW, 
        height=buttonH, window=data.upgradeCooldownButton)
    canvas.create_text(menuLeft, menuTop + buttonH - vMargin + 2, 
        text="(Cost: 10)", anchor=W)
    
    def upgradePowerPressed(): upgradePowerButtonPressed(data)
    data.upgradePowerButton = Button(canvas, text="Increase Power", 
        wraplength=buttonW, bg="light salmon", command=upgradePowerPressed)
    canvas.create_window(menuLeft + 1*buttonW + hMargin, menuTop, anchor=W, 
        width=buttonW, height=buttonH, window=data.upgradePowerButton)
    canvas.create_text(menuLeft + 1*buttonW + hMargin, 
        menuTop + buttonH - vMargin + 2, text="(Cost: 5)", anchor=W)
    
    def upgradeBulletsPressed(): upgradeBulletsButtonPressed(data)
    data.upgradeBulletsButton = Button(canvas, text="Increase Bullets", 
        wraplength=buttonW, bg="pale green", command=upgradeBulletsPressed)
    canvas.create_window(menuLeft + 2*(buttonW + hMargin), menuTop, anchor=W, 
        width=buttonW, height=buttonH, window=data.upgradeBulletsButton)
    canvas.create_text(menuLeft + 2*(buttonW + hMargin), 
        menuTop + buttonH - vMargin + 2, text="(Cost: 10)", anchor=W)
    
    def upgradeBulletSizePressed(): upgradeBulletSizeButtonPressed(data)
    data.upgradeBulletSizeButton = Button(canvas, text="Increase Bullet Size", 
        wraplength=buttonW, bg="wheat", command=upgradeBulletSizePressed)
    canvas.create_window(menuLeft + 0*(buttonW + hMargin), 
        menuTop + 1*(buttonH + vMargin), anchor=W, width=buttonW, 
        height=buttonH, window=data.upgradeBulletSizeButton)
    canvas.create_text(menuLeft + 0*(buttonW + hMargin), 
        menuTop + 2*buttonH + 2, text="(Cost: 5)", anchor=W)
    
    def upgradeBulletSpeedPressed(): upgradeBulletSpeedButtonPressed(data)
    data.upgradeBulletSpeedButton = Button(canvas, 
        text="Increase Bullet Speed", wraplength=buttonW, bg="wheat", 
        command=upgradeBulletSpeedPressed)
    canvas.create_window(menuLeft + 1*(buttonW + hMargin), 
        menuTop + 1*(buttonH + vMargin), anchor=W, width=buttonW, 
        height=buttonH, window=data.upgradeBulletSpeedButton)
    canvas.create_text(menuLeft + 1*(buttonW + hMargin), 
        menuTop + 2*buttonH + 2, text="(Cost: 5)", anchor=W)
    
    def upgradeBulletDurationPressed(): upgradeBulletDurationButtonPressed(data)
    data.upgradeBulletDurationButton = Button(canvas, 
        text="Increase Bullet Duration", wraplength=buttonW, bg="wheat", 
            command=upgradeBulletDurationPressed)
    canvas.create_window(menuLeft + 2*(buttonW + hMargin), 
        menuTop + 1*(buttonH + vMargin), anchor=W, width=buttonW, 
        height=buttonH, window=data.upgradeBulletDurationButton)
    canvas.create_text(menuLeft + 2*(buttonW + hMargin), 
        menuTop + 2*buttonH + 2, text="(Cost: 5)", anchor=W)

def initMenuOptions(data):
    canvas = data.canvas
    menuLeft = data.canvasWidth - data.menuWidth + 10
    menuRight = data.canvasWidth - 10
    menuCenter = data.canvasWidth - data.menuWidth//2
    menuBottom = data.canvasHeight - 20
    
    vertSpacing = 30
    
    def startGamePressed(): startGameButtonPressed(data)
    data.startGameButton = Button(data.canvas, text="Start Game", 
        command=startGamePressed)
    canvas.create_window(menuLeft, menuBottom-6*vertSpacing, anchor=W, 
        window=data.startGameButton)
    
    def pausePressed(): pauseButtonPressed(data)
    data.pauseButton = Button(canvas, text="Pause", command=pausePressed)
    canvas.create_window(menuRight, menuBottom-6*vertSpacing, anchor=E, 
        window=data.pauseButton)
    
    def spawnEnemiesPressed(): spawnEnemiesButtonPressed(data)
    data.spawnEnemiesButton = Button(canvas, text="Spawn enemies", 
        command=spawnEnemiesPressed, state=DISABLED)
    canvas.create_window(menuLeft, menuBottom-5*vertSpacing, anchor=W, 
        window=data.spawnEnemiesButton)
    
    def gameStatsPressed(): gameStatsButtonPressed(data)
    data.gameStatsButton = Button(canvas, text="Stats", 
        command=gameStatsPressed)
    canvas.create_window(menuRight, menuBottom-5*vertSpacing, anchor=E, 
        window=data.gameStatsButton)
    
    def hFractalMapPressed(): hFractalMapButtonPressed(data)
    data.hFractalMapButton = Button(canvas, text="H Fractal Map", 
        command=hFractalMapPressed)
    canvas.create_window(menuLeft, menuBottom-2*vertSpacing, anchor=W, 
        window=data.hFractalMapButton)
    
    def editWallsPressed(): editingWallsButtonPressed(data)
    data.editingWallsButton = Button(canvas, text="Editing walls: Off", 
        command=editWallsPressed)
    canvas.create_window(menuLeft, menuBottom-3*vertSpacing, anchor=W, 
        window=data.editingWallsButton)
    
    def wallDimensionCheck(newText):
        if not newText.isnumeric(): return False
        num = int(newText)
        return num >= 7 and num <= 500
    
    def onInvalidWallDimensions(widgetID):
        widget = data.canvas.nametowidget(widgetID)
        widget.insert(0, "7")
        widget.delete(1, END)
    
    legalWallDimensions = canvas.register(wallDimensionCheck)
    fixWallDimensions = canvas.register(onInvalidWallDimensions)
    
    # Width entry
    data.wallWidthEntry = Entry(canvas, width=3, validate="focusout", 
        validatecommand=(legalWallDimensions, "%P"), 
        invalidcommand=(fixWallDimensions, "%W"), takefocus=0)
    data.wallWidthEntry.insert(0, "7") # Default value
    canvas.create_window(menuLeft+130, menuBottom-3*vertSpacing, anchor=W, 
        window=data.wallWidthEntry)
    canvas.create_text(menuLeft+130, menuBottom-3*vertSpacing, anchor=E, 
        text="W: ")
    
    # Height entry
    data.wallHeightEntry = Entry(canvas, width=3, validate="focusout", 
        validatecommand=(legalWallDimensions, "%P"), 
        invalidcommand=(fixWallDimensions, "%W"), takefocus=0)
    data.wallHeightEntry.insert(0, "7") # Default value
    canvas.create_window(menuLeft+180, menuBottom-3*vertSpacing, anchor=W, 
        window=data.wallHeightEntry)
    canvas.create_text(menuLeft+180, menuBottom-3*vertSpacing, anchor=E, 
        text="H: ")
    
    def clearWallsPressed(): clearWallsButtonPressed(data)
    data.clearWallsButton = Button(canvas, text="Clear walls", 
        command = clearWallsPressed)
    canvas.create_window(menuLeft, menuBottom-1*vertSpacing, anchor=W, 
        window=data.clearWallsButton)
    
    def helpPressed(): helpButtonPressed(data)
    data.helpButton = Button(canvas, text="Help", command=helpPressed)
    canvas.create_window(menuRight-50, menuBottom, anchor=E, 
                         window=data.helpButton)
    
    def returnToGamePressed(): returnToGameButtonPressed(data)
    data.returnToGameButton = Button(canvas, text="Return to game", 
        command=returnToGamePressed, state=DISABLED)
    canvas.create_window(menuLeft, menuBottom, anchor=W, 
                         window=data.returnToGameButton)

def initGameWorld(data):
    data.canvas.create_rectangle(0, 0, data.canvasWidth-data.menuWidth, 
        data.canvasHeight, fill="SlateGray2")
    
    data.enemiesKilled = 0
    data.level = 0
    data.exp = 0
    data.expToProgress = 50
    data.spawnInterval = 10.0
    
    data.terrainTypes = {Wall, Explosion}
    data.enemyTypes = {Explosive, Zombie}
    
    data.lifeforms = set()
    data.enemies = set()
    data.terrain = set()
    data.walls = set()
    data.waypoints = set()
    data.deadSprites = set()
    
    # Starts player in the center
    data.player=Player(data, Vector2((data.canvasWidth-data.menuWidth)//2, 20))
    
    menuWidth = data.menuWidth
    
    # Form a box around the playing area
    Wall(data, Vector2((data.canvasWidth-menuWidth)//2, 0), 
        data.canvasWidth-menuWidth, 10, fixed=True)
    Wall(data, Vector2((data.canvasWidth-menuWidth)//2, data.canvasHeight), 
        data.canvasWidth-menuWidth, 10, fixed=True)
    Wall(data, Vector2(0, data.canvasHeight//2), 10, data.canvasHeight, 
        fixed=True)
    Wall(data, Vector2(data.canvasWidth-menuWidth, data.canvasHeight//2), 10, 
        data.canvasHeight, fixed=True)
    
def initClassAttributes():
    initVector2Attributes()
    initPlayerAttributes()
    initExplosiveAttributes()
    initZombieAttributes()
    initWallAttributes()
    initExplosionAttributes()

def initVector2Attributes():
    Vector2.NORTH = Vector2( 0,  1)
    Vector2.SOUTH = Vector2( 0, -1)
    Vector2.WEST  = Vector2(-1,  0)
    Vector2.EAST  = Vector2( 1,  0)

#
# Lifeform stats
#

def initPlayerAttributes():
    Player.radius = 10
    Player.width = Player.height = 2*Player.radius
    Player.tag = "player"
    Player.color = "light sea green"
    
    # Made with reference to:
    # http://www.shutterstock.com/blog/10-images-brought-to-you-by-pixel-art
    Player.image = PhotoImage(file="Images/Player.png")
    
    Player.cooldownLength = 1000 # milliseconds
    Player.maxHP = 3000
    Player.hpRegen = 10 # per second
    Player.strength = 20
    Player.defence = 5
    Player.maxSpeed = 200 # pixels per second
    Player.maxTurnSpeed = math.radians(360) # radians per second

def initExplosiveAttributes():
    Explosive.width = 20
    Explosive.height = 50
    Explosive.tag = "explosive"
    Explosive.color = "firebrick"
    
    # Duplicated from Scribblenauts
    # http://scribblenauts.wikia.com/wiki/Dynamite
    Explosive.image = PhotoImage(file="Images/Dynamite.png")
    
    Explosive.waypointGraph = None
    Explosive.optimumEndpoints = dict()
    Explosive.paths = dict()
    
    Explosive.cooldownLength = 1 # milliseconds    Dies immediately
    Explosive.maxHP = 100
    Explosive.hpRegen = 0 # per second
    Explosive.strength = 100
    Explosive.defence = 0
    Explosive.maxSpeed = 40 # pixels per second
    Explosive.maxTurnSpeed = math.radians(360) # radians per second
    Explosive.value = 5

def initZombieAttributes():
    Zombie.radius = 9
    Zombie.width = Zombie.height = 2*Zombie.radius
    Zombie.tag = "zombie"
    Zombie.color = "chartreuse3"
    
    # Made with reference to:
    # http://www.shutterstock.com/blog/10-images-brought-to-you-by-pixel-art
    Zombie.image = PhotoImage(file="Images/Zombie.png")
    
    Zombie.waypointGraph = None
    Zombie.optimumEndpoints = dict()
    Zombie.paths = dict()
    
    Zombie.cooldownLength = 500 # milliseconds
    Zombie.maxHP = 1000
    Zombie.hpRegen = 66 # per second
    Zombie.strength = 10
    Zombie.defence = 5
    Zombie.maxSpeed = 150 # pixels per second
    Zombie.maxTurnSpeed = math.radians(720) # radians per second
    Zombie.value = 15
    
#
# Terrain stats
#

def initWallAttributes():
    Wall.thickness = 10
    Wall.tag = "wall"
    Wall.color = "black"

def initExplosionAttributes():
    Explosion.tag = "explosion"
    Explosion.color = "red"
    
    Explosion.radius = 50

#
# Draw functions
#

def redrawHelpScreen(data):
    canvas = data.canvas
    m = 10
    
    # Draw background
    right, bot = data.canvasWidth-data.menuWidth-m, data.canvasHeight-m
    canvas.create_rectangle(m, m, right, bot, fill="AntiqueWhite1", 
        tag="redraw")
    
    # Draw title
    title = "Help"
    xc, yc = (data.canvasWidth-data.menuWidth)//2, 50
    canvas.create_text(xc, yc, text=title, font="Arial 20 bold", tag="redraw")
    
    # Draw instructions
    file = open("Help/Instructions.txt")
    text = file.read()
    file.close()
    canvas.create_text(20, yc+20, anchor=NW, text=text, font="Arial 10", 
                       width=data.canvasWidth-data.menuWidth-40, tag="redraw")

def redrawStatsScreen(data):
    canvas = data.canvas
    m = 10
    
    # Draw background
    right, bot = data.canvasWidth-data.menuWidth-m, data.canvasHeight-m
    canvas.create_rectangle(m, m, right, bot, fill="AntiqueWhite1", 
        tag="redraw")
    
    # Draw title
    title = "Game Stats"
    xc, yc = (data.canvasWidth-data.menuWidth)//2, 50
    canvas.create_text(xc, yc, text=title, font="Arial 20 bold", tag="redraw")
    
    # Draw stats
    weapon = data.player.weapon
    vertSpacing = 40
    top = yc+20
    
    canvas.create_text(20, top, font="Arial 12", tag="redraw", 
        anchor=NW, text="Level: %d" %(data.level+1))
    
    canvas.create_text(20, top+1*vertSpacing, font="Arial 12", tag="redraw", 
        anchor=NW, 
        text="EXP to next level: %d" %(max(0, data.expToProgress-data.exp)))
    
    canvas.create_text(20, top+2*vertSpacing, font="Arial 12", tag="redraw", 
        anchor=NW, 
        text="Average enemy spawn time: %.1f seconds" %(data.spawnInterval))
    
    canvas.create_text(20, top+3*vertSpacing, font="Arial 12", tag="redraw", 
        anchor=NW, text="Enemies killed: %d" %(data.enemiesKilled))
    
    canvas.create_text(20, top+4*vertSpacing, font="Arial 12", tag="redraw", 
        anchor=NW, text="Weapon cooldown: %d milliseconds" %(weapon.cooldown))
    
    canvas.create_text(20, top+5*vertSpacing, font="Arial 12", tag="redraw", 
        anchor=NW, text="Weapon power: %d" %(weapon.power))
    
    canvas.create_text(20, top+6*vertSpacing, font="Arial 12", tag="redraw", 
        anchor=NW, text="Weapon bullets: %.1f" %(weapon.bullets))
    
    canvas.create_text(20, top+7*vertSpacing, font="Arial 12", tag="redraw", 
        anchor=NW, text="Bullet radius: %d pixels" %(weapon.bulletSize))
    
    canvas.create_text(20, top+8*vertSpacing, font="Arial 12", tag="redraw", 
        anchor=NW, 
        text="Bullet speed: %d pixels per second" %(weapon.bulletSpeed))
    
    canvas.create_text(20, top+9*vertSpacing, font="Arial 12", tag="redraw", 
        anchor=NW, 
        text="Bullet duration: %d milliseconds" %(weapon.bulletDuration))

def drawMenu(data):
    canvas = data.canvas
    menuCenter = data.canvasWidth - data.menuWidth//2
    menuLeft = data.canvasWidth - data.menuWidth + 10
    
    # Background
    canvas.create_rectangle(data.canvasWidth-data.menuWidth, 0, 
        data.canvasWidth, data.canvasHeight, fill="honeydew2")
    
    # Title
    canvas.create_text(menuCenter, 20, text="Menu", font="Arial 32 bold")
    
    # Subtitle: Weapon Upgrades
    canvas.create_text(menuLeft, 50, anchor=NW, text="Weapon Upgrades:", 
        font="Arial 10 bold")
    
    # Subtitle: Options
    canvas.create_text(menuLeft, data.canvasHeight//2 + 20, anchor=W, 
        text="Options:", font="Arial 10 bold")
    
    # Divider line
    canvas.create_line(data.canvasWidth-data.menuWidth, data.canvasHeight//2, 
                       data.canvasWidth, data.canvasHeight//2)
    
    # Click coords
    data.clickCoords = data.canvas.create_text(data.canvasWidth-10, 
                           data.canvasHeight-10, anchor=SE, text="0, 0")
    
####################
# MVC
####################

def init(data):
    data.canvas.focus_set()
    
    image = PhotoImage(file="Images/Dynamite.png")
    data.dynamite = data.canvas.create_image(500, 250, image=image)
    
    data.rowHeight, data.colWidth = 10, 10
    data.rows = data.canvasHeight//data.rowHeight
    data.cols = data.canvasWidth//data.colWidth
    
    data.timerDelay = 10 # milliseconds
    data.timerFiredsPerSecond = 1000//data.timerDelay
    
    data.HELP = 1
    data.GAME = 2
    data.STATS = 3
    data.screen = data.GAME
    
    data.gameOver = False
    data.gameStarted = False
    data.paused = False
    data.editingWalls = False
    
    data.debugging = False
    data.debuggingType = Explosive
    
    data.menuWidth = 250
    
    initClassAttributes()
    initGameWorld(data)
    
    drawMenu(data)
    initMenuOptions(data)
    initMenuPlayerDisplay(data)
    
    # Start with the help screen open
    data.helpButton.invoke()

def leftMousePressed(event, data):
    # Doesn't do anything if you're clicking a non-canvas widget
    if (not isinstance(event.widget, Entry) and 
        data.canvas.focus_get() != data.canvas):
        data.canvas.focus_set()
        return
    elif not event.widget is data.canvas: return
    
    if data.paused:
        data.canvas.itemconfigure(data.clickCoords,
                                  text = "%d, %d" %(event.x, event.y))
    
    if data.screen == data.GAME and event.x < data.canvasWidth-data.menuWidth:
        if data.editingWalls:
            placeWall(data, Vector2(event.x, event.y), 
                int(data.wallWidthEntry.get()), int(data.wallHeightEntry.get()))
        elif not data.paused:
            data.player.onLeftMousePressed(data, event.x, event.y)

def rightMousePressed(event, data):
    if data.editingWalls:
        removeWall(data, Vector2(event.x, event.y))

def leftMouseReleased(event, data):
    data.player.onLeftMouseReleased(data, event.x, event.y)

def keyPressed(event, data):
    if not data.canvas.focus_get() is data.canvas: return
    
    if event.keysym == "Escape":
        data.returnToGameButton.invoke()
    
    if data.screen == data.GAME:
        data.player.onKeyPressed(data, event.keysym)
        
        if event.keysym == "space":
            data.pauseButton.invoke()
        
        elif event.keysym == "d" and not data.gameOver:
            data.debugging = not data.debugging
        
        # elif event.keysym == "t":
        #     data.paused = not data.paused
        #     timerFired(data)
        #     data.paused = not data.paused
        
        elif event.keysym == "e":
            data.spawnEnemiesButton.invoke()

def keyReleased(event, data):
    data.player.onKeyReleased(data, event.keysym)

def timerFired(data):
    data.canvas.itemconfigure(data.HPDisplay, 
        text="HP: %d/%d" %(data.player.HP, data.player.maxHP))
    data.canvas.itemconfigure(data.moneyDisplay, 
        text="Money: %d" %(data.player.money))
    if data.screen == data.GAME:
        if not data.paused:
            updateLevel(data)
            if (returnsTrueOncePerNSeconds(data, data.spawnInterval) or 
                len(data.enemies) == 0):
                data.spawnEnemiesButton.invoke()
            
            for group in [data.terrain, data.lifeforms, data.waypoints]:
                for member in group:
                    if not data.paused:
                        member.onTimerFired(data)
            
            for corpse in data.deadSprites:
                for group in [data.terrain, data.lifeforms, data.waypoints, 
                              data.enemies, data.walls]:
                    group.discard(corpse)
        
            data.deadSprites.clear()
            
            if data.gameOver:
                data.debugging = True
                x = data.canvas.winfo_pointerx() - data.canvas.winfo_rootx()
                y = data.canvas.winfo_pointery() - data.canvas.winfo_rooty()
                if (0 <= x <= data.canvasWidth-data.menuWidth and 
                    0 <= y <= data.canvasHeight):
                    data.player.position = Vector2(x, y)

def redrawScreen(data):
    data.canvas.delete("redraw")
    if data.gameOver:
        data.canvas.create_text((data.canvasWidth-data.menuWidth)//2, 
            data.canvasHeight//2, font="Arial 32 bold", fill="white", anchor=S, 
            tag="redraw", text="Game Over")
        data.canvas.create_text((data.canvasWidth-data.menuWidth)//2, 
            data.canvasHeight//2, font="Arial 16 bold", fill="white", anchor=N, 
            tag="redraw", text="Click the \"Reset game\" button to restart.")
    if data.screen == data.HELP:
        redrawHelpScreen(data)
    elif data.screen == data.STATS:
        redrawStatsScreen(data)

####################
# Run game
####################

# Duplicated and modified from: 
# http://www.cs.cmu.edu/~112/notes/events-example0.py
def runGame():
    def leftMousePressedWrapper(event, data):
        leftMousePressed(event, data)
        data.canvas.update()
    
    def rightMousePressedWrapper(event, data):
        rightMousePressed(event, data)
        data.canvas.update()

    def leftMouseReleasedWrapper(event, data):
        leftMouseReleased(event, data)
        data.canvas.update()

    def keyPressedWrapper(event, data):
        keyPressed(event, data)
        data.canvas.update()
    
    def keyReleasedWrapper(event, data):
        keyReleased(event, data)
        data.canvas.update()

    def timerFiredWrapper(data):
        timerFired(data)
        redrawScreen(data)
        data.canvas.update()
        # Pause, then call timerFired again
        data.canvas.after(data.timerDelay, timerFiredWrapper, data)
    
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.canvasWidth = 1000
    data.canvasHeight = 500
    
    # Create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.canvasWidth, height=data.canvasHeight, 
        highlightthickness=0)
    canvas.pack()
    data.canvas = canvas
    
    init(data)
    
    # Set up events
    root.bind("<Button-1>", lambda event:
                            leftMousePressedWrapper(event, data))
    root.bind("<ButtonRelease-1>", lambda event:
                            leftMouseReleasedWrapper(event, data))
    root.bind("<Button-3>", lambda event:
                            rightMousePressedWrapper(event, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, data))
    root.bind("<KeyRelease>", lambda event:
                            keyReleasedWrapper(event, data))
    timerFiredWrapper(data)
    
    # Launch the app
    root.mainloop()

####################
# Miscellaneous
####################

# pygraph is for the weak! >:o
class Graph(object):
    def __init__(self, weightFunc=lambda v1, v2: 1):
        self.vertices = set()
        self.edges = dict()
        self.weightFunc = weightFunc
        self.memoizedPaths = dict()
    
    def addVertex(self, v, overwrite=False):
        if overwrite or not v in self.vertices: self.edges[v] = dict()
        
        self.vertices.add(v)
    
    # Creates an edge between 2 vertices, adding them to the graph if they 
    # aren't already in it.
    def addEdge(self, v1, v2, weight=1, oneWay=False):
        self.addVertex(v1)
        self.addVertex(v2)
        self.createEdge(v1, v2, weight, oneWay)
    
    # Creates an edge between 2 vertices.  Raises an exception if either 
    # vertex is not already in the graph.
    def createEdge(self, v1, v2, weight=None, oneWay=False):
        if v1 and v2 in self.vertices:
            self.edges[v1][v2] = weight
            if not oneWay: self.edges[(v2, v1)] = weight
        else:
            raise Exception("Vertices not in graph")
    
    # Connect a vertex to all vertices that cause filterFunc to return True.
    # Default argument connect the vertex to every other vertex
    def connectVertex(self, v, filterFunc=lambda v1, v2: True):
        for other in self.vertices:
            if filterFunc(v, other):
                weight = self.weightFunc(v, other)
                self.createEdge(v, other, weight, oneWay=True)
    
    # Connects all vertex pairs to each other if they satisfy filterFunc.
    # Default argument creates edges between all vertices.
    def connectAll(self, filterFunc=lambda v1, v2: True):
        for v in self.vertices:
            self.connectVertex(v, filterFunc)
    
    # Depth-first search using a heuristic
    def estimateLeastWeightedPath(self, start, end):
        if start == end: return [start]
        if end in self.edges[start]: return [start, end]
        
        # Check for a memoized path
        if (start, end) in self.memoizedPaths:
            return self.memoizedPaths[(start, end)]
        
        # print(start, end)
        
        path = []
        newEnd = end
        checked = {end}
        
        # New end is closest point to start that can reach original end.  
        # Repeats until start can reach end.
        while not end in self.edges[start]:
            
            # Couldn't find a path, so we backtrack.
            if newEnd == None:
                if path != []:
                    checked.add(path.pop(0))
                    end = path[0]
                
                # There is no path D:
                else:
                    # print("Line 1703: D:")
                    break
            else:
                path.insert(0, newEnd)
                checked.add(newEnd)
                end = newEnd
            
            newEnd = self.estimateBestWaypoint(end, start, checked)
        
        if path == []:
            self.memoizedPaths[(start, end)] = []
            return path
        
        path.insert(0, start)
        
        # print("Untrimmed: ", path)
        path = self.trimPath(path)
        # print("Trimmed: ", path)
        
        self.memoizePath(path)
        
        return path
    
    def estimateBestWaypoint(self, start, end, checked):
        bestDistance = None
        bestNeighbor = None
        
        try:
            for neighbor in self.edges[start]:
                if neighbor in checked: continue
                
                # A neighbor that can reach end directly is preferable to one 
                # that is closer to end but cannot reach it directly.
                if (bestNeighbor in self.edges[end] and 
                    not neighbor in self.edges[end]): continue
                
                travelDistance = self.edges[start][neighbor]
                estimatedRemainingDistance = neighbor.distanceTo(end)
                
                distance = travelDistance+estimatedRemainingDistance
                if bestDistance == None or distance < bestDistance:
                    bestDistance = distance
                    bestNeighbor = neighbor
            
            return bestNeighbor
        except:
            print(start, start in self.edges)
            raise Exception("start is None")
    
    def memoizePath(self, path):
        # Can't memoize every subpath of a long path without serious lag and 
        # potentially a memory error
        if len(path) >= 10:
            # Forwards
            key = (path[0], path[len(path)-1])
            self.memoizedPaths[key] = path
            
            # Backwards
            reverseKey = (key[1], key[0])
            self.memoizedPaths[reverseKey] = list(reversed(path))
        else:
            for subpath in powerset(path):
                length = len(subpath)
                if length >= 2:
                    # Again, forwards and backwards
                    key = (path[0], path[length-1])
                    self.memoizedPaths[key] = subpath
                    
                    reverseKey = (key[1], key[0])
                    self.memoizedPaths[reverseKey] = list(reversed(subpath))
    
    def trimPath(self, path):
        if len(path) < 2: return path
        
        trimmingComplete = True
        start, end = path[0], path[len(path)-1]
        
        temp = [end]
        end = []  # So we don't duplicate end if there's nothing to trim
        for i in range(len(path)-1):
            if path[i] in self.edges[path[len(path)-1]]:
                path = path[:i+1]
                trimmingComplete = False
                end = temp
                break
        
        temp = [start]
        start = []    # So we don't duplicate start if there's nothing to trim
        for i in range(len(path)-1, 0, -1):
            if path[i] in self.edges[path[0]]:
                path = path[i:]
                trimmingComplete = False
                start = temp
                break
        
        # Add start and end back since they were truncated.
        if trimmingComplete: return start + path + end
        else: return start + self.trimPath(path) + end

# Inspired by the vector objects from ROBLOX
# Contains some unused methods from earlier versions of the project.
class Vector2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # Vector addition
    def __add__(self, vector):
        return Vector2(self.x+vector.x, self.y+vector.y)
    
    # Vector subtraction
    def __sub__(self, vector):
        return Vector2(self.x-vector.x, self.y-vector.y)
    
    # Scalar multiplication
    def __mul__(self, scalar):
        return Vector2(self.x*scalar, self.y*scalar)
    def __rmul__(self, scalar):
        return Vector2(self.x*scalar, self.y*scalar)
    
    def __eq__(self, other):
        return isinstance(other, Vector2) and self.coords() == other.coords()
    
    def __repr__(self):
        return "<%d, %d>" %(self.coords())
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def copy(self):
        return Vector2(self.x, self.y)
    
    def coords(self):
        return (self.x, self.y)
    
    def magnitude(self):
        return (self.x**2 + self.y**2)**0.5
    
    def distanceTo(self, vector):
        return (self - vector).magnitude()
    
    def unit(self):
        magnitude = self.magnitude()
        if almostEqual(magnitude, 0): return self       # Uh oh...
        xUnit = self.x/magnitude
        yUnit = self.y/magnitude
        return Vector2(xUnit, yUnit)
    
    def crossProduct(self, vector):
        return self.x*vector.y - self.y*vector.x
    
    def dotProduct(self, vector):
        return self.x*vector.x + self.y*vector.y
    
    def getNormal(self):
        return Vector2(-1*self.y, self.x)
    
    def angleBetween(self, vector):
        unitSelf = self.unit()
        unitVector = vector.unit()
        
        # This can be greater than 1 under certain conditions due to silly 
        # Python floats, hence the check
        acosArgument = unitSelf.dotProduct(unitVector)
        if acosArgument > 1: acosArgument = 1
        elif acosArgument < -1: acosArgument = -1
        
        # Cross product indicates whether 'vector' is below or above 'self'.
        # Angle's sign is negative for the former, positive for the latter.
        if self.crossProduct(vector) < 0:
            return -1*math.acos(acosArgument)
        else:
            return math.acos(acosArgument)
    
    def rotate(self, pivot, amount, ccw=True):
        startAngle = self.angleBetween(Vector2(1, 0))
        endAngle = startAngle + amount if ccw else startAngle - amount
        
        xPivot, yPivot = pivot.coords()
        endX = xPivot + math.cos(endAngle)
        endY = yPivot - math.sin(endAngle)
        
        self.x, self.y = endX-xPivot, endY-yPivot
    
    def isPerpendicular(self, vector):
        return almostEqual(abs(self.angleBetween(vector)), math.pi/2)
    
    def isParallel(self, vector):
        return almostEqual(self.angleBetween(vector), 0)
    
    # Formula from Multivariable Calculus
    def scalarProjection(self, vector):
        return self.dotProduct(vector)/vector.magnitude()
    
    # Formula from Multivariable Calculus
    def vectorProjection(self, vector):
        return self.scalarProjection(vector) * vector.unit()
    
    def compassDirection(self):
        north = Vector2.NORTH
        south = Vector2.SOUTH
        west  = Vector2.WEST
        east  = Vector2.EAST
        angleBoundary = math.radians(45)
        
        if   abs(self.angleBetween(north)) <= angleBoundary: return "N"
        elif abs(self.angleBetween(south)) <= angleBoundary: return "S"
        elif abs(self.angleBetween(west )) <= angleBoundary: return "W"
        elif abs(self.angleBetween(east )) <= angleBoundary: return "E"
        else: return None # Only happens if angleBoundary < math.radians(45)

# Duplicated from lab9 and slightly modified
class Line(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.slope = (None if end.x == start.x
                           else (end.y - start.y)/(end.x - start.x))
        self.slopeVector = (self.end - self.start).unit()
        self.yIntercept = (None if self.slope == None
                                else start.y - self.slope*start.x)
    
    def __eq__(self, line):
        return str(self) == str(line)
    
    def __hash__(self):
        return hash((self.start, self.end, self.slope, self.yIntercept))
    
    def __repr__(self):
        slope = self.slope
        yIntercept = self.yIntercept
        
        if self.slope == None: return "x=%d" %(self.start.x)
        
        part1 = "y="
        
        if slope == None: part2 = ""
        elif slope == -1: part2 = "-x"
        elif slope == 1: part2 = "x"
        elif slope == 0: part2 = ""
        else: part2 = "%dx" %(slope)
        
        if yIntercept == None: part3 = ""
        elif yIntercept == 0: part3 = ""
        elif yIntercept > 0:
            if slope != 0: part3 = "+%d" %(yIntercept)
            else: part3 = "%d" %(yIntercept)
        else: part3 = "%d" %(yIntercept)
        
        result = part1+part2+part3
        if result == "y=": result = "y=0"
        return result
    
    def getIntersection(self, line):
        selfSlope, lineSlope = self.slope, line.slope
        selfIntercept, lineIntercept = self.yIntercept, line.yIntercept
        
        if selfSlope == lineSlope: return None
        elif selfSlope == None: x = self.start.x
        elif lineSlope == None: x = line.start.x
        else: x = (lineIntercept - selfIntercept)/(selfSlope - lineSlope)
        
        if selfSlope != None: y = x*selfSlope + selfIntercept
        else: y = x*lineSlope + lineIntercept
        return Vector2(x, y)
    
    def isParallelTo(self, line):
        return self.getIntersection(line) == None
    
    def getHorizontalLine(self, xIntersection):
        # Vertical line going through xIntersection
        vertLineStart = Vector2(xIntersection, 0)
        vertLineEnd = Vector2(xIntersection, 1)
        vertLine = Line(vertLineStart, vertLineEnd)
        
        # We want the y value of where Self intersects the vertical line
        yIntersection = self.getIntersection(vertLine).y
        
        # We return a horizontal line crossing Self at the xIntersection
        lineStart = Vector2(xIntersection, yIntersection)
        lineEnd = Vector2(xIntersection+1, yIntersection)
        return Line(lineStart, lineEnd)
    
    def getVerticalLine(self, yIntersection):
        # Horizontal line going through yIntersection
        horizontalLineStart = Vector2(0, yIntersection)
        horizontalLineEnd = Vector2(1, yIntersection)
        horizontalLine = Line(horizontalLineStart, horizontalLineEnd)
        
        # We want the x value of where Self intersects the horizontal line
        xIntersection = self.getIntersection(horizontalLine).x
        
        # We return a vertical line crossing Self at the yIntersection
        lineStart = Vector2(xIntersection, yIntersection)
        lineEnd = Vector2(xIntersection, yIntersection+1)
        return Line(lineStart, lineEnd)

runGame()