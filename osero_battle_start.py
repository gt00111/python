import pygame

# 初期化
pygame.init()

# ウィンドウ作成
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("オセロ")

# マス設定
square_num = 8
square_size = screen_width // square_num

# FPS設定
FPS = 60
clock = pygame.time.Clock()

# 色の設定
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 盤面(黒:1 白:-1)
board = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, -1, 1, 0, 0, 0],
    [0, 0, 0, 1, -1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

# プレイヤー
player = 1

vec_table = [
    (-1, -1), # 左上
    (0, -1), #上
    (1, -1), # 右上
    (-1, 0), #左
    (1, 0), #右
    (-1, 1), # 左下
    (0, 1), #下
    (1, 1) # 右下
]


game_over = False
pass_num = 0

# フォントの設定
font = pygame.font.SysFont(None, 100, bold=False, italic=False)
button_font = pygame.font.SysFont(None, 50)
title_font = pygame.font.SysFont(None, 80, bold=True)

Your_win_surface = font.render("Your Win!", False, BLACK, RED)
Your_loss_surface = font.render("Your loss!", False, WHITE, RED)
draw_surface = font.render("Draw...", False, BLUE, RED)
reset_surface = font.render("Click to reset!", False, BLACK, RED)

cpu_depth = 3 
selected_difficulty = "Normal"


#関数_______________________________________________________________________

# グリッド線描画
def draw_grid():
    for i in range(square_num):
        # 横線
        pygame.draw.line(screen, BLACK, (0, i * square_size), (screen_width, i * square_size), 3)
        # 縦線
        pygame.draw.line(screen, BLACK, (i * square_size, 0), (i * square_size, screen_height), 3)

# 盤面の描画
def draw_board():       
    for row_index, row in enumerate(board):
        for col_index, col in enumerate(row):
            if col == 1:
                pygame.draw.circle(screen, BLACK, (col_index * square_size + 50, row_index * square_size + 50), 45)
            elif col == -1:
                pygame.draw.circle(screen, WHITE, (col_index * square_size + 50, row_index * square_size + 50), 45)
                
# 石が置ける場所の取得
def get_valid_position():
    valid_position_list = []
    for row in range(square_num):
        for col in range(square_num):
            #　石を置いていないマスのチェック
            if board[row][col] == 0:
                for vx, vy in vec_table:
                    x = vx + col
                    y = vy + row
                    # マスの範囲内かつプレイヤーの石と異なる石があり場合、その方向に引き続きチェック
                    if  0 <= x < square_num and 0 <= y < square_num and board[y][x] == -player:
                        while True:
                            x += vx
                            y += vy
                            # プレイヤーの石と異なる色がある場合は、その方向を引き続きチェック
                            if  0 <= x < square_num and 0 <= y < square_num and board[y][x] == -player:
                                continue
                            # プレイヤーの石と同色の石がある場合、石が置けるためインデックスを保存
                            elif 0 <= x < square_num and 0 <= y < square_num and board[y][x] == player:
                                valid_position_list.append((col, row))
                                break
                            else:
                                break
    return valid_position_list

# 石をひっくり返す
def flip_pieces(col, row):
    for vx, vy in vec_table:
        flip_list = []
        x = vx + col
        y = vy + row
        while 0 <= x < square_num and 0 <= y < square_num and board[y][x] == -player:
            flip_list.append((x, y))
            x += vx
            y += vy
            if 0 <= x < square_num and 0 <= y < square_num and board[y][x] == player:
                for flip_x, flip_y in flip_list:
                    board[flip_y][flip_x] = player
                    
# 評価関数：CPUにとって有利な局面ほど高いスコアを返す
def evaluate_board():
    score = 0
    for row in range(square_num):
        for col in range(square_num):
            # CPU（白）の石
            if board[row][col] == -1:
                score += 1
            # プレイヤー（黒）の石
            elif board[row][col] == 1:
                score -= 1

    # 角のスコアを高くする（強化ポイント）
    corners = [(0,0), (0,7), (7,0), (7,7)]
    for x, y in corners:
        # CPUが角を取った
        if board[y][x] == -1:
            score += 5
        # プレイヤーが角を取った
        elif board[y][x] == 1:
            score -= 5

    return score


def minimax(depth, maximizing_player, alpha, beta):
    valid_moves = get_valid_position()
    
    # ゲームオーバー、または指定した探索の深さに到達したら評価関数を返す
    if depth == 0 or len(valid_moves) == 0:
        return evaluate_board()
    
    # CPUの手番（最大化）
    if maximizing_player:  
        max_eval = float('-inf')
        for x, y in valid_moves:
            # 盤面のコピー
            temp_board = [row[:] for row in board]
            # 石をひっくり返す
            flip_pieces(x, y)
            # CPUの手を打つ
            board[y][x] = -1

            # 相手のターン
            eval = minimax(depth - 1, False, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)

            # 盤面を元に戻す
            board[:] = temp_board

            # α-β剪定
            if beta <= alpha:
                break
        return max_eval
    else:
        # プレイヤーの手番（最小化）
        min_eval = float('inf')
        for x, y in valid_moves:
            temp_board = [row[:] for row in board]
            flip_pieces(x, y)
            # プレイヤーの手を打つ
            board[y][x] = 1

            eval = minimax(depth - 1, True, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            
            # 盤面を元に戻す
            board[:] = temp_board

            # α-β剪定
            if beta <= alpha:
                break
        return min_eval

                    
# cpuが最適な手を選ぶ関数               
def cpu_move():
    best_score = float('-inf')
    best_move = None
    valid_moves = get_valid_position()

    for x, y in valid_moves:
        temp_board = [row[:] for row in board]
        flip_pieces(x, y)
        # CPUの手を試す
        board[y][x] = -1
        # 3手先を読む　minimax(3, False, float('-inf'), float('inf'))第一引数変更で強さ変更
        move_score = minimax(cpu_depth, False, float('-inf'), float('inf'))
        if move_score > best_score:
            best_score = move_score
            best_move = (x, y)
        # 盤面を元に戻す
        board[:] = temp_board

    if best_move:
        x, y = best_move
        flip_pieces(x, y)
        # CPUが実際に石を置く
        board[y][x] = -1
        
# 選択した難易度の背景色を黄色に        
def render_buttons(easy_rect, normal_rect, hard_rect):
    global selected_difficulty
    colors = {"Easy": WHITE, "Normal": WHITE, "Hard": WHITE}
    colors[selected_difficulty] = YELLOW  # 選択した難易度の背景色を黄色に
    
    easy_surface = button_font.render("Easy", True, BLACK, colors["Easy"])
    normal_surface = button_font.render("Normal", True, BLACK, colors["Normal"])
    hard_surface = button_font.render("Hard", True, BLACK, colors["Hard"])
    # 背景をリセットして重なりを防ぐ
    screen.blit(easy_surface, easy_rect.topleft)
    screen.blit(normal_surface, normal_rect.topleft)
    screen.blit(hard_surface, hard_rect.topleft)
    pygame.display.update()

def show_start_screen():
    global cpu_depth, selected_difficulty
    screen.fill(GREEN)
    
    title_surface = title_font.render("The Othello", True, WHITE)
    screen.blit(title_surface, (screen_width//2 - 180, 200))

    button_surface = button_font.render("START", True, BLACK, YELLOW)
    button_rect = button_surface.get_rect(center=(screen_width//2, 400))
    screen.blit(button_surface, button_rect.topleft)
    
    easy_rect = pygame.Rect(screen_width//2 - 200, 500, 100, 50)
    normal_rect = pygame.Rect(screen_width//2 - 60, 500, 100, 50)
    hard_rect = pygame.Rect(screen_width//2 + 120, 500, 100, 50)
    
    render_buttons(easy_rect, normal_rect, hard_rect)
    
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if button_rect.collidepoint(mx, my):
                    waiting = False
                elif easy_rect.collidepoint(mx, my):
                    cpu_depth = 2
                    selected_difficulty = "Easy"
                elif normal_rect.collidepoint(mx, my):
                    cpu_depth = 3
                    selected_difficulty = "Normal"
                elif hard_rect.collidepoint(mx, my):
                    cpu_depth = 5
                    selected_difficulty = "Hard"
                    
                screen.fill(GREEN)  # 背景を再描画
                screen.blit(title_surface, (screen_width//2 - 180, 200))  # タイトルを再描画
                screen.blit(button_surface, button_rect.topleft)  # スタートボタンを再描画
                render_buttons(easy_rect, normal_rect, hard_rect)
                pygame.display.update()

# タイトル画面__________________________________________________________________
# スタート画面を表示
show_start_screen()

# メインループ__________________________________________________________________
run = True
while run:
    # 背景の塗りつぶし
    screen.fill(GREEN)
    
    # グリッド線描画
    draw_grid()
    
    # 盤面の描画
    draw_board()
    
    # 石が置ける場所の取得
    valid_position_list = get_valid_position()
    # 石が置ける場所の取得(黄色丸)
    for x, y in valid_position_list:
        pygame.draw.circle(screen, YELLOW, (x * square_size + 50, y * square_size + 50), 45, 3)
    
    #石が置ける場所がない場合、パス
    if len(valid_position_list) < 1:
        player *= -1
        pass_num += 1
        
    # ゲームオーバー判定
    if pass_num > 1 :
        pass_num = 2
        game_over = True
    
    # 勝敗チェック
    black_num = 0
    white_num = 0
    if game_over:
        black_num = sum(row.count(1) for row in board)
        white_num = sum(row.count(-1) for row in board)

        if black_num > white_num:
            screen.blit(Your_win_surface, (230, 200))
        elif black_num < white_num:
            screen.blit(Your_loss_surface, (230, 200))
        else:
            screen.blit(draw_surface, (280, 200))
            
        screen.blit(reset_surface, (180, 400))
        
    # イベントの取得
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
        # マウスクリック
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over == False:
                mx, my = pygame.mouse.get_pos()
                x = mx // square_size
                y = my // square_size
                if board[y][x] == 0 and (x, y) in valid_position_list:
                    #石をひっくり返す
                    flip_pieces(x, y)
                    board[y][x] = player
                    player *= -1
                    pass_num = 0
                    
                    # 🎯 CPUの手番を追加（プレイヤーの手の後に CPU が動く）
                    pygame.time.delay(500)  
                    # 0.5秒待機（プレイヤーの動きを見やすくする）
                    cpu_move()
                    # CPUの手が終わったら再びプレイヤーのターン
                    player *= -1
            else:
                show_start_screen()
                board = [
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, -1, 1, 0, 0, 0],
                    [0, 0, 0, 1, -1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0]
                ]
                player = 1
                game_over = False
                pass_num = 0

    # 更新
    pygame.display.update()
    clock.tick(FPS)
# ___________________________________________________________________________

pygame.quit()
