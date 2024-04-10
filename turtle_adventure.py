"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import math
import random
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.

class RandomWalkEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.op = []

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill="red")

    def update(self) -> None:
        operators = ['+', '-']
        random_x_operator = random.choice(operators)
        random_y_operator = random.choice(operators)
        if len(self.op) == 0:
            self.op.append(random_x_operator)
            self.op.append(random_y_operator)

        # Apply operators to x and y
        if self.op[0] == '+':
            self.x += 1
        elif self.op[0] == '-':
            self.x -= 1

        if self.op[1] == '+':
            self.y += 1
        elif self.op[1] == '-':
            self.y -= 1

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        pass


class ChasingEnemy(Enemy):

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.speed = random.randint(2,3)

    def create(self) -> None:
        self.__id = self.canvas.create_oval(
            0, 0, self.size/2, self.size/2, fill=self.color)

    def update(self) -> None:

        x_cor = self.game.player.x
        y_cor = self.game.player.y

        dx, dy = x_cor - self.x, y_cor - self.y
        dist = math.hypot(dx, dy)
        dx, dy = dx / dist, dy / dist

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Check out of bound
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.size:
            self.x = SCREEN_WIDTH - self.size
        if self.y < 0:
            self.y = 0
        elif self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size

        if ( (self.x < self.game.player.x < self.x + self.size) and
             (self.y < self.game.player.y < self.y + self.size) ):
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x,
                           self.y,
                           self.x+self.size,
                           self.y+self.size)

    def delete(self):
        self.canvas.delete(self.__id)


# FENCING BOUND (660, 210) -> (720, 210) -> (720, 270) -> (660,270)
class FencingEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,):
        super().__init__(game, size, color)
        self.speed = 5
        self.spawnOpt = None

    def create(self) -> None:
        self.__id = self.canvas.create_oval(
            0, 0, self.size/2, self.size/2, fill=self.color)
        if self.spawnOpt == 1:
            self.x, self.y = 660, 210
        elif self.spawnOpt == 0:
            self.x, self.y = 720, 270
        elif self.spawnOpt == 2:
            self.x, self.y = 720, 210
        elif self.spawnOpt == 3:
            self.x, self.y = 660, 270

    def update(self) -> None:
            if self.spawnOpt == 1:
                if self.y == 210:
                    if self.x < 720:
                        self.x += self.speed
                if self.x == 720:
                    if self.y < 270:
                        self.y += self.speed
                if self.y == 270:
                    if self.x > 660:
                        self.x -= self.speed
                if self.x == 660:
                     if self.y > 210:
                         self.y -= self.speed

            elif self.spawnOpt == 0:
                if self.y == 270:
                    if self.x > 660:
                        self.x -= self.speed
                if self.x == 660:
                     if self.y > 210:
                         self.y -= self.speed
                if self.y == 210:
                    if self.x < 720:
                        self.x += self.speed
                if self.x == 720:
                    if self.y < 270:
                        self.y += self.speed

            elif self.spawnOpt == 2:
                if self.x == 720:
                    if self.y < 270:
                        self.y += self.speed
                if self.y == 270:
                    if self.x > 660:
                        self.x -= self.speed
                if self.x == 660:
                     if self.y > 210:
                         self.y -= self.speed
                if self.y == 210:
                    if self.x < 720:
                        self.x += self.speed

            elif self.spawnOpt == 3:
                if self.x == 660:
                     if self.y > 210:
                         self.y -= self.speed
                if self.y == 210:
                    if self.x < 720:
                        self.x += self.speed
                if self.x == 720:
                    if self.y < 270:
                        self.y += self.speed
                if self.y == 270:
                    if self.x > 660:
                        self.x -= self.speed

            if ( (self.x < self.game.player.x < self.x + self.size) and
                (self.y < self.game.player.y < self.y + self.size) ):
                self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x,
                           self.y,
                           self.x+self.size,
                           self.y+self.size)

    def delete(self):
        self.canvas.delete(self.__id)


class CentipedeEnemy(Enemy):
    def __init__(self, game: "TurtleAdventureGame", size: int,
                 color: str):
        super().__init__(game, size, color)
        self.speed = 4
        self.body_segments = []
        self.segment_spacing = 1 * self.size  # space between seg
        self.length = 10

    def create(self) -> None:
        # head
        self.body_segments.append(
            self.canvas.create_rectangle(
                self.x, self.y, self.x + self.size + 4, self.y + self.size + 4,
                fill=self.color, outline='black', width=2))

        # create body seg
        for i in range(1, self.length):
            x = self.x - i * self.segment_spacing
            y = self.y
            self.body_segments.append(
                self.canvas.create_rectangle(
                    x, y, x + self.size, y + self.size,
                    fill=self.color, outline='black', width=2))

    def update(self) -> None:
        x_cor = self.game.player.x
        y_cor = self.game.player.y

        dx, dy = x_cor - self.x, y_cor - self.y
        dist = math.hypot(dx, dy)
        dx, dy = dx / dist, dy / dist

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Move body
        for i in range(1, len(self.body_segments)):
            prev_segment = self.body_segments[i - 1]
            segment = self.body_segments[i]
            dx = self.canvas.coords(prev_segment)[0] - \
                 self.canvas.coords(segment)[0]
            dy = self.canvas.coords(prev_segment)[1] - \
                 self.canvas.coords(segment)[1]
            dist = math.hypot(dx, dy)
            if dist > self.segment_spacing:
                dx, dy = dx / dist, dy / dist
                segment_x, segment_y = self.canvas.coords(segment)[:2]
                segment_x += dx * (dist - self.segment_spacing)
                segment_y += dy * (dist - self.segment_spacing)
                self.canvas.coords(segment, segment_x, segment_y,
                                   segment_x + self.size,
                                   segment_y + self.size)

        # To sure that head will move to front
        self.canvas.coords(self.body_segments[0], self.x, self.y,
                           self.x + self.size, self.y + self.size)

        if ((self.x < self.game.player.x < self.x + self.size) and
                (self.y < self.game.player.y < self.y + self.size)):
            self.game.game_over_lose()

    def render(self) -> None:
        for segment in self.body_segments:
            self.canvas.coords(segment,
                               self.canvas.coords(segment)[0],
                               self.canvas.coords(segment)[1],
                               self.canvas.coords(segment)[0] + self.size,
                               self.canvas.coords(segment)[1] + self.size)

    def delete(self) -> None:
        for segment in self.body_segments:
            self.canvas.delete(segment)


class ShootingEnemy(Enemy):
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str, ball_speed: int):
        super().__init__(game, size, color)
        self.ball_speed = ball_speed
        self.__ball = None
        self.last_shot_time = time.time()

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, self.size/2, self.size/2, fill=self.color)

    def update(self) -> None:
        # Shoot a ball towards the player's location if it's been at least 1 second since the last shot
        current_time = time.time()
        if current_time - self.last_shot_time >= 1:
            self.last_shot_time = current_time
            self.__shoot_ball()

        # Move the existing ball towards its destination
        if self.__ball is not None and self.__ball.isvisible():
            self.__ball.forward(self.ball_speed)

            # Check if the ball hits the player
            if self.__ball.distance(self.game.player.x, self.game.player.y) < self.size:
                self.game.game_over_lose()
                self.__ball.hideturtle()  # Hide the ball when the game is over

    def __shoot_ball(self) -> None:
        x_cor = self.game.player.x
        y_cor = self.game.player.y
        if self.__ball is not None:
            self.__ball.hideturtle()
        self.__ball = RawTurtle(self.canvas)
        self.__ball.penup()
        self.__ball.color('red')
        self.__ball.shape('circle')
        self.__ball.shapesize(0.5)
        self.__ball.goto(self.x, self.y)
        self.__ball.setheading(self.__ball.towards(x_cor, y_cor))

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x,
                           self.y,
                           self.x+self.size,
                           self.y+self.size)

    def delete(self):
        self.canvas.delete(self.__id)


# TODO
# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__game.after(100, self.create_fencing)
        self.__game.after(100, self.create_centipede)
        self.__game.after(100, self.create_randomWalkenemy)
        for i in range(5):
            self.__game.after(100, self.create_ShootingEnemy)
        for i in range(1000, 100000, 1000):
            self.__game.after(i, self.create_randomWalkenemy)
        for i in range(1000, 10000, 1000):
            self.__game.after(i, self.create_chasing)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_randomWalkenemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        new_enemy = RandomWalkEnemy(self.__game, 20, "blue")
        new_enemy.x = random.randint(0, 600)
        new_enemy.y = random.randint(0, 500)
        self.game.add_element(new_enemy)

    def create_chasing(self):
        new_enemy = ChasingEnemy(self.__game, 20, "green")
        new_enemy.x = random.randint(0, 600)
        new_enemy.y = random.randint(0, 500)
        self.__game.add_enemy(new_enemy)

    def create_fencing(self):
        for i in range(4):
            new_enemy = FencingEnemy(self.__game, 10, "red")
            new_enemy.spawnOpt = i
            self.__game.add_enemy(new_enemy)

    def create_centipede(self):
        new_enemy = CentipedeEnemy(self.__game, 10, 'yellow')
        new_enemy.x = random.randint(0, 600)
        new_enemy.y = random.randint(0, 500)
        self.__game.add_enemy(new_enemy)

    def create_ShootingEnemy(self):
        new_enemy = ShootingEnemy(self.__game, 10, 'brown', 10)
        new_enemy.x = random.randint(0, 600)
        new_enemy.y = random.randint(0, 500)
        self.__game.add_enemy(new_enemy)


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
