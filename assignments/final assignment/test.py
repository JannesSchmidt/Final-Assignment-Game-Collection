import pygame
import sys
import random
import time # For time.sleep effects during intro

pygame.init()
pygame.mixer.init() # Initialize mixer for sound

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
BLUE = (0, 0, 255) # Added for retro game
YELLOW = (255, 255, 0) # For warning messages
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# --- Font ---
font = pygame.font.SysFont("arial", 24)
title_font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 18)

# --- Game State Variables ---
DEBUG = False # Set to True to skip name/age input for quick testing
name = ""
age = 0
score = 7 # Initial score from minigames.py
mistakes = 0 # Initial mistakes from minigames.py
tickets = 3 # Initial tickets from minigames.py
current_game = "start_intro" # Initial state for intro and age verification
difficulty = 1
current_q = 0 # For quiz game
message = "" # General message display
selected_animal = None # For ASCII art game
final_message = "" # For evaluation screen

# --- Audio ---
try:
    pygame.mixer.music.load('retro_bg.mp3') # Load background music
    pygame.mixer.music.set_volume(0.5) # Set volume (0.0 to 1.0)
    pygame.mixer.music.play(-1) # Play indefinitely
except pygame.error as e:
    print(f"Could not load or play music: {e}")
    print("Please ensure 'retro_bg.mp3' is in the same directory as the script.")


# --- ASCII Art (from minigames.py, adapted for GUI) ---
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

# --- Questions (from quiz_gui_game.py) ---
questions = [
    {"q": "How do you spell Sacrilegious?", "a": ["Sacriligious", "Sacrilegious", "Sacreligious"], "correct": 1},
    {"q": "Capital of Hungary?", "a": ["Vienna", "Budapest", "Prague"], "correct": 1},
    {"q": "Seconds in 7 days?", "a": ["604800", "700000", "540000"], "correct": 0},
]

# --- Button Class (from quiz_gui_game.py) ---
class Button:
    def __init__(self, text, x, y, width, height, callback, color=GREEN, text_color=BLACK):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text_color = text_color
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10) # Added rounded corners
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()
            return True # Indicate button was clicked
        return False

# --- Input Box Class for Text Input ---
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
                    return True # Indicate input is complete
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if self.is_numeric and event.unicode.isdigit() or not self.is_numeric:
                        self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)
        return False

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=10) # Added rounded corners

    def get_text(self):
        return self.text

# --- Helper Functions ---
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

# --- Game Screens and Logic ---

# Initial Intro Screen
name_input_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40)
age_input_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 40, is_numeric=True)
intro_message_y = HEIGHT // 2 - 100

def reset_intro_inputs():
    global name, age, name_input_box, age_input_box, current_game, intro_message_y
    name = ""
    age = 0
    name_input_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40)
    age_input_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 40, is_numeric=True)
    current_game = "start_intro"
    intro_message_y = HEIGHT // 2 - 100


def handle_start_intro_input():
    global current_game, name, age, message, tickets, intro_message_y
    if name_input_box.text.strip() == "":
        message = "Please enter your name."
        return
    name = name_input_box.get_text()

    try:
        age = int(age_input_box.get_text())
        if age >= 125:
            message = "!!! AGE TOO HIGH !!!\n!!! POSSIBLE RISK DETECTED !!!\n!!!! SERVER SHUTTING DOWN !!!!"
            current_game = "fatal_error" # A new state for unrecoverable errors
            return
        if age < 18:
            message = "Sorry, this game is not available for you right now.\nCome back at a later point in time."
            current_game = "age_restricted" # A new state for age restriction
            return
        message = f"Welcome {name}! Your age ({age}) processed.\n\nAccess granted. Welcome!"
        tickets = 3 # Grant tickets
        current_game = "display_intro_messages" # Move to display sequence
        intro_message_y = 20 # Reset message Y for sequence
        # Start initial message sequence
        pygame.time.set_timer(pygame.USEREVENT + 1, 1500) # Timer for messages
        # messages will be displayed one by one
        global intro_messages_list, current_intro_message_index
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

# Define buttons for the main menu
menu_buttons = [
    Button("Quiz", 240, 100, 150, 40, lambda: choose_game(1)),
    Button("Gamble", 240, 160, 150, 40, lambda: choose_game(2)),
    Button("ASCII-Art", 240, 220, 150, 40, lambda: choose_game(3)),
    Button("Retro Game", 240, 280, 150, 40, lambda: choose_game(4)) # New retro game
]

# Define buttons for ASCII art selection
ascii_buttons = [
    Button("Dog", 50, 100, 100, 40, lambda: handle_ascii_selection("Dog")),
    Button("Cat", 200, 100, 100, 40, lambda: handle_ascii_selection("Cat")),
    Button("Elephant", 350, 100, 130, 40, lambda: handle_ascii_selection("Elephant")),
    Button("Owl", 50, 160, 100, 40, lambda: handle_ascii_selection("Owl")),
    Button("All ASCII (2 Tickets)", 240, 220, 200, 40, lambda: handle_ascii_selection("All"), color=YELLOW)
]

# Quiz buttons will be generated dynamically

# --- Game Logic Functions ---
def choose_game(game_id):
    global current_game, tickets, message, current_q, score, mistakes
    if tickets <= 0:
        message = "You are out of tickets!"
        return

    if game_id == 1: # Quiz
        current_q = 0 # Reset quiz questions
        message = "" # Clear message
        current_game = "quiz"
        tickets -= 1
    elif game_id == 2: # Gamble
        tickets -= 1
        handle_gamble()
    elif game_id == 3: # ASCII-Art
        current_game = "ascii"
        message = "" # Clear message
    elif game_id == 4: # Retro Game
        tickets -= 1
        current_game = "retro_game_intro"
        # Reset score and mistakes for retro game
        score = 0
        mistakes = 0


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
        current_game = "end" # Go to end screen after quiz
    else:
        # Give a moment to see the message before advancing
        pygame.time.set_timer(pygame.USEREVENT + 2, 1000) # Short delay for message


def handle_gamble():
    global score, mistakes, current_game, message
    # Simple gambling: guess if a coin flip is heads or tails
    choice_made = False

    def make_guess(user_choice):
        nonlocal choice_made
        global score, mistakes, message, current_game # Changed nonlocal to global
        if choice_made: return # Prevent multiple clicks
        roll = random.choice(["Heads", "Tails"])
        if user_choice == roll:
            score += 1
            message = f"You won! Coin landed on {roll}."
        else:
            mistakes += 1
            message = f"You lost. Coin landed on {roll}."
        choice_made = True
        pygame.time.set_timer(pygame.USEREVENT + 3, 1500) # Short delay to show result then return to menu

    global gamble_buttons
    gamble_buttons = [
        Button("Heads", WIDTH // 2 - 150, HEIGHT // 2 - 20, 100, 40, lambda: make_guess("Heads")),
        Button("Tails", WIDTH // 2 + 50, HEIGHT // 2 - 20, 100, 40, lambda: make_guess("Tails"))
    ]
    current_game = "gamble"
    message = "Choose Heads or Tails!"


def handle_ascii_selection(animal):
    global selected_animal, current_game, tickets, message
    if animal == "All":
        if tickets < 2:
            message = "Not enough tickets to show all ASCII art. Costs 2 tickets."
            return
        selected_animal = ""
        for art_name in ascii_art:
            selected_animal += ascii_art_text(art_name) + "\n\n" # Add the actual ASCII text
        tickets -= 2 # Deduct 2 tickets for all
    else:
        selected_animal = ascii_art.get(animal, None)
    current_game = "ascii_result"

def ascii_art_text(animal_name):
    # This helper function now applies colors directly if needed, or just returns raw ASCII.
    # For simplicity, returning raw ASCII as colors are hard to manage in a Pygame text blit without custom rendering.
    return ascii_art.get(animal_name, "Error: Art not found.")

def evaluate_final_message():
    global final_message, score, mistakes, name
    final_score = evaluate_score(score, mistakes)
    if final_score == 10:
        final_message = f"Score {final_score}/10 - {name} is the coolest person ever <3"
    elif 5 < final_score < 10:
        final_message = f"Score {final_score}/10 - {name} is a cool person <3"
    elif 0 < final_score <= 5:
        final_message = f"Score {final_score}/10 - {name} disappointed me."
    else:
        final_message = f"Score {final_score}/10 - {name} how could this even happen...?!?!"

# --- Retro Game Logic (adapted from game12.py) ---
def run_retro_game():
    global current_game, score, mistakes

    retro_game_win = win # Use the main window for the retro game
    retro_game_width, retro_game_height = WIDTH, HEIGHT

    player_surf = pygame.Surface((40, 40))
    player_surf.fill(WHITE)
    player_rect = player_surf.get_rect(center=(retro_game_width//2, retro_game_height - 50))

    blocks = []
    for _ in range(5):
        rect = pygame.Rect(random.randint(0, retro_game_width - 30), random.randint(-600, -50), 30, 30)
        blocks.append(rect)

    retro_score = 0
    retro_game_running = True

    # Show instructions
    retro_game_win.fill(BLACK)
    instruction_text = font.render("Use Arrow Keys to Move. Avoid Red Blocks! Reach 100 points.", True, WHITE)
    instruction_rect = instruction_text.get_rect(center=(retro_game_width//2, retro_game_height//2 - 20))
    retro_game_win.blit(instruction_text, instruction_rect)

    countdown_font = pygame.font.SysFont("arial", 72, bold=True)
    for i in range(3, 0, -1):
        retro_game_win.fill(BLACK)
        retro_game_win.blit(instruction_text, instruction_rect)
        countdown_text = countdown_font.render(str(i), True, YELLOW)
        countdown_rect = countdown_text.get_rect(center=(retro_game_width//2, retro_game_height//2 + 50))
        retro_game_win.blit(countdown_text, countdown_rect)
        pygame.display.flip()
        pygame.time.delay(1000)

    while retro_game_running:
        retro_game_win.fill(BLACK) # Clear the screen for the retro game

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                retro_game_running = False
                current_game = "end" # Exit to end screen if user quits during retro game
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Allow escaping the game
                    retro_game_running = False
                    current_game = "menu" # Go back to menu

        keys = pygame.key.get_pressed() # movement commands
        if keys[pygame.K_LEFT]:
            player_rect.x -= 5
        if keys[pygame.K_RIGHT]:
            player_rect.x += 5
        if keys[pygame.K_UP]:
            player_rect.y -= 5
        if keys[pygame.K_DOWN]:
            player_rect.y += 5

        player_rect.clamp_ip(retro_game_win.get_rect())

        for block in blocks: # "Enemies" or Obstacles rather
            block.y += 5
            pygame.draw.rect(retro_game_win, RED, block)
            if block.y > retro_game_height:
                block.x = random.randint(0, retro_game_width - 30)
                block.y = random.randint(-100, -50)
                retro_score += 1
            if player_rect.colliderect(block): # Game over condition
                score = retro_score # Update main score with retro game score before ending
                mistakes += 1 # A mistake for losing
                game_over_text = title_font.render("Game Over", True, RED)
                retro_game_win.blit(game_over_text, (retro_game_width//2 - game_over_text.get_width()//2, retro_game_height//2 - 20))
                pygame.display.flip()
                pygame.time.delay(2000)
                retro_game_running = False
                current_game = "end" # Go to the end screen

        if retro_score >= 100: # Winning condition
            score = retro_score # Update main score
            winning_text = title_font.render("You won!", True, WHITE)
            retro_game_win.blit(winning_text, (retro_game_width//2 - winning_text.get_width()//2, retro_game_height//2 - 20))
            pygame.display.flip()
            pygame.time.delay(2000)
            retro_game_running = False
            current_game = "end" # Go to the end screen

        retro_game_win.blit(player_surf, player_rect)
        score_surf = font.render(f"Score: {retro_score}", True, WHITE)
        retro_game_win.blit(score_surf, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


# --- Main Game Loop ---
running = True
# States for intro messages
intro_messages_list = []
current_intro_message_index = 0
current_displayed_intro_message = ""
MESSAGE_TIMER_EVENT = pygame.USEREVENT + 1 # Timer for sequence messages
QUIZ_MESSAGE_TIMER_EVENT = pygame.USEREVENT + 2 # Timer for quiz answer message
GAMBLE_RESULT_TIMER_EVENT = pygame.USEREVENT + 3 # Timer for gamble result message

while running:
    win.fill(WHITE) # Fill background for all screens

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_game == "start_intro":
                name_input_box.handle_event(event)
                age_input_box.handle_event(event)
                # After Confirm Button is hit, the code continues
                for b in [Button("Confirm", WIDTH // 2 - 75, HEIGHT // 2 + 120, 150, 40, handle_start_intro_input)]:
                    b.click(event.pos)
            elif current_game == "menu":
                for b in menu_buttons:
                    if b.click(event.pos):
                        message = "" # Here the desired game can be selected
            elif current_game == "quiz":
                for b in quiz_buttons:
                    b.click(event.pos)
            elif current_game == "ascii":
                for b in ascii_buttons:
                    if b.click(event.pos):
                        message = "" # Clears messages for ASCII game
            elif current_game == "ascii_result":
                # Button to go back to menu
                back_button = Button("Back to Menu", WIDTH // 2 - 100, HEIGHT - 70, 200, 50, lambda: globals().update(current_game="menu", selected_animal=None))
                back_button.click(event.pos)
            elif current_game == "gamble":
                for b in gamble_buttons:
                    b.click(event.pos)
            elif current_game == "fatal_error" or current_game == "age_restricted":
                 # Add a button to reset or quit after a fatal error/age restriction
                 reset_button = Button("Restart", WIDTH // 2 - 100, HEIGHT - 70, 200, 50, reset_intro_inputs)
                 quit_button = Button("Quit", WIDTH // 2 - 100, HEIGHT - 10, 200, 50, lambda: globals().update(running=False))
                 reset_button.click(event.pos)
                 quit_button.click(event.pos)

        elif event.type == pygame.KEYDOWN:
            if current_game == "start_intro":
                if name_input_box.active:
                    name_input_box.handle_event(event)
                elif age_input_box.active:
                    age_input_box.handle_event(event)
                # Allow pressing ENTER to confirm input
                if event.key == pygame.K_RETURN:
                    if name_input_box.active:
                        name_input_box.active = False
                        age_input_box.active = True # Move to age input
                    elif age_input_box.active:
                        age_input_box.active = False
                        handle_start_intro_input() # Process name/age

            elif current_game == "ascii_result":
                if event.key == pygame.K_x: # Press 'X' to go back
                    current_game = "menu"
                    selected_animal = None
            elif current_game == "end":
                if event.key == pygame.K_x: # Press 'X' to quit
                    running = False
        elif event.type == MESSAGE_TIMER_EVENT:
            if current_game == "display_intro_messages":
                if current_intro_message_index < len(intro_messages_list):
                    current_displayed_intro_message = intro_messages_list[current_intro_message_index]
                    current_intro_message_index += 1
                else:
                    pygame.time.set_timer(MESSAGE_TIMER_EVENT, 0) # Stop timer
                    current_game = "menu" # Go to main menu after all messages
                    current_displayed_intro_message = "" # Clear message
        elif event.type == QUIZ_MESSAGE_TIMER_EVENT:
            pygame.time.set_timer(QUIZ_MESSAGE_TIMER_EVENT, 0) # Stop timer
            # Advance quiz or go to end
            if current_q < len(questions):
                message = "" # Clear message for next question
            else:
                current_game = "end"
        elif event.type == GAMBLE_RESULT_TIMER_EVENT:
            pygame.time.set_timer(GAMBLE_RESULT_TIMER_EVENT, 0) # Stop timer
            current_game = "menu" # Return to menu after gamble result


    # --- Drawing Logic based on current_game state ---
    if current_game == "start_intro":
        draw_text("Welcome!", HEIGHT // 2 - 180, BLACK, align='center', font_override=title_font)
        draw_text("Please enter your name:", HEIGHT // 2 - 50, BLACK, align='center')
        name_input_box.draw(win)
        draw_text("Please enter your age:", HEIGHT // 2 + 30, BLACK, align='center')
        age_input_box.draw(win)
        confirm_button = Button("Confirm", WIDTH // 2 - 75, HEIGHT // 2 + 120, 150, 40, handle_start_intro_input)
        confirm_button.draw(win)
        draw_text(message, HEIGHT // 2 + 180, RED if "Invalid" in message or "Please" in message else BLACK, align='center', font_override=small_font)

    elif current_game == "display_intro_messages":
        win.fill(BLACK)
        draw_text(current_displayed_intro_message, HEIGHT // 2 - 50, WHITE, align='center')
        draw_text("___________________________________________________________________", HEIGHT // 2 + 50, WHITE, align='center', font_override=small_font)
        # News message from minigames.py
        news = "i: Don't miss out on the new ASCII-Art."
        border = "." * (len(news) + 4)
        draw_text(border, HEIGHT // 2 + 100, WHITE, align='center', font_override=small_font)
        draw_text(f": {news} :", HEIGHT // 2 + 130, WHITE, align='center', font_override=small_font)
        draw_text(border, HEIGHT // 2 + 160, WHITE, align='center', font_override=small_font)

    elif current_game == "menu":
        draw_text(f"Welcome {name}. Tickets: {tickets}", 20)
        draw_text("It's time to choose your minigame!", 60)
        for b in menu_buttons:
            b.draw(win)
        if message: # Display messages related to ticket warnings or game choices
            draw_text(message, HEIGHT - 50, RED, align='center')

    elif current_game == "quiz":
        if current_q < len(questions):
            q = questions[current_q]
            draw_text(q["q"], 20)
            quiz_buttons = [] # Re-create buttons for current question
            for i, a in enumerate(q["a"]):
                b = Button(a, 100, 100 + i*60, 400, 40, lambda i=i: handle_quiz_answer(i))
                b.draw(win)
                quiz_buttons.append(b)
        draw_text(message, 300, BLUE if "Correct" in message else RED) # Show quiz result message

    elif current_game == "gamble":
        draw_text("Ah, a fellow gambling addict. I welcome you <3:", 20)
        draw_text(message, 60) # Instructions for gamble
        for b in gamble_buttons:
            b.draw(win)

    elif current_game == "ascii":
        draw_text("ASCII-Art Generator! Choose your animal:", 20)
        for b in ascii_buttons:
            b.draw(win)
        if message:
            draw_text(message, HEIGHT - 50, RED, align='center') # Display messages like "Not enough tickets"

    elif current_game == "ascii_result":
        if selected_animal:
            # Render multi-line ASCII art
            lines = selected_animal.split("\n")
            y_offset = 80
            for i, line in enumerate(lines):
                draw_text(line, y_offset + i*20, BLACK) # Adjust Y for multi-line art
        draw_text("Press ESC or click 'Back to Menu' to go back.", 20)
        back_button = Button("Back to Menu", WIDTH // 2 - 100, HEIGHT - 70, 200, 50, lambda: globals().update(current_game="menu", selected_animal=None))
        back_button.draw(win)

    elif current_game == "retro_game_intro":
        run_retro_game() # This function takes over the display loop until the game ends, then sets current_game

    elif current_game == "end":
        evaluate_final_message() # Calculate final message before displaying
        draw_text("Game Over!", 50, BLACK, align='center', font_override=title_font)
        draw_text(final_message, 200, BLACK, align='center') # Dynamic message based on score
        draw_text(f"{name}, you are out of tickets. You may leave now. Bye", 240, BLACK, align='center')
        draw_text("Press [X] to quit.", 280, RED, align='center')

    elif current_game == "fatal_error" or current_game == "age_restricted":
        win.fill(BLACK)
        draw_text(message, HEIGHT // 2 - 50, RED, align='center', font_override=font)
        draw_text("___________________________________________________________________", HEIGHT // 2 + 50, WHITE, align='center', font_override=small_font)
        reset_button = Button("Restart", WIDTH // 2 - 100, HEIGHT - 70, 200, 50, reset_intro_inputs, color=YELLOW)
        quit_button = Button("Quit", WIDTH // 2 - 100, HEIGHT - 10, 200, 50, lambda: globals().update(running=False), color=RED)
        reset_button.draw(win)
        quit_button.draw(win)


    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
#guuut