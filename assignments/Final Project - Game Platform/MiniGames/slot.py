import pygame
import random


class SlotGame:
    def __init__(self, font, Button, state):
        self.font = font
        self.Button = Button
        self.state = state
        self.symbols = ['+', '*', '#', '@', '$']
        self.reels = ["?", "?", "?"]
        self.bet_amount = 1
        self.message = "Place your bet and spin!"
        self.spinning = False
        self.spin_timer = 0
        self.spin_duration = 60  # frames
        self.reel_stops = [False, False, False]
        self.spin_delay = 10  # frames between reel stops

        # UI buttons
        self.bet_up_button = Button("+", 450, 450, 40, 40, self.bet_up)
        self.bet_down_button = Button("-", 510, 450, 40, 40, self.bet_down)
        self.spin_button = Button("Spin", 425, 520, 150, 40, self.spin)
        self.exit_button = Button("Exit", 425, 580, 150, 40, self.exit_game)

    def start_game(self):
        self.message = "Place your bet and spin!"
        self.reels = ["?", "?", "?"]

    def bet_up(self):
        self.bet_amount += 1
        if self.bet_amount > self.state.get("balance", 0):
            self.bet_amount = self.state.get("balance", 0)

    def bet_down(self):
        self.bet_amount -= 1
        if self.bet_amount < 1:
            self.bet_amount = 1

    def spin(self):
        if not self.spinning and self.state.get("balance", 0) >= self.bet_amount:
            self.state["balance"] -= self.bet_amount
            self.spinning = True
            self.spin_timer = 0
            self.reel_stops = [False, False, False]
            self.reels = ["Spinning", "Spinning", "Spinning"]
            self.message = "Spinning..."
        elif self.state.get("balance", 0) < self.bet_amount:
            self.message = "Not enough balance!"

    def exit_game(self): # self explanatory.
        self.state["current_game"] = "menu"

    def handle_event(self, event):
        # checks for clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bet_up_button.click(event.pos)
            self.bet_down_button.click(event.pos)
            self.spin_button.click(event.pos)
            self.exit_button.click(event.pos)

    def update(self, win):
        # Draws background and balance
        win.fill((0, 0, 0))
        balance_text = self.font.render(f"Balance: ${self.state.get('balance', 0)}", True, (255, 255, 255))
        balance_text_rect = balance_text.get_rect(center=(500, 200))
        win.blit(balance_text, balance_text_rect)

        # Draws message
        message_text = self.font.render(self.message, True, (255, 255, 255))
        message_rect = message_text.get_rect(center=(500, 350))
        win.blit(message_text, message_rect)

        if self.spinning:
            self.spin_timer += 1
            if not self.reel_stops[0] and self.spin_timer >= self.spin_duration:
                self.reels[0] = random.choice(self.symbols)
                self.reel_stops[0] = True
            if not self.reel_stops[1] and self.spin_timer >= self.spin_duration + self.spin_delay:
                self.reels[1] = random.choice(self.symbols)
                self.reel_stops[1] = True
            if not self.reel_stops[2] and self.spin_timer >= self.spin_duration + (self.spin_delay * 2):
                self.reels[2] = random.choice(self.symbols)
                self.reel_stops[2] = True
                self.spinning = False
                payout = self.get_payout(self.reels, self.bet_amount)
                self.state["balance"] += payout
                if payout > 0:
                    self.message = f"You won ${payout}! Congrats."
                else:
                    self.message = "Sorry, you lost this round. Gambling is a pain innit?"

        # Draw the reels
        for i, symbol in enumerate(self.reels):
            reel_text = self.font.render(symbol, True, (255, 255, 255))
            reel_rect = reel_text.get_rect(center=(400 + i * 100, 300))
            win.blit(reel_text, reel_rect)

        # Bet amount:
        bet_text = self.font.render(f"Bet: {self.bet_amount}", True, (255, 255, 255))
        bet_text_rect = bet_text.get_rect(center=(500, 420))
        win.blit(bet_text, bet_text_rect)

        # Buttons:
        self.bet_up_button.draw(win)
        self.bet_down_button.draw(win)
        self.spin_button.draw(win)
        self.exit_button.draw(win)

    def get_payout(self, row, bet):
        if row[0] == row[1] == row[2]:
            if row[0] == '+': return bet * 10  # Jackpot
            if row[0] == '*': return bet * 8
            if row[0] == '#': return bet * 6
            if row[0] == '@': return bet * 4
            if row[0] == '$': return bet * 2

        # Two matching symbols
        if row[0] == row[1] or row[1] == row[2] or row[0] == row[2]:
            return bet

        return 0

# Inspiration and Credits to: