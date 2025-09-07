import pygame

ascii_art = {
    "Dog": r"""
   ,_____ ,
  ,._ ,_. 7\
 j `-'     /
 |o_, o    \
.`_y_`-,'   !
|/   `, `._ `-,
|_     \   _.'*\
  >--,-'`-'*_*'``---.
  |\_* _*'-'         '
 /    `               \
 \.         _ .       /
  '`._     /   )     /
   \  |`-,-|  /c-'7 /
    ) \ (_,| |   / (_
   ((_/   ((_;)  \_)))       -nabis
""",
    "Cat": r"""
Art by Hayley Jane Wakenshaw
    _..---...,""-._     ,/}/)
 .''        ,      ``..'(/-<
/   _      {      )         \ 
;   _ `.     `.   <         a(
,'   ( \  )      `.  \ __.._ .: y
(  <\_-) )'-.____...\  `._   //-'
 `. `-' /-._)))      `-._)))
   `...'         hjw
""",
    "Elephant": r"""
Art by Joan G. Stark
                        _
                      .' `'.__
                     /      \ `'"-,
    .-''''--...__..-/ .     |      \
  .'               ; :'     '.  a   |
 /                 | :.       \     =\
;                   \':.      /  ,-.__;.-;`
/|     .              '--._   /-.7`._..-;`
; |       '                |`-'      \  =|
|/\        .   -' /     /  ;         |  =/
(( ;.       ,_  .:|     | /     /\   | =|
 ) / `\     | `""`;     / |    | /   / =/
   | ::|    |      \    \ \    \ `--' =/
  /  '/\    /       )    |/     `-...-`
 /    | |  `\    /-'    /;
 \  ,,/ |    \   D    .'  \
jgs `""`   \  nnh  D_.-'L__nnh
""",
    "Owl": r"""
, _ ,
( o o )
/'` ' `'\\
|'''''''|
|\\'''//|
   HHH
""",
    "Dolphin": r"""
                                       .--.
                _______             .-"  .'
        .---u"""       """"---._  ."    %
      .'                        "--.    %
 __.--'  o                          "".. "
(____.                                  ":
 `----.__                                 ".
         `----------__                     ".
               ".   . ""--.                 ".
                 ". ". bIt ""-.              ".
                   "-.)        ""-.           ".
                                   "".         ".
                                      "".       ".
                                         "".      ".
                                            "".    ".
                      ^~^~^~^~^~^~^~^~^~^~^~^~^"".  "^~^~^~^~^
                                            ^~^~^~^  ~^~
                                                 ^~^~^~
"""
}


class AsciiArtGame:
    def __init__(self, font, draw_text, Button, state):
        self.font = font
        self.draw_text = draw_text
        self.Button = Button
        self.state = state
        self.selected_animal = None
        # Fonts for displaying text on the screen.
        self.title_font = pygame.font.SysFont("consolas", 20)
        # Loads and sets up the background image.
        self.background_image = pygame.image.load("Images/nature.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (1000, 1000))
        # Makes the image semi-transparent.
        self.background_image.set_alpha(128)


        # Creates a list of buttons for each animal and the "Back" button.
        self.buttons = [
            self.Button("Dog", 50, 850, 120, 40, lambda: self.select_animal("Dog")),
            self.Button("Cat", 200, 850, 120, 40, lambda: self.select_animal("Cat")),
            self.Button("Elephant", 350, 850, 120, 40, lambda: self.select_animal("Elephant")),
            self.Button("Owl", 500, 850, 120, 40, lambda: self.select_animal("Owl")),
            self.Button("Dolphin", 650, 850, 120, 40, lambda: self.select_animal("Dolphin")),
            self.Button("Back", 850, 850, 120, 40, lambda: self.state.__setitem__("current_game", "menu"))
        ]

    def select_animal(self, animal):
        # Sets the selected animal when a button is clicked.
        self.selected_animal = animal

    def handle_event(self, event):
        # Checks if a mouse button was clicked.
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Goes through each button to see if it was clicked.
            for b in self.buttons:
                if b.rect.collidepoint(event.pos):
                    # Calls the button's function if it was clicked.
                    b.callback()

    def update(self, win):
        # Draws the background image first.
        if self.background_image:
            win.blit(self.background_image, (0, 0))

        # Creates a semi-transparent surface for the "whiteboard" area.
        whiteboard_surface = pygame.Surface((900, 750), pygame.SRCALPHA)
        pygame.draw.rect(whiteboard_surface, (255, 255, 255, 128), whiteboard_surface.get_rect())
        # Draws the whiteboard onto the main window.
        win.blit(whiteboard_surface, (50, 50))

        # Checks if an animal has been selected.
        if self.selected_animal:
            # Gets the ASCII art for the selected animal and splits it into separate lines.
            art = ascii_art[self.selected_animal].strip("\n").split("\n")

            # Calculates the height needed to display all lines of the art.
            line_height = self.title_font.get_height()
            block_height = len(art) * line_height

            # Finds the starting y-position to center the art vertically.
            start_y = 50 + (750 - block_height) // 2

            # Finds the widest line to center the art horizontally.
            max_width = max(self.title_font.size(line)[0] for line in art)
            start_x = 50 + (900 - max_width) // 2

            # Draws each line of the ASCII art onto the screen.
            for i, line in enumerate(art):
                text_surface = self.title_font.render(line, True, (0, 0, 0))
                win.blit(text_surface, (start_x, start_y + i * line_height))

        # Draws all the buttons at the bottom of the screen.
        for b in self.buttons:
            b.draw(win)
