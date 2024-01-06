import math
from utils import *


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
