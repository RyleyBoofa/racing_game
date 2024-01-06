# IMPORTS
import pygame
import math, time
from utils import *

# FONTS
pygame.font.init()
MAIN_FONT = pygame.font.SysFont("comicsans", 44)
SECONDARY_FONT = pygame.font.SysFont("comicsans", 36)

# CONSTANTS
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 30

PATH = [
    (157, 140),
    (80, 101),
    (45, 236),
    (64, 471),
    (136, 572),
    (196, 637),
    (249, 692),
    (341, 702),
    (389, 648),
    (405, 531),
    (538, 475),
    (588, 584),
    (599, 690),
    (709, 689),
    (747, 523),
    (706, 407),
    (619, 332),
    (557, 346),
    (445, 360),
    (398, 275),
    (558, 251),
    (701, 238),
    (724, 140),
    (668, 83),
    (572, 46),
    (441, 45),
    (298, 88),
    (279, 192),
    (282, 274),
    (283, 328),
    (244, 389),
    (164, 363),
    (174, 258),
    (176, 235),
]


class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time, 1)


# CARS
class AbstractCar:
    def __init__(self, max_vel, rot_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rot_vel = rot_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rot_vel
        elif right:
            self.angle -= self.rot_vel

    def draw(self, window):
        blit_rotate_center(window, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        """Calculate and apply acceleration"""
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        """Calculate and apply deceleration/reversing"""
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        """Calculate move direction and move car"""
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        """Check for collisions between the car and the given mask"""
        car_mask = pygame.mask.from_surface(self.img)
        # Determine the offset between the car and the given mask
        offset = (int(self.x - x), int(self.y - y))
        # Generate a point of intersection at where the objects overlap
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

    def reduce_speed(self):
        """Calculate and apply deceleration"""
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        """Invert velocity to simulate bouncing off a wall"""
        self.vel = -self.vel
        self.move()

    def drive(self):
        """Read player inputs and apply movement to player_car"""

        # Store a list of all keys pressed this frame
        keys = pygame.key.get_pressed()

        # By default, moved this frame is False
        moved = False

        # Perform movement based on keys pressed this frame
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(left=True)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(right=True)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            moved = True
            self.move_forward()
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            moved = True
            self.move_backward()

        # If not moved this frame then decelerate car
        if not moved:
            self.reduce_speed()


class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rot_vel, path=[]):
        super().__init__(max_vel, rot_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_path(self, window):
        """Plot the computer_car's path using red dots"""
        for point in self.path:
            pygame.draw.circle(window, "red", point, 5)

    def draw(self, window):
        """Draw the computer car and it's path"""
        super().draw(window)
        if debug:
            self.draw_path(window)

    def calculate_angle(self):
        """Determine the angle to rotate computer_car to"""
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        # Ensure there won't be a 0 division error
        if y_diff == 0:
            # Convert 90deg to radians
            desired_radian_angle = math.pi / 2
        else:
            # Return angle between computer_car and current_point
            desired_radian_angle = math.atan(x_diff / y_diff)

        # Point towards correct angle when current_point is below computer_car
        if target_y > self.y:
            desired_radian_angle += math.pi

        # Use the difference_in_angle to determine optimal turn direction
        difference_in_angle = self.angle - math.degrees(desired_radian_angle)

        # If angle is greater than 180 then turning the wrong direction
        if difference_in_angle > 180:
            difference_in_angle -= 360

        # Rotate computer_car in desired direction
        if difference_in_angle > 0:
            self.angle -= min(self.rot_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rot_vel, abs(difference_in_angle))

    def update_path_point(self):
        """Set current_point to next in path once current_point is reached"""
        target = self.path[self.current_point]
        car_rect = pygame.Rect(
            self.x, self.y, self.img.get_width(), self.img.get_height()
        )
        if car_rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        """Angle and move the computer_car towards the next point in it's path"""

        # Ensure not trying to move to a point that doesn't exist
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0


# DRAWING
def draw(window, images, player_car, computer_car, game_info):
    """Handle all drawing to the screen"""
    for img, pos in images:
        window.blit(img, pos)

    level_text = SECONDARY_FONT.render(f"Level: {game_info.level}", 1, "white")
    window.blit(level_text, (10, HEIGHT - level_text.get_height() - 110))

    time_text = SECONDARY_FONT.render(
        f"Time: {game_info.get_level_time()}s", 1, "white"
    )
    window.blit(time_text, (10, HEIGHT - time_text.get_height() - 60))

    speed_text = SECONDARY_FONT.render(
        f"Speed: {round(player_car.vel * 10)}px/s", 1, "white"
    )
    window.blit(speed_text, (10, HEIGHT - speed_text.get_height() - 10))

    player_car.draw(window)
    computer_car.draw(window)

    pygame.display.update()


def handle_collisions():
    """Handle and respond to all collisions"""
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    # *FINISH_POSITION splits the tuple storing the coords into 2 seperate values
    # Handle computer_car collsions
    computer_finish_poi = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi != None:
        blit_text_center(WINDOW, MAIN_FONT, "You lost!")
        pygame.time.wait(3000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

    # Handle player_car collisions
    player_finish_poi = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi != None:
        # Collided with top of the finish line (ie: backwards)
        if player_finish_poi[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)


# GAME CONFIG
debug = True
running = True
clock = pygame.time.Clock()
images = [
    (GRASS, (0, 0)),
    (TRACK, (0, 0)),
    (FINISH, FINISH_POSITION),
    (TRACK_BORDER, (0, 0)),
]
player_car = PlayerCar(5, 5)
computer_car = ComputerCar(3, 4, PATH)
game_info = GameInfo()

# GAME LOOP
while running:
    clock.tick(FPS)

    draw(WINDOW, images, player_car, computer_car, game_info)

    while not game_info.started:
        blit_text_center(
            WINDOW, MAIN_FONT, f"Press any key to start level {game_info.level}!"
        )
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    player_car.drive()

    computer_car.move()

    handle_collisions()

    if game_info.game_finished():
        blit_text_center(WINDOW, MAIN_FONT, "You won the game!")
        pygame.time.wait(3000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

    if debug:
        print(clock.get_fps())


pygame.quit()
