import pygame
import time

# The questions with the respective answers.
questions = [
    {"q": "What is the Capital of Hungary?", "a": ["Vienna", "Budapest", "Prague"], "correct": 1},
    {"q": "How many seconds are in 7 days?", "a": ["604800", "700000", "540000"], "correct": 0},
    {"q": "How do you spell Sacrilegious?", "a": ["Sacriligious", "Sacrilegious", "Sacreligious"], "correct": 1},
]

# defining the "Game" as a class
class QuizGame:
    def __init__(self, font, draw_text, Button, state):
        self.font = font
        self.draw_text = draw_text
        self.Button = Button
        self.state = state
        self.buttons = []
        self.selected_index = None
        self.feedback_start = 0
        self.feedback_duration = 1.5  # seconds

        # Fonts
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.question_font = pygame.font.SysFont("arial", 36, bold=True)
        self.button_font = pygame.font.SysFont("arial", 28)

        # Background (which is AI generated)
        self.quiz_bg = pygame.image.load("Images/quiz bg.png").convert()
        self.quiz_bg = pygame.transform.scale(self.quiz_bg, (1000, 1000))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.selected_index is None:  # only allows clicks if not waiting for feedback. Makes it feel smoother.
                for b in self.buttons:
                    if b.rect.collidepoint(event.pos):
                        self.selected_index = b.answer_index
                        self.feedback_start = time.time()
                        self.check_answer(b.answer_index)
                        break

    def check_answer(self, user_answer_index):
        x = self.state["current_q"]
        if x < len(questions):
            correct_answer_index = questions[x]["correct"]
            if user_answer_index == correct_answer_index:
                self.state["score"] += 1
            else:
                self.state["score"] -= 1

    def update(self, win):
        # Draws the background
        if self.quiz_bg:
            win.blit(self.quiz_bg, (0, 0))
        else:
            win.fill((200, 200, 200))
        x = self.state["current_q"]
        if x < len(questions):
            q = questions[x]

            # Question text
            self.draw_text(f"Question {x + 1}:", 140, (0, 0, 0), align='center', font_override=self.title_font)
            self.draw_text(q["q"], 300, (0, 0, 0), align='center', font_override=self.question_font)

            # Score display
            self.draw_text(f"Score: {self.state['score']}", 50, (0, 0, 0), align='left', font_override=self.button_font)

            # Creates buttons
            self.buttons = []
            button_width = 400
            button_height = 60
            start_y = 500

            for i, a in enumerate(q["a"]):
                button_x = (win.get_width() - button_width) // 2
                button_y = start_y + i * (button_height + 20)

                # Default color
                button_color = (70, 130, 180)

                # If feedback is active, color the selected button
                if self.selected_index is not None and i == self.selected_index:
                    correct_index = q["correct"]
                    if self.selected_index == correct_index:
                        button_color = (50, 205, 50)  # green
                    else:
                        button_color = (220, 20, 60)  # red

                button = self.Button(
                    a,
                    button_x,
                    button_y,
                    button_width,
                    button_height,
                    None,
                    color=button_color,
                    text_color=(255, 255, 255),
                    font_override=self.button_font
                )
                button.answer_index = i
                button.draw(win)
                self.buttons.append(button)

            # If feedback time passed, it goes to next question
            if self.selected_index is not None:
                if time.time() - self.feedback_start > self.feedback_duration:
                    self.selected_index = None
                    self.state["current_q"] += 1
                    if self.state["current_q"] >= len(questions):
                        self.state["current_game"] = "menu"
                        self.state["message"] = "Quiz completed!"

        else:
            self.state["current_game"] = "menu"
            self.state["message"] = "Quiz completed!"
