import pygame
import random

# defining colors for later purposes
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (50, 205, 50)

# setting the Game states
class GambleGame:
    def __init__(self, font, draw_text, Button, state):
        self.font = font
        self.draw_text = draw_text
        self.Button = Button
        self.state = state
        self.buttons = []
        self.result_shown = False
        self.retry_buttons = []
        self.result = ""
        self.coin_bg = None
        self.coin_heads = None
        self.coin_tails = None

        # Fonts:
        self.large_font = pygame.font.SysFont("arial", 36, bold=True)
        self.button_font = pygame.font.SysFont("arial", 28)

        # Loads and scales background and coin images with correct paths
        self.coin_bg = pygame.image.load("Images/coin bg.png").convert()
        self.coin_bg = pygame.transform.scale(self.coin_bg, (1000, 1000))

    def handle_event(self, event):
        # for Quitting the game
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.result_shown:
                for b in self.buttons:
                    if b.click(event.pos):
                        break
            else:
                for b in self.retry_buttons:
                    if b.click(event.pos):
                        break

    def update(self, win):
        # Sets the Game Screen
        if self.coin_bg:
            win.blit(self.coin_bg, (0, 0))
        if not self.result_shown:
            self.draw_text("Choose Heads or Tails!", 350, color=WHITE, align='center', font_override=self.large_font)

            # Centers the buttons
            button_width = 200
            button_height = 60
            spacing = 50
            total_width = button_width * 2 + spacing
            start_x = (win.get_width() - total_width) // 2
            button_y = 500
            self.buttons = [
                self.Button("Heads", start_x, button_y, button_width, button_height, lambda: self.flip_coin("Heads"),
                            color=(100, 180, 100), text_color=BLACK, font_override=self.button_font),
                self.Button("Tails", start_x + button_width + spacing, button_y, button_width, button_height,
                            lambda: self.flip_coin("Tails"), color=(180, 180, 180), text_color=BLACK,
                            font_override=self.button_font)
            ]
            for b in self.buttons:
                b.draw(win)
        else:
            if self.result == "Heads" and self.coin_heads:
                coin_img = self.coin_heads
            elif self.result == "Tails" and self.coin_tails:
                coin_img = self.coin_tails
            else:
                coin_img = None

            if coin_img:
                coin_rect = coin_img.get_rect(center=(win.get_width() // 2, 450))
                win.blit(coin_img, coin_rect)

            self.draw_text(self.state["message"], 350, color=WHITE, align='center', font_override=self.large_font)

            # Centers the retry button
            button_width = 200
            button_height = 60
            spacing = 50
            total_width = button_width * 2 + spacing
            start_x = (win.get_width() - total_width) // 2
            button_y = 500
            self.retry_buttons = [
                self.Button("Try Again", start_x, button_y, button_width, button_height, self.try_again, color=GREEN,
                            text_color=BLACK, font_override=self.button_font),
                self.Button("Exit", start_x + button_width + spacing, button_y, button_width, button_height,
                            self.exit_game, color=RED, text_color=BLACK, font_override=self.button_font)
            ]
            for b in self.retry_buttons:
                b.draw(win)

    def flip_coin(self, guess):
        # handling the flip / guess and result
        self.result = random.choice(["Heads", "Tails"])
        if guess == self.result:
            self.state["message"] = f"It's {self.result}! Good job!"
        else:
            self.state["message"] = f"It's {self.result}. Nope, well sucks to be you!."
        self.result_shown = True

    def try_again(self):
        self.result_shown = False
        self.state["message"] = "Choose Heads or Tails!"

    def exit_game(self):
        self.state["current_game"] = "menu"
