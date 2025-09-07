import pygame
import sys
import time
import json
import os
import datetime

from MiniGames.Quiz import QuizGame
from MiniGames.Gambling import GambleGame
from MiniGames.Ascii_Art import AsciiArtGame
from MiniGames.Retro_Game import start_retro_game
from MiniGames.slot import SlotGame


DEBUG = True  # False is the standard. True = Admin Mode for fast testing, with new music.

SCOREBOARD_FILE = "scoreboard.json"

# Initializes all pygame modules
pygame.init()
pygame.mixer.init()

# Screen Setup / Settings
WIDTH, HEIGHT = 1000, 1000
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini-Game Collection")
clock = pygame.time.Clock()
FPS = 60

# Defining the Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (50, 205, 50)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREY = (150, 150, 150)

# Fonts for upcoming text messages
font = pygame.font.SysFont("arial", 24)
title_font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 18)


# The dictionaries purpose is to hold the game states
state = {
    "name": "",
    "age": 0,
    "score": 7, # 7 because with the 3 tickets you can't otherwise get 10/10 points
    "mistakes": 0, # relevant for the evaluation at the end
    "tickets": 3,
    "balance": 100,
    "current_game": "start_intro",
    "message": "",
    "selected_animal": None,
    "final_message": "",
    "current_q": 0,
    "intro_messages": [],
    "intro_index": 0,
    "current_intro_message": "",
    "loading_bar_progress": 0.0,
    "loading_bar_start_time": 0,
    "loading_dots_frame": 0,
    "scoreboard_updated": False,
    "ending_song_played": False,
}

def normalize_name(name: str) -> str:
    # This normalizes the name by removing extra spaces and making it lowercase (helps with the scoreboard)
    return name.strip().lower()


def load_scoreboard() -> dict: # Credits at the bottom *1
    # Checks if the scoreboard file exists and loads it
    if os.path.exists(SCOREBOARD_FILE):
        try:
            with open(SCOREBOARD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Failed to load scoreboard:", e)
    # Returns an empty dictionary if the file doesn't exist or an error occurs
    return {}

def save_scoreboard():
    # Tries to save the scoreboard data in/as a json.file
    try:
        with open(SCOREBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(scoreboard, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Failed to save scoreboard:", e)


def update_scoreboard():
    # Evaluates the player's name and age
    name = state.get("name", "").strip()
    try:
        age = int(state.get("age", 0))
    except Exception:
        age = 0
    if not name:
        return
    # Calculates the final score
    score_val = int(state.get("score", 0)) - int(state.get("mistakes", 0))
    # Creates a unique key for the player
    key = f"{normalize_name(name)}#{age}"
    now = datetime.datetime.utcnow().isoformat()
    entry = scoreboard.get(key)
    # Updates the scoreboard entry or creates a new one
    if entry is None:
        scoreboard[key] = {
            "display_name": name,
            "age": age,
            "score": score_val,
            "tries": 1,
            "last": now
        }
    else:
        entry["tries"] = int(entry.get("tries", 0)) + 1
        entry["score"] = score_val
        entry["last"] = now
    # Saves the updated scoreboard
    save_scoreboard()

# load scoreboard from disk
scoreboard = load_scoreboard()

# Music area:
# Handles music loading based on the debug flag
try:
    if DEBUG:
        pygame.mixer.music.load('Songs/admin_song.mp3') # For the extra flair. Can get annoying to be honest...
    else:
        pygame.mixer.music.load('Songs/retro_bg.mp3')
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
except pygame.error:
    print("Could not load background music.")

# Image area:
# Loads and scales the menu background image
try:
    menu_background_image = pygame.image.load('Images/menu bg.png').convert()
    menu_background_image = pygame.transform.scale(menu_background_image, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Error loading menu background image: {e}")
    menu_background_image = None


# Input-Box class
class InputBox:
    def __init__(self, x, y, w, h, text='', is_numeric=False):
        # Initializes the input box properties
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.txt_surface = font.render(self.text, True, self.color)
        self.active = False
        self.is_numeric = is_numeric

    def handle_event(self, event):
        # Handles user input events like mouse clicks and key presses
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = GREEN if self.active else WHITE
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = WHITE
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif not self.is_numeric or event.unicode.isdigit():
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, WHITE)

    def draw(self, screen):
        # Draws the input box on the screen
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        # Returns the text from the input box
        return self.text


# Normal button Class
class Button:
    def __init__(self, text, x, y, width, height, callback, color=GREEN, text_color=BLACK, font_override=None):
        # Initializes the button properties
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text_color = text_color
        self.callback = callback
        self.font = font_override if font_override else font

    def draw(self, surface):
        # Draws the button on the surface
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def click(self, pos):
        # Checks if the button was clicked
        if self.rect.collidepoint(pos):
            self.callback()
            return True
        return False


# Other functions
def draw_text(text, y, color=BLACK, x=20, align='left', font_override=None):
    # Renders and draws text on the screen
    current_font = font_override or font
    text_surf = current_font.render(text, True, color)
    text_rect = text_surf.get_rect()
    if align == 'center':
        text_rect.center = (WIDTH // 2, y)
    else:
        text_rect.topleft = (x, y)
    win.blit(text_surf, text_rect)


def draw_retro_loading_bar(progress):
    # Creates a retro-style loading bar. Credits below *2
    bar_width = 400
    bar_height = 50
    x = (WIDTH - bar_width) // 2
    y = (HEIGHT - bar_height) // 2
    pixel_size = 5
    dots = "." * (state["loading_dots_frame"] % 4)
    loading_text = f"LOADING{dots}"
    loading_surf = font.render(loading_text, True, WHITE)
    loading_rect = loading_surf.get_rect(center=(WIDTH // 2, y - 40))
    win.blit(loading_surf, loading_rect)
    for i in range(bar_width // pixel_size):
        for j in range(bar_height // pixel_size):
            pygame.draw.rect(win, GREY, (x + i * pixel_size, y + j * pixel_size, pixel_size - 1, pixel_size - 1))
    fill_pixels = int(progress * (bar_width // pixel_size))
    for i in range(fill_pixels):
        for j in range(bar_height // pixel_size):
            pygame.draw.rect(win, BLUE, (x + i * pixel_size, y + j * pixel_size, pixel_size - 1, pixel_size - 1))


# Handling  the name/age input
def confirm_age_and_name():
        name_text = name_box.get_text().strip()
        age_text = age_box.get_text().strip()
        state["name"] = name_text
        state["age"] = int(age_text) if age_text != "" else 0
        # Checks if the age is at least 18
        if state["age"] < 18:
            state["message"] = "You must be 18 or older. Sorry mate. Cry about it. ^-^"
            return
        # Setting up the intro messages and transitions to the loading state
        state["intro_messages"] = [
            f"{state['name']}, before you can continue, we quickly have to confirm your age.",
            "Processing age...",
            f"Days alive: {state['age'] * 365}.",
            "Verifying identity...",
            "Loading mini-games...",
            "Shortly wasting everyone's time...",
            "Setup complete. Welcome!"
        ]
        state["intro_index"] = 0
        pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
        state["current_game"] = "loading"
        state["scoreboard_updated"] = False


def evaluate_final_message():
    # Calculates the final score and assigns a message
    score_val = state["score"] - state["mistakes"]
    name = state["name"]
    if score_val == 10:
        state["final_message"] = f"Score {score_val}/10 - {name} is the coolest person ever <3. Well done!"
    elif 5 < score_val < 10:
        state["final_message"] = f"Score {score_val}/10 - {name} is a cool person <3. You tried your very best!"
    elif 0 < score_val <= 5:
        state["final_message"] = f"Score {score_val}/10 - {name} disappointed me. Better luck next time."
    else:
        state["final_message"] = f"Score {score_val}/10 - {name}, how could this even happen?! Like for real - I created this as a joke..."


# Creates instances of the mini-games
quiz = QuizGame(font, draw_text, Button, state)
gamble = GambleGame(font, draw_text, Button, state)
ascii_art = AsciiArtGame(font, draw_text, Button, state)
slot_game = SlotGame(font, Button, state)

# Creates input boxes and buttons for the intro screen
name_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40)
age_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 40, is_numeric=True)
confirm_button = Button("Confirm", WIDTH // 2 - 75, HEIGHT // 2 + 120, 150, 40, confirm_age_and_name, text_color=BLACK,
                        color=GREEN)
# If DEBUG is True, skip the intro and set a default name and age
if DEBUG:
    state["name"] = "Admin"
    state["age"] = 99
    state["current_game"] = "menu"


# In case someone wants to give it another go. Couldn't find a better way to do it...
def restart_game():
    # Reset all game state variables
    state.update({
        "name": "",
        "age": 0,
        "score": 7,
        "mistakes": 0,
        "tickets": 3,
        "balance": 100,
        "current_game": "start_intro",
        "message": "",
        "selected_animal": None,
        "final_message": "",
        "current_q": 0,
        "intro_messages": [],
        "intro_index": 0,
        "current_intro_message": "",
        "loading_bar_progress": 0.0,
        "loading_bar_start_time": 0,
        "loading_dots_frame": 0,
        "scoreboard_updated": False,
        "ending_song_played": False,  # Reset on restart
    })

    # Handles music and game state based on DEBUG flag
    try:
        if DEBUG:
            pygame.mixer.music.load('Songs/admin_song.mp3')
            state["name"] = "Admin"
            state["age"] = 99
            state["current_game"] = "menu"
        else:
            pygame.mixer.music.load('Songs/retro_bg.mp3')
            state["current_game"] = "start_intro"
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Could not load background music.")


try_again_button = Button("Try Again", WIDTH // 2 - 75, 450, 150, 40, restart_game)


def show_scoreboard(): # No explanation needed. I hope.
    state["current_game"] = "scoreboard"


def back_to_end():
    state["current_game"] = "end"


scoreboard_button = Button("Scoreboard", WIDTH // 2 - 75, 520, 150, 40, show_scoreboard)
back_button = Button("Back", WIDTH // 2 - 75, HEIGHT - 100, 150, 40, back_to_end)


# More buttons + Ticket control:
def start_game(game, message=None):
    # Checks if the player has tickets and starts the game
    if state["tickets"] > 0:
        state["tickets"] -= 1
        state["current_game"] = game
        state["scoreboard_updated"] = False
        state["ending_song_played"] = False
        if message:
            state["message"] = message
    else:
        state.update({
            "current_game": "end_loading",
            "loading_bar_start_time": time.time(),
            "message": "You have no tickets left to play!"
        })

# "Going" into the games
def start_quiz():
    start_game("quiz")

def start_gamble():
    start_game("gamble", "Choose Heads or Tails!")

def start_ascii():
    start_game("ascii")

def start_retro():
    start_game("retro")

def start_slot():
    start_game("slot")

menu_buttons = [
    Button("Quiz", WIDTH // 2 - 75, 300, 150, 40, start_quiz, text_color=WHITE, color=BLUE),
    Button("Gamble", WIDTH // 2 - 75, 360, 150, 40, start_gamble, text_color=WHITE, color=BLUE),
    Button("ASCII-Art", WIDTH // 2 - 75, 420, 150, 40, start_ascii, text_color=WHITE, color=BLUE),
    Button("Retro Game", WIDTH // 2 - 75, 480, 150, 40, start_retro, text_color=WHITE, color=BLUE),
    Button("Slot Machine", WIDTH // 2 - 75, 540, 150, 40, start_slot, text_color=WHITE, color=BLUE),
]

# Game Loop
running = True
while running:
    # If you want to leave.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif state["current_game"] == "start_intro":
            name_box.handle_event(event)
            age_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                confirm_button.click(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and state["current_game"] == "menu":
            for b in menu_buttons:
                b.click(event.pos)
        elif state["current_game"] == "quiz":
            quiz.handle_event(event)
        elif state["current_game"] == "gamble":
            gamble.handle_event(event)
        elif state["current_game"] == "ascii":
            ascii_art.handle_event(event)
        elif state["current_game"] == "slot":
            slot_game.handle_event(event)

        elif state["current_game"] == "loading" and event.type == pygame.USEREVENT + 1:
            if state["intro_index"] < len(state["intro_messages"]):
                state["current_intro_message"] = state["intro_messages"][state["intro_index"]]
                state["intro_index"] += 1
            else:
                # Stops the timer and transitions to the menu
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                state["current_game"] = "menu"

        if event.type == pygame.USEREVENT + 2:
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)
            state["current_game"] = "menu" if state["tickets"] > 0 else "end_loading"
            if state["current_game"] == "end_loading":
                state["loading_bar_start_time"] = time.time()
        if event.type == pygame.USEREVENT + 3:
            pygame.time.set_timer(pygame.USEREVENT + 3, 0)
            state["selected_animal"] = None
            state["current_game"] = "menu" if state["tickets"] > 0 else "end_loading"
            if state["current_game"] == "end_loading":
                state["loading_bar_start_time"] = time.time()

        if event.type == pygame.MOUSEBUTTONDOWN and state["current_game"] == "end":
            # Checks for clicks on the game over buttons
            try_again_button.click(event.pos)
            scoreboard_button.click(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and state["current_game"] == "scoreboard":
            # Checks for clicks on the back button
            back_button.click(event.pos)

    # Drawing
    if state["current_game"] == "start_intro":
        # Draws the intro screen
        if menu_background_image:
            win.blit(menu_background_image, (0, 0))
        draw_text("Enter Name:", HEIGHT // 2 - 50, color=WHITE, align='center')
        draw_text("Enter Age:", HEIGHT // 2 + 30, color=WHITE, align='center')
        name_box.draw(win)
        age_box.draw(win)
        confirm_button.draw(win)
        draw_text(state["message"], HEIGHT - 100, RED, align='center')

    elif state["current_game"] == "loading":
        # Draws the loading screen
        win.fill(BLACK)
        draw_text(state["current_intro_message"], HEIGHT // 2, WHITE, align='center')

    elif state["current_game"] == "menu":
        # Draws up the main menu
        if menu_background_image:
            win.blit(menu_background_image, (0, 0))

        draw_text(f"Welcome {state['name']} (Tickets: {state['tickets']})", 955, color=BLACK, align='center')
        draw_text("Please choose a game (-1 Ticket):", 100, color=WHITE, align='center', font_override=title_font)
        for b in menu_buttons:
            b.draw(win)
        draw_text(state["message"], HEIGHT - 100, RED, align='center')

    elif state["current_game"] == "quiz":
        # Updates and draws the quiz game
        quiz.update(win)
    if state["current_q"] >= 3:
        state["current_q"] = 0
        state["message"] = ""
        state["current_game"] = "menu" if state["tickets"] > 0 else "end_loading"
        if state["current_game"] == "end_loading":
            state["loading_bar_start_time"] = time.time()

    elif state["current_game"] == "gamble":
        # Updates and draws the gambling game
        gamble.update(win)
    elif state["current_game"] == "ascii":
        # Updates and draws the ascii art game
        ascii_art.update(win)
    elif state["current_game"] == "slot":
        # Updates and draws the slot machine game
        slot_game.update(win)

    elif state["current_game"] == "retro":
        # Starts the retro game
        start_retro_game(win, font, clock, WIDTH, HEIGHT, FPS, state)
        state["current_game"] = "menu" if state["tickets"] > 0 else "end_loading"
        if state["current_game"] == "end_loading":
            state["loading_bar_start_time"] = time.time()

    elif state["current_game"] == "end_loading":
        # Clears the screen and draws the loading bar
        win.fill(BLACK)
        draw_text("Evaluating final score...", HEIGHT // 2 - 100, WHITE, align='center')
        # Animate the loading dots every 0.5s. Again *2
        if time.time() - state.get("last_dot_update", 0) > 0.5:
            state["loading_dots_frame"] = (state["loading_dots_frame"] + 1) % 4
            state["last_dot_update"] = time.time()
        # Progress bar
        elapsed_time = time.time() - state["loading_bar_start_time"]
        loading_duration = 6.0
        progress = min(elapsed_time / loading_duration, 1.0)
        draw_retro_loading_bar(progress)
        if progress >= 1.0:
            # Transitions to the end screen
            state["current_game"] = "end"

    elif state["current_game"] == "end":
        # Clears the screen and draws the game over screen
        win.fill(WHITE)
        if not state.get("scoreboard_updated", False):
            update_scoreboard()
            state["scoreboard_updated"] = True

        if not state["ending_song_played"]:
            try:
                pygame.mixer.music.load('Songs/ending_song.mp3')
                pygame.mixer.music.play(-1)
                state["ending_song_played"] = True
            except pygame.error:
                print("Could not load ending music.")

        evaluate_final_message()
        draw_text("Game Over!", 100, RED, align='center', font_override=title_font)
        draw_text(state["final_message"], 200, BLACK, align='center')
        draw_text("Press ESC to quit.", 300, BLACK, align='center')
        try_again_button.draw(win)
        scoreboard_button.draw(win)

    elif state["current_game"] == "scoreboard":
        # Draws the scoreboard
        win.fill(WHITE)
        draw_text("Scoreboard", 50, BLACK, align="center", font_override=title_font)
        # Sorts the scoreboard entries
        entries = list(scoreboard.values())
        entries.sort(key=lambda e: (-int(e.get("tries", 0)),
                                    -int(e.get("score", 0)),
                                    e.get("display_name", "").lower()))
        y = 120
        # Loops through and displays each scoreboard entry
        for e in entries:
            if y > HEIGHT - 150:
                draw_text("... more entries ...", y, BLACK, align="center")
                break
            entry = f"{e['display_name']} ({e['age']}): {e['score']} points - {e['tries']} tries"
            draw_text(entry, y, BLACK, align="center")
            y += 30

        back_button.draw(win)

    # Updates the display
    pygame.display.flip()
    # Controls the game's frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()
# End of the Game/Code

# Credits:
#*1
#*2