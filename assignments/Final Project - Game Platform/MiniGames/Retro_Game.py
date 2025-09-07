import pygame
import random


def start_retro_game(win, font, clock, WIDTH, HEIGHT, FPS, state):
    # Loads and scales the player image

    player_image = pygame.image.load('Images/ship.png').convert_alpha()
    player_image = pygame.transform.scale(player_image, (60, 60))

    # Positions the player rect.
    player = player_image.get_rect(center=(WIDTH // 2, HEIGHT - 60))

    # Loads and rotates the comet image, so that it looks good.
    comet_image = pygame.image.load('Images/Comet.png').convert_alpha()
    comet_image = pygame.transform.scale(comet_image, (30, 30))  # Adjust size as needed
    comet_image = pygame.transform.rotate(comet_image, -45)  # Rotate by 45 degrees

    # Replaces blocks with comet-based rects
    blocks = [pygame.Rect(random.randint(0, WIDTH - 40), random.randint(-600, -50), 40, 40) for _ in range(5)]
    retro_score = 0
    running = True
    speed = 5
    difficulty_level = 0

    # Checkpoints to ensure score bonuses are only awarded once. Had to find out the hard way and then added this.
    score_50_awarded = False
    score_100_awarded = False
    score_150_awarded = False

    # Loading and scaling the background image
    background_image = pygame.image.load('Images/retro bg.jpg').convert_alpha()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    background_image.set_alpha(50)

    # Setting variables
    start_time = pygame.time.get_ticks()
    countdown_duration = 5
    show_instructions = True
    game_over = False

    while running:
        win.blit(background_image, (0, 0))

        # Events / Quitting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    state["current_game"] = "menu"

            # Handle button clicks in the game over-state
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if main_menu_button.collidepoint(event.pos):
                    state["current_game"] = "menu"
                    return

        # Countdown and instruction logic
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) / 1000
        remaining_time = countdown_duration - int(elapsed_time)

        if show_instructions:
            # Displays instructions
            instructions_text = [
                "Controls: Use the arrow keys to move.",
                "Goal: Avoid the comets.",
                "Try to reach 200 points!",
                f"Starting in: {remaining_time}"
            ]

            for i, line in enumerate(instructions_text):
                instruction_surf = font.render(line, True, (255, 255, 255))
                instruction_rect = instruction_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60 + i * 40))
                win.blit(instruction_surf, instruction_rect)

            if remaining_time <= 0:
                show_instructions = False

        elif not game_over:
            # Game controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: player.x -= 5
            if keys[pygame.K_RIGHT]: player.x += 5
            if keys[pygame.K_UP]: player.y -= 5
            if keys[pygame.K_DOWN]: player.y += 5
            player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

            for block in blocks:
                block.y += speed
                if player.colliderect(block):
                    state["score"] -= 1
                    state["message"] = "You lost!"

                    # Deducts score if the performance was not enough
                    if retro_score < 50:
                        state["score"] -= 1
                    state["current_game"] = "end"
                    return

                if block.y > HEIGHT:
                    block.y = random.randint(-100, -50)
                    block.x = random.randint(0, WIDTH - 40)
                    retro_score += 1

            # Checks for score and win-condition
            if retro_score >= 200:
                game_over = True
            elif retro_score >= 50 and not score_50_awarded:
                state["score"] += 1
                score_50_awarded = True
            elif retro_score >= 100 and not score_100_awarded:
                state["score"] += 1
                score_100_awarded = True
            elif retro_score >= 150 and not score_150_awarded:
                state["score"] += 1
                score_150_awarded = True

            # Increases difficulty-level every 10 points
            new_difficulty_level = retro_score // 10
            if new_difficulty_level > difficulty_level:
                difficulty_level = new_difficulty_level
                speed += 0.25  # Increases speed every level
                blocks.append(
                    pygame.Rect(random.randint(0, WIDTH - 40), random.randint(-600, -50), 40, 40))  # Add a new block with each new level

            # Draws the player image
            if player_image:
                win.blit(player_image, player)

            # Draws the comet image
            for block in blocks:
                win.blit(comet_image, block)


            score_surf = font.render(f"Score: {retro_score} / 200", True, (255, 255, 255))
            win.blit(score_surf, (10, 10))

        else:  # Game over
            # Displays Victory text
            victory_font = pygame.font.Font(None, 80)
            victory_text_surf = victory_font.render("Victory!", True, (0, 255, 0))
            victory_text_rect = victory_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            win.blit(victory_text_surf, victory_text_rect)

            # Draws Main Menu button
            main_menu_text_surf = font.render("Main Menu", True, (255, 255, 255))
            main_menu_button = main_menu_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            pygame.draw.rect(win, (100, 100, 100), main_menu_button.inflate(20, 10))
            win.blit(main_menu_text_surf, main_menu_button)

        pygame.display.flip()
        clock.tick(FPS)