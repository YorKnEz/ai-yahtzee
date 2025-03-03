import pygame

from constants import FPS
from utils import point_in_convex_polygon


class Die:

    def __init__(
        self,
        image: pygame.Surface,
        value: int,
        pos: tuple[float, float],
        size: int = 64,
    ):
        # pre-allocated state instances
        self.idle_state = IdleDie(self)
        self.pickable_state = PickableDie(self)
        self.picked_state = PickedDie(self)

        # state
        self.state: DieState = self.idle_state

        # common attributes
        self.image = image
        self.value = value
        self.size = size
        self.bounds = pygame.Rect(0, 0, size, size)
        self.bounds.center = (int(pos[0]), int(pos[1]))
        self.rotation = 0.0

        self.start_pos = self.bounds.center
        self.throw_pos = (0.0, 0.0, 0.0)
        self.poly_bounds = self.get_updated_poly_bounds()

    def get_updated_poly_bounds(self):
        """Returns an array of vertices representing the corners of the die."""
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = self.bounds.center
        pivot = pygame.math.Vector2(rect.center)

        poly = [
            (pygame.math.Vector2(rect.topleft) - pivot).rotate(-self.rotation) + pivot,
            (pygame.math.Vector2(rect.topright) - pivot).rotate(-self.rotation) + pivot,
            (pygame.math.Vector2(rect.bottomright) - pivot).rotate(-self.rotation)
            + pivot,
            (pygame.math.Vector2(rect.bottomleft) - pivot).rotate(-self.rotation)
            + pivot,
        ]

        return [(p.x, p.y) for p in poly]

    def update_image(self, rotation=0.0):
        # kind of inefficient, the alternative would be to have a variable that stores the original
        # loaded image and another that would represent the image to draw on-screen
        #
        # we'll see what MateI says

        self.rotation = rotation
        self.image = pygame.transform.scale(
            pygame.image.load(f"assets/dice/dice{self.value}.png").convert_alpha(),
            (self.size, self.size),
        )

        if rotation != 0.0:
            self.image = pygame.transform.rotate(self.image, rotation)

        self.bounds.width = self.image.get_width()
        self.bounds.height = self.image.get_height()

    def draw(self, screen):
        screen.blit(self.image, self.bounds.topleft)

    def throw(self, new_value: int, off_screen_pos, throw_pos, throw_bounds):
        self.state.throw(new_value, off_screen_pos, throw_pos, throw_bounds)

    def update(self, dt):
        self.state.update(dt)

    def click(self, pos):
        if point_in_convex_polygon(pos, self.poly_bounds):
            self.state.click()

    def pick(self):
        self.state.click()

    def reset(self, new_pos):
        self.state.reset(new_pos)

    def picked(self) -> bool:
        return self.state.picked()

    def in_animation(self) -> bool:
        return self.state.in_animation()


class DieState:

    def throw(self, new_value: int, off_screen_pos, throw_pos, throw_bounds):
        pass

    def update(self, dt):
        pass

    def click(self):
        pass

    def reset(self, new_pos):
        pass

    def picked(self) -> bool:
        return False

    def in_animation(self) -> bool:
        return False


class IdleDie(DieState):

    def __init__(self, parent: Die):
        self.parent = parent

    def throw(self, new_value: int, off_screen_pos, throw_pos, throw_bounds):
        self.parent.value = new_value
        self.parent.state = ThrownDieAnimation(
            self.parent, off_screen_pos, throw_pos, throw_bounds
        )


class ThrownDieAnimation(DieState):

    def __init__(
        self, parent: Die, off_screen_pos, throw_pos, throw_bounds: pygame.Rect
    ):
        self.parent = parent

        # the keyframes of the animation (a tuple of form (duration in seconds, duration in frames)):
        # - first item: off-screen animation
        # - second item: "die throw" animation
        self.keyframes = [(0.5, 0.5 * FPS), (0.3, 0.3 * FPS)]
        self.frame_count = 0
        self.curr_keyframe = 0

        self.off_screen_pos = off_screen_pos

        self.throw_bounds = throw_bounds
        self.throw_pos = throw_pos

        self.vector = (
            self.off_screen_pos[0] - self.parent.bounds.center[0],
            self.off_screen_pos[1] - self.parent.bounds.center[1],
        )

    def update(self, dt):
        """
        Performs the updates needed for one frame of the throw animation (i.e. moving the dice).
        """
        duration, total_frames = self.keyframes[self.curr_keyframe]

        if self.frame_count < total_frames:  # if current keyframe is still running
            self.parent.bounds.topleft = (
                self.parent.bounds.x + (self.vector[0] * dt / duration),
                self.parent.bounds.y + (self.vector[1] * dt / duration),
            )

            self.frame_count += 1
        else:  # if current keyframe ended, do different things depending on current keyframe
            throw_x, throw_y, rot = self.throw_pos

            if self.curr_keyframe == 0:
                # snap dice to their final position
                self.parent.bounds.center = self.off_screen_pos

                # prepare direction vectors for the dice throw
                self.vector = (
                    throw_x - self.parent.bounds.center[0],
                    throw_y - self.parent.bounds.center[1],
                )

                # reset frame_count and move to next keyframe
                self.frame_count = 0
                self.curr_keyframe += 1
            else:
                # update dice values
                # rotate the dice for a more realistic throw animation
                self.parent.update_image(rot)
                self.parent.throw_pos = self.throw_pos

                # snap dice to their final position
                self.parent.bounds.center = (throw_x, throw_y)

                # get the bounds of the rotated dice as a set of points of a polygon
                # this is used in determining if a die is clicked
                self.parent.poly_bounds = self.parent.get_updated_poly_bounds()

                # reset frame_count and curr_keyframe and stop the animation
                self.frame_count = 0
                self.curr_keyframe = 0

                # move to pickable state
                self.parent.state = self.parent.pickable_state

    def in_animation(self) -> bool:
        return True


class PickableDie(DieState):

    def __init__(self, parent: Die):
        self.parent = parent

    def throw(self, new_value: int, off_screen_pos, throw_pos, throw_bounds):
        self.parent.value = new_value
        self.parent.state = ThrownDieAnimation(
            self.parent, off_screen_pos, throw_pos, throw_bounds
        )

    def click(self):
        # move die to its start position
        self.parent.state = MovingDieAnimation(
            self.parent, self.parent.start_pos, 0.0, self.parent.picked_state
        )

    def reset(self, new_pos):
        self.parent.start_pos = new_pos
        # move die to its start position
        self.parent.state = MovingDieAnimation(
            self.parent, self.parent.start_pos, 0.0, self.parent.idle_state
        )


class MovingDieAnimation(DieState):

    def __init__(
        self,
        parent: Die,
        final_pos: tuple[int, int],
        rotation: float,
        final_state: DieState,
    ):
        self.parent = parent

        self.final_pos = final_pos
        self.rotation = rotation
        self.final_state = final_state

        # the keyframes of the animation (a tuple of form (duration in seconds, duration in frames)):
        # - first item: off-screen animation
        # - second item: "die throw" animation
        self.keyframes = [(0.5, 0.5 * FPS)]
        self.frame_count = 0
        self.curr_keyframe = 0

        self.vector = (
            self.final_pos[0] - self.parent.bounds.center[0],
            self.final_pos[1] - self.parent.bounds.center[1],
        )

    def update(self, dt):
        """
        Performs the updates needed for one frame of the pick animation (i.e. moving the dice).
        """
        duration, total_frames = self.keyframes[self.curr_keyframe]

        if self.frame_count < total_frames:  # if current keyframe is still running
            self.parent.bounds.topleft = (
                self.parent.bounds.x + (self.vector[0] * dt / duration),
                self.parent.bounds.y + (self.vector[1] * dt / duration),
            )

            self.frame_count += 1
        else:  # if current keyframe ended, do different things depending on current keyframe
            # update dice values
            # rotate the dice for a more realistic throw animation
            self.parent.update_image(self.rotation)

            # snap dice to their final position
            self.parent.bounds.center = self.final_pos

            # get the bounds of the rotated dice as a set of points of a polygon
            # this is used in determining if a die is clicked
            self.parent.poly_bounds = self.parent.get_updated_poly_bounds()

            # reset frame_count and curr_keyframe and stop the animation
            self.frame_count = 0

            # move to picked state
            self.parent.state = self.final_state

    def in_animation(self) -> bool:
        return True


class PickedDie(DieState):

    def __init__(self, parent: Die):
        self.parent = parent

    def click(self):
        # move to pickable state again
        x, y, rot = self.parent.throw_pos
        self.parent.state = MovingDieAnimation(
            self.parent, (int(x), int(y)), rot, self.parent.pickable_state
        )

    def reset(self, new_pos):
        self.parent.start_pos = new_pos
        # move die to its start position
        self.parent.state = MovingDieAnimation(
            self.parent, self.parent.start_pos, 0.0, self.parent.idle_state
        )

    def picked(self) -> bool:
        return True
