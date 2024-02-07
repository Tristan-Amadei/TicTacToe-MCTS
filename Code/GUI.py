import pygame
from Board import Board, direction
from threading import Thread
from MCTS import play_mcts

pygame.font.init()
pygame.init()

def player_color(player):
    color_blood_red = (136, 8, 8)
    color_blue = (60, 60, 190)
    if player == 1:
        return color_blood_red
    elif player == -1:
        return color_blue

def winning_color(gameState):
    color_red = (255, 0, 0)
    color_blue = (0, 0, 255)
    if gameState == 1:
        return color_red
    elif gameState == -1:
        return color_blue
    return (0, 0, 0)

def draw_cell(win, i, j, board, width, height, player_string):
    fnt = pygame.font.SysFont("comicsans", 120)
    gap = width / 3
    x = j * gap
    y = i * gap

    if board.grid[i][j] == 0:
        return
    
    text = fnt.render(board.display_player_name(board.grid[i][j]), 
                                                1, player_color(board.grid[i][j]))
    win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))

def draw_selected_cell(win, selected, width):
    if selected[0] == -1 or selected[1] == -1:
        #no square is currently selected
        return
    
    gap = width / 3
    x = selected[1] * gap
    y = selected[0] * gap
    pygame.draw.rect(win, (255,0,0), (x,y, gap ,gap), 3)

def draw(win, board, width, height, player_string):
    gap = width / 3
    for i in range(3+1):
        thick = 4
        pygame.draw.line(win, (0,0,0), (0, i*gap), (width, i*gap), thick)
        pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, gap*3), thick)

    for i in range(3):
        for j in range(3):
            draw_cell(win, i, j, board, width, height, player_string)

def draw_window_selection_screen(win, board, width, height, selected):
    win.fill((255,255,255))
    # Draw player
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Player Selection: ", 1, (0,0,0))
    win.blit(text, (10, height-text.get_height()-12.5))

    fnt = pygame.font.SysFont("comicsans", 60)
    text_X = fnt.render("X", 1, player_color(1))
    win.blit(text_X, (text.get_width()+50, height-text.get_height()-30))
    text_O = fnt.render("O", 1, player_color(-1))
    win.blit(text_O, (text.get_width()+text_X.get_width()+100, height-text.get_height()-30))

    fnt = pygame.font.SysFont("comicsans", 20)
    text_choose = fnt.render("(Click to choose)", 1, (0,0,0))
    win.blit(text_choose, (width-10-text_choose.get_width(), height-text.get_height()-5))

    # Draw grid and board
    draw(win, board, width, height, "") # as the board is still empty, we don't care about the player_string parameter

    # Draw square around the selected cell
    draw_selected_cell(win, selected, width)

def redraw_window(win, board, width, height, player, player_string, selected, engine):
    win.fill((255,255,255))
    # Draw player
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Player: ", 1, (0,0,0))
    win.blit(text, (10, height-text.get_height()-12.5))
    text_player = fnt.render(player_string, 1, player_color(player))
    win.blit(text_player, (text.get_width()+10, height-text.get_height()-10))

    # Draw grid and board
    draw(win, board, width, height, player_string)

    # Draw square around the selected cell
    draw_selected_cell(win, selected, width)

    #Draw lines to show the winner
    draw_winner(win, board, width, height)
    
    #display the text reading that the engine is running
    if engine:
        draw_engine_search_text(win, width, height)
        
    #display a text explaining how to make a move, only displaying it when no move has been played
    if len(board.moves) == 0:
        draw_instruction_text(win, width, height)

def click_square(mouse_pos, selected, width, height, board, player):
    gap = width / 3
    if mouse_pos[0] < width and mouse_pos[1] < height:
        x = int(mouse_pos[0] // gap)
        y = int(mouse_pos[1] // gap)
        if selected[0] == y and selected[1] == x:
            #the square was already selected, selecting it again means we want to play on there
            try:
                board.play(y, x, player)
                selected[0] = -1
                selected[1] = -1
                return True
            except:
                selected[0] = -1
                selected[1] = -1
                return False
        else:
            selected[0] = y
            selected[1] = x
            return False

def player_selection(mouse_pos, width, height):

    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Player Selection: ", 1, (0,0,0))
    text_X = fnt.render("X", 1, player_color(1))
    text_O = fnt.render("O", 1, player_color(-1))

    x = mouse_pos[0]
    y = mouse_pos[1]
    if height-text.get_height()-30-text.get_height() <= y and y <= height:
        if text.get_width()+40 <= x and x <= text.get_width()+50+text_X.get_width()+30:
            return 1
        if text.get_width()+50+text_X.get_width()+50 < x and x <= text.get_width()+50+text_X.get_width()+50+text_O.get_width()+30:
            return -1
    return 0

def draw_winner(win, board, width, height):
    gap = width / 3
    if board.winningMove != None:
        fnt = pygame.font.SysFont("comicsans", 40)
        text = fnt.render(f"Player {board.display_player_name(board.gameState)} wins!", 1, (0,0,0))
        win.blit(text, (width - text.get_width()-10, height-text.get_height()-15))

        (i, j), dir = board.winningMove
        color = winning_color(board.gameState)
        if dir == direction.ROW:
            pygame.draw.line(win, color, (gap/2, i*gap + gap/2), 
                                           (width - gap / 2, i*gap + gap / 2), 6)
        if dir == direction.COL:
            pygame.draw.line(win, color, (j*gap + gap/2, gap/2), 
                                           (j*gap + gap / 2, width - gap / 2), 6)
        if dir == direction.DIAG_TOP_BOTTOM:
            pygame.draw.line(win, color, (gap/2, gap/2), 
                                           (width - gap / 2, width - gap / 2), 6)
        if dir == direction.DIAG_BOTTOM_TOP:
            pygame.draw.line(win, color, (width - gap/2, gap/2), 
                                           (gap / 2, width - gap / 2), 6)
    elif len(board.moves) == 9:
        fnt = pygame.font.SysFont("comicsans", 40)
        text = fnt.render(f"Draw Game", 1, (0,0,0))
        win.blit(text, (width - text.get_width()-10, height-text.get_height()-15))
        
def draw_engine_search_text(win, width, height):
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Engine running...", 1, (0,0,0))
    win.blit(text, (width-10-text.get_width(), height-text.get_height()-5))
    
def draw_instruction_text(win, width, height):
    fnt = pygame.font.SysFont("comicsans", 20)
    text = fnt.render("To play, double-click on a square", 1, (0,0,0))
    win.blit(text, (width-10-text.get_width(), height-text.get_height()-5))


def main():
    screenInfo = pygame.display.Info()
    width = 0.4*screenInfo.current_w
    height = 0.8*screenInfo.current_h
    win = pygame.display.set_mode((width,height))
    pygame.display.set_caption("Tic-Tac-Toe")

    run = True
    boardInitialized = False
    engine_running = False

    while run:
        while run and not boardInitialized:
            board = Board()
            player = 0
            selected = [-1, -1]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    player = player_selection(mouse_pos, width, height)

                            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            draw_window_selection_screen(win, board, width, height, selected)
            pygame.display.update()

            if player != 0:
                player_string = "X" if player == 1 else "O"
                opponent = -1 if player == 1 else 1
                boardInitialized = True

        ## player selection is over, now we play

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                move_was_played = click_square(mouse_pos, selected, width, height, board, player)
                if move_was_played and not board.isGameOver():
                    engine_running = True
                    
                    thread = Thread(target=play_mcts, args=(board, opponent, 100, 1.4))
                    
                    thread.start()  
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    board.undo_last_move()   

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        try:
            engine_running = thread.is_alive()
        except:
            engine_running = False
            
        redraw_window(win, board, width, height, player, player_string, selected, engine_running)
        pygame.display.update()

main()