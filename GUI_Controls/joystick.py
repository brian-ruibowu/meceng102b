import pygame
import time

class Joystick:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Initialize the joystick module
        pygame.joystick.init()

        # Check for available joysticks
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            raise RuntimeError("No joysticks found.")

        # Initialize the first joystick
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print("Initialized joystick:", self.joystick.get_name())

    def get_values(self):

        pygame.event.get()

        # Get the state of all the joystick's buttons
        buttons = [self.joystick.get_button(i) for i in range(4)]

        # Get the state of all the joystick's hats
        hats = [self.joystick.get_hat(i) for i in range(self.joystick.get_numhats())]

        return {'buttons': buttons, 'hats': hats}

    def close(self):
        # Clean up
        self.joystick.quit()
        pygame.quit()