import pygame
import sys
import random
import time

pygame.init()
pygame.mixer.init()

# --- Setup ---
SCREEN = WIDTH, HEIGHT = 1000, 1000
win = pygame.display.set_mode(SCREEN)
pygame.display.set_caption("Combined Mini-Game Collection")
clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# --- Fonts ---
font = pygame.font.SysFont("arial", 24)
title_font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 18)

# --- Game State ---
DEBUG = False
name = ""
age = 0
score = 7
mistakes = 0
tickets = 3
current_game = "start_intro"
difficulty = 1
current_q = 0
message = ""
selected_animal = None
final_message = ""
music_started = False

# --- ASCII Art ---
ascii_art = {
    "Dog": """/^ ^\\
/ 0 0 \\
V\\ Y /V
 / - \\
 |    \\\\
 || (__)""",
    "Cat": """/\\_/\\
( o.o )
 > ^ <""",
    "Owl": """,_,
(O,O)
(   )
 " " """,
    "Elephant": """       _.-- ,.--.
     .'   .'     /
     | @       |'..--------._
    /      \\._/              '.
   /  .-.-                     \\
  (  /    \\                     \\
  \\      '.                  | #
   \\       \\   -.           /
    :\\       |    )._____.'   \\
     "       |   /  \\  |  \\    )
             |   |./'  :__ \\.-'
             '--'"""
}

# --- Questions ---
questions = [
    {"q": "How do you spell Sacrilegious?", "a": ["Sacriligious", "Sacrilegious", "Sacreligious"], "correct": 1},
    {"q": "Capital of Hungary?", "a": ["Vienna", "Budapest", "Prague"], "correct": 1},
    {"q": "Seconds in 7 days?", "a": ["604800", "700000", "540000"], "correct": 0},
]

# --- Button Class ---
class Button:
    def __init__(self, text, x, y, width, height, callback, color=GREEN, text_color=BLACK):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text_color = text_color
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()
            return True
        return False

# --- InputBox Class ---
class InputBox:
    def __init__(self, x, y, w, h, text='', is_numeric=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLACK
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False
        self.is_numeric = is_numeric

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = GREEN if self.active else BLACK
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = BLACK
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if self.is_numeric and event.unicode.isdigit() or not self.is_numeric:
                        self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)
        return False

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=10)

    def get_text(self):
        return self.text

# --- Drawing Helper ---
def draw_text(text, y, color=BLACK, x=20, align='left', font_override=None):
    current_font = font_override if font_override else font
    text_surf = current_font.render(text, True, color)
    text_rect = text_surf.get_rect()
    if align == 'center':
        text_rect.center = (WIDTH // 2, y)
    else:
        text_rect.topleft = (x, y)
    win.blit(text_surf, text_rect)

def evaluate_score(score_val, mistakes_val):
    return score_val - mistakes_val
# --- Intro Input Boxes ---
name_input_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40)
age_input_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 40, is_numeric=True)
intro_message_y = HEIGHT // 2 - 100

def reset_intro_inputs():
    global name, age, name_input_box, age_input_box, current_game, intro_message_y, music_started
    name = ""
    age = 0
    music_started = False
    name_input_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40)
    age_input_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 40, is_numeric=True)
    current_game = "start_intro"
    intro_message_y = HEIGHT // 2 - 100

def handle_start_intro_input():
    global current_game, name, age, message, tickets, intro_message_y, intro_messages_list, current_intro_message_index, music_started

    if name_input_box.text.strip() == "":
        message = "Please enter your name."
        return
    name = name_input_box.get_text()

    try:
        age = int(age_input_box.get_text())
        if age >= 125:
            message = "!!! AGE TOO HIGH !!!\\n!!! POSSIBLE RISK DETECTED !!!\\n!!!! SERVER SHUTTING DOWN !!!!"
            current_game = "fatal_error"
            return
        if age < 18:
            message = "Sorry, this game is not available for you right now.\\nCome back at a later point in time."
            current_game = "age_restricted"
            return

        message = f"Welcome {name}! Your age ({age}) processed.\\n\\nAccess granted. Welcome!"
        tickets = 3
        current_game = "display_intro_messages"
        intro_message_y = 20

        # Start music here
        if not music_started:
            try:
                pygame.mixer.music.load('retro_bg.mp3')
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                music_started = True
            except pygame.error as e:
                print(f"Could not load or play music: {e}")

        # Begin message sequence
        pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
        intro_messages_list = [
            f"{name}, before you can continue, we quickly have to confirm your age.",
            "Your age is being processed. Please wait...",
            "Counting days...",
            f"{name}, {age * 365} days old.",
            f"{name}, age {age}, scanning browser history...",
            "Building up suspense...",
            "--> Human being confirmed.",
            "Downloading invisible textures...",
            "Setting up games...",
            "i: Synchronization completed."
        ]
        current_intro_message_index = 0

    except ValueError:
        message = "That was not a valid number. Please enter your age using digits."

# --- Final Evaluation Matching Terminal Logic ---
def evaluate_final_message():
    global final_message, score, mistakes, name
    final_score = evaluate_score(score, mistakes)

    if 0 < final_score < 5:
        final_message = f"Score {final_score}/10 - {name} disappointed me. -_-"
    elif final_score == 10:
        final_message = f"Score {final_score}/10 - {name} is the coolest person ever <3"
    elif 5 < final_score < 10:
        final_message = f"Score {final_score}/10 - {name} is a cool person <3"
    elif final_score <= 0:
        final_message = f"Score {final_score}/10 - {name} how could this even happen...?!?!"

# --- Menu Buttons ---
menu_buttons = [
    Button("Quiz", 240, 100, 150, 40, lambda: choose_game(1)),
    Button("Gamble", 240, 160, 150, 40, lambda: choose_game(2)),
    Button("ASCII-Art", 240, 220, 150, 40, lambda: choose_game(3)),
    Button("Retro Game", 240, 280, 150, 40, lambda: choose_game(4))
]

# --- ASCII Buttons ---
ascii_buttons = [
    Button("Dog", 50, 100, 100, 40, lambda: handle_ascii_selection("Dog")),
    Button("Cat", 200, 100, 100, 40, lambda: handle_ascii_selection("Cat")),
    Button("Elephant", 350, 100, 130, 40, lambda: handle_ascii_selection("Elephant")),
    Button("Owl", 50, 160, 100, 40, lambda: handle_ascii_selection("Owl")),
    Button("All ASCII (2 Tickets)", 240, 220, 200, 40, lambda: handle_ascii_selection("All"), color=YELLOW)
]

# --- Game Selection Logic ---
def choose_game(game_id):
    global current_game, tickets, message, current_q, score, mistakes
    if tickets <= 0:
        message = "You are out of tickets!"
        return

    if game_id == 1:  # Quiz
        current_q = 0
        message = ""
        current_game = "quiz"
        tickets -= 1
    elif game_id == 2:  # Gamble
        tickets -= 1
        handle_gamble()
    elif game_id == 3:  # ASCII-Art
        current_game = "ascii"
        message = ""
    elif game_id == 4:  # Retro Game
        tickets -= 1
        current_game = "retro_game_intro"
        score = 0
        mistakes = 0
# --- Quiz ---
def handle_quiz_answer(index):
    global current_q, score, mistakes, message, current_game
    if index == questions[current_q]["correct"]:
        score += 1
        message = "Correct!"
    else:
        mistakes += 1
        message = "Wrong!"
    current_q += 1
    if current_q >= len(questions):
        current_game = "menu" if tickets > 0 else "end"
    else:
        pygame.time.set_timer(pygame.USEREVENT + 2, 1000)

# --- Gamble ---
def handle_gamble():
    global score, mistakes, current_game, message
    choice_made = False

    def make_guess(user_choice):
        nonlocal choice_made
        global score, mistakes, message, current_game
        if choice_made: return
        roll = random.choice(["Heads", "Tails"])
        if user_choice == roll:
            score += 1
            message = f"You won! Coin landed on {roll}."
        else:
            mistakes += 1
            message = f"You lost. Coin landed on {roll}."
        choice_made = True
        pygame.time.set_timer(pygame.USEREVENT + 3, 1500)

    global gamble_buttons
    gamble_buttons = [
        Button("Heads", WIDTH // 2 - 150, HEIGHT // 2 - 20, 100, 40, lambda: make_guess("Heads")),
        Button("Tails", WIDTH // 2 + 50, HEIGHT // 2 - 20, 100, 40, lambda: make_guess("Tails"))
    ]
    current_game = "gamble"
    message = "Choose Heads or Tails!"

# --- ASCII ---
def handle_ascii_selection(animal):
    global selected_animal, current_game, tickets, message
    if animal == "All":
        if tickets < 2:
            message = "Not enough tickets to show all ASCII art. Costs 2 tickets."
            return
        selected_animal = ""
        for art_name in ascii_art:
            selected_animal += ascii_art.get(art_name, "") + "\\n\\n"
        tickets -= 2
    else:
        selected_animal = ascii_art.get(animal, None)
        tickets -= 1
    current_game = "ascii_result"

# --- Retro Game ---
def run_retro_game():
    global current_game, score, mistakes

    player = pygame.Rect(WIDTH//2, HEIGHT-60, 40, 40)
    blocks = [pygame.Rect(random.randint(0, WIDTH-30), -random.randint(50, 500), 30, 30) for _ in range(5)]
    retro_score = 0
    retro_running = True

    while retro_running:
        win.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                retro_running = False
                current_game = "end"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                retro_running = False
                current_game = "menu" if tickets > 0 else "end"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.x -= 5
        if keys[pygame.K_RIGHT]: player.x += 5
        if keys[pygame.K_UP]: player.y -= 5
        if keys[pygame.K_DOWN]: player.y += 5
        player.clamp_ip(win.get_rect())

        for block in blocks:
            block.y += 5
            pygame.draw.rect(win, RED, block)
            if block.y > HEIGHT:
                block.x = random.randint(0, WIDTH-30)
                block.y = -random.randint(100, 300)
                retro_score += 1
            if player.colliderect(block):
                score += retro_score
                mistakes += 1
                retro_running = False
                current_game = "menu" if tickets > 0 else "end"

        if retro_score >= 100:
            score += retro_score
            retro_running = False
            current_game = "menu" if tickets > 0 else "end"

        pygame.draw.rect(win, WHITE, player)
        draw_text(f"Score: {retro_score}", 10, WHITE)
        pygame.display.update()
        clock.tick(FPS)

# --- Main Game Loop ---
# (Already in your original script – ensure you've added the event logic correctly):
# In event loop:
# Replace:
# current_game = "end"
# With:
# current_game = "menu" if tickets > 0 else "end"

# Likewise in:
# - QUIZ_MESSAGE_TIMER_EVENT
# - GAMBLE_RESULT_TIMER_EVENT
# - Retro game (above)

# --- End screen draw ---
# Inside if current_game == "end":
evaluate_final_message()
draw_text("Game Over!", 50, BLACK, align='center', font_override=title_font)
draw_text(final_message, 200, BLACK, align='center')
draw_text(f"{name}, you are out of tickets. You may leave now. Bye", 240, BLACK, align='center')
draw_text("Press [X] to quit.", 280, RED, align='center')
