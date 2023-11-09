import pygame
from collections import deque
from pygame.locals import *
import random
import tkinter as tk
from tkinter import filedialog
import threading
import heapq
import time

WIDTH2, HEIGHT2 = 700, 520
WIDTH, HEIGHT = 450, 450
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BACKGROUND_COLOR = (192, 192, 192)

pygame.init()
screen = pygame.display.set_mode((WIDTH2, HEIGHT2))
pygame.display.set_caption("Trò chơi 8-puzzle sử dụng thuật toán")

font = pygame.font.Font(None, 36)

class PuzzleNode: #nut trong cay tim kiem
    def __init__(self, puzzle, parent=None): ##khởi tạo một thể hiện của lớp PuzzleNode
        self.puzzle = puzzle  #trạng thái hiện tại của câu đố đang được giải 
        self.parent = parent #trỏ đến nút trước đó trong cây tìm kiếm, đại diện cho trạng thái trước đó
#đại diện cho một nút trong cây tìm kiếm để giải câu đố. Mỗi nút chứa trạng thái câu đố, một tham chiếu đến nút cha của nó
class PuzzleNodeID:
    def __init__(self, puzzle, parent=None):
        self.puzzle = puzzle
        self.parent = parent
        self.g = 0  
        self.h = 0 

    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)
 #Biến nút
bfs_button = None
dfs_button = None
id_button = None 
ucs_button = None 
shuffle_button = None
reset_button = None 
play_button = None
solution=None

#luu tru nut mo rong
bfs_expanded_nodes = 0
dfs_expanded_nodes = 0
id_expanded_nodes =0 
ucs_expand_node =0 
file_path = "image.png"
your_image = "image.png"
initial_state = [2, 6, 5, 0, 8, 7, 4, 3, 1]
goal_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
current_state=initial_state
depth_limit = 25

#kiểm tra xem một nước đi cho trước có hợp lệ hay không
#empty_index: Chỉ số của ô trống trong trạng thái câu đố.
#block_index: Chỉ số của khối đang được di chuyển
def is_move_valid(empty_index, block_index):
    row_diff = abs(empty_index // 3 - block_index // 3) # tính toán sự khác biệt tuyệt đối về hàng giữa ô trống và khối đang được di chuyển
    col_diff = abs(empty_index % 3 - block_index % 3) #tính toán sự khác biệt tuyệt đối về cột giữa ô trống và khối đang được di chuyển
    return row_diff + col_diff == 1 #Dòng này trả về một giá trị boolean cho biết liệu tổng của sự khác biệt về hàng và cột có bằng 1 hay không
#di chuyển khối 
def move_block(puzzle, empty_index, block_index):
    puzzle[empty_index], puzzle[block_index] = puzzle[block_index], puzzle[empty_index]
#Mã này kiểm tra xem trạng thái hiện tại của câu đố có khớp với trạng thái mục tiêu hay không
def is_game_solved(puzzle, goal_state):
    return puzzle == goal_state
#Nó xử lý sự tương tác của người dùng bằng chuột và bàn phím, đồng thời quản lý trạng thái trò chơi tương ứng.
#empty_index: Lưu trữ vị trí của ô trống trong câu đố.
#step_count: Lưu trữ số bước di chuyển đã thực hiện.
#solved: Là cờ chỉ ra liệu câu đố đã được giải hay chưa.
#winner_displayed: Là cờ chỉ ra liệu thông báo người thắng đã được hiển thị hay chưa.
#should_exit: Là cờ chỉ ra liệu trò chơi nên thoát hay không.
#start_time: Lưu trữ thời gian bắt đầu trò chơ
def handle_mouse_movement(puzzle, image_blocks, goal_state): 
    global current_state
    empty_index = puzzle.index(0)
    step_count = 0
    solved = False
    winner_displayed = False
    should_exit = False 
    start_time = time.time()
    #Vòng lặp này chạy cho đến khi câu đố được giải hoặc người chơi muốn thoát khỏi trò chơi.
    while not solved and not should_exit:  
        font = pygame.font.Font(None, 36)  
        text = font.render("Press ESC to exit", True, (0, 0, 0))  
        text2 = font.render("Play Now", True, (0, 0, 0))  
        text_rect = text.get_rect(center=(580, HEIGHT -400)) 
        text2_rect = text2.get_rect(center=(580, HEIGHT -350)) 
        screen.blit(text, text_rect)  
        screen.blit(text2,text2_rect) 
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            #Nếu loại sự kiện là KEYDOWN và phím được nhấn là ESC, khối mã này đặt cờ should_exit thành True.
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                should_exit = True

            if event.type == MOUSEBUTTONDOWN:
                for i in range(1, 9):
                    #Nếu di chuyển hợp lệ, khối mã này di chuyển ô và cập nhật các biến empty_index và step_count
                    if is_move_valid(empty_index, puzzle.index(i)):
                        row, col = puzzle.index(i) // 3, puzzle.index(i) % 3
                        x = col * (WIDTH // 3)
                        y = row * (HEIGHT // 3)
                        block_rect = pygame.Rect(x, y, WIDTH // 3, HEIGHT // 3)
                        if block_rect.collidepoint(event.pos):
                            block_index = puzzle.index(i)
                            move_block(puzzle, empty_index, block_index)
                            empty_index = block_index
                            step_count += 1
                            current_state=puzzle
                            if is_game_solved(puzzle, goal_state):
                                solved = True
                                end_time=time.time()
                                draw_puzzle(puzzle, step_count, image_blocks,round(end_time-start_time,2),0)
                                

            if event.type == MOUSEMOTION:
                draw_puzzle(puzzle, step_count, image_blocks,0,0)
                pygame.display.flip()
        #Nếu trò chơi đã được giải và thông báo người thắng chưa được hiển thị, khối mã này vẽ câu đố, hiển thị thông báo người thắng và hiển thị hình ảnh ban đầu

        if solved and not winner_displayed:
            
            draw_puzzle(puzzle, step_count, image_blocks,round(end_time-start_time,2),0)
            font = pygame.font.Font(None, 72)
            text = font.render("Bạn đã thắng rồi !", True, (156, 112, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            winner_displayed = True
            
def iterative_deepening():
    global current_state, goal_state, depth_limit
    for depth_limit in range(1, depth_limit + 1):
        solution = depth_limited_search()
        if solution:
            return solution
        else:
            font = pygame.font.Font(None, 36)
            no_solution_text = font.render("No Solution !", True, (0, 0, 0))
            text_rect = no_solution_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(no_solution_text, text_rect)
            return None
def depth_limited_search():
    global current_state, goal_state, depth_limit,id_expanded_nodes
    open_set = [PuzzleNodeID(current_state)]
    closed_set = set()

    while open_set:
        current_node = heapq.heappop(open_set)
        id_expanded_nodes+=1

        if current_node.puzzle == goal_state:
            return reconstruct_path(current_node)

        if len(reconstruct_path(current_node)) >= depth_limit:
            continue

        closed_set.add(tuple(current_node.puzzle))

        for neighbor in get_neighbors(current_node.puzzle):
            if tuple(neighbor) in closed_set:
                continue

            neighbor_node = PuzzleNodeID(neighbor, current_node)
            neighbor_node.g = current_node.g + 1
            neighbor_node.h = heuristic(neighbor, goal_state)

            if neighbor_node not in open_set:
                heapq.heappush(open_set, neighbor_node)

    return None
    
def id_wrapper():
    global stop_bfs,file_path, your_image
    image = pygame.image.load(file_path)
    image = pygame.transform.scale(image, (WIDTH, HEIGHT))
    stop_bfs = False
    image_blocks = {}
    for i in range(9):
        row, col = i // 3, i % 3
        image_blocks[i + 1] = image.subsurface(col * WIDTH // 3, row * HEIGHT // 3, WIDTH // 3, HEIGHT // 3)
    start_time=time.time()
    solution = depth_limited_search()
    end_time=time.time()
    if solution:
            pygame.time.delay(500)
            for step, state in enumerate(solution):
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                draw_puzzle(state, step, image_blocks,round(end_time-start_time,2),id_expanded_nodes)
                pygame.time.delay(100)
                if step < len(solution) - 1:
                    pygame.time.delay(100)
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                pygame.display.flip()
    else:
        font = pygame.font.Font(None, 36)
        no_solution_text = font.render("No Solution !", True, (0, 0, 0))
        text_rect = no_solution_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(no_solution_text, text_rect)
        return None
        
#nhận một câu đố làm đầu vào và trả về một phiên bản câu đố đã được xáo trộn
def shuffle_puzzle(puzzle):
    shuffled_puzzle = list(puzzle)
    random.shuffle(shuffled_puzzle)
    return shuffled_puzzle

def bfs():
    global your_image, current_state, goal_state,bfs_expanded_nodes

    queue = deque([PuzzleNode(current_state)])
    visited = set()

    while queue:
        current_node = queue.popleft()
        bfs_expanded_nodes += 1

        if current_node.puzzle == goal_state:
            return reconstruct_path(current_node)

        visited.add(tuple(current_node.puzzle))

        for neighbor in get_neighbors(current_node.puzzle):
            if tuple(neighbor) not in visited:
                neighbor_node = PuzzleNode(neighbor, current_node)
                queue.append(neighbor_node)

    return None
def dfs():
    global current_state,goal_state,dfs_expanded_nodes
    stack = [PuzzleNode(current_state)]
    closed_set = set()
    
    while stack:
        current_node = stack.pop()
        dfs_expanded_nodes +=1

        if current_node.puzzle == goal_state:
            return reconstruct_path(current_node)

        closed_set.add(tuple(current_node.puzzle))

        for neighbor in get_neighbors(current_node.puzzle):
            if tuple(neighbor) not in closed_set:
                neighbor_node = PuzzleNode(neighbor, current_node)
                stack.append(neighbor_node)

    return None
#Hàm này đặt tất cả các cờ dừng thành True khi nhấp vào nút dừng. Các cờ dừng này được sử dụng để kiểm soát việc thực thi các thuật toán tìm kiếm khác nhau trong ứng dụng.
def handle_stop_button():
    global stop_bfs, stop_dfs, stop_id, stop_usc
    stop_bfs = stop_dfs = stop_id = stop_usc = True
#Chúng tôi tạo một danh sách trống gọi là hàng xóm để lưu trữ các trạng thái lân cận.
def get_neighbors(state):
    neighbors = []
    empty_index = state.index(0)

    if empty_index % 3 > 0:
        new_state = state[:]
        new_state[empty_index], new_state[empty_index - 1] = new_state[empty_index - 1], new_state[empty_index]
        neighbors.append(new_state)

    if empty_index % 3 < 2:
        new_state = state[:]
        new_state[empty_index], new_state[empty_index + 1] = new_state[empty_index + 1], new_state[empty_index]
        neighbors.append(new_state)

    if empty_index // 3 > 0:
        new_state = state[:]
        new_state[empty_index], new_state[empty_index - 3] = new_state[empty_index - 3], new_state[empty_index]
        neighbors.append(new_state)

    if empty_index // 3 < 2:
        new_state = state[:]
        new_state[empty_index], new_state[empty_index + 3] = new_state[empty_index + 3], new_state[empty_index]
        neighbors.append(new_state)

    return neighbors
#Trong mã này, hàm tái tạo_path lấy một nút làm đối số và xây dựng đường dẫn từ nút gốc đến nút đã cho.
def reconstruct_path(node):
    path = []
    while node:
        path.append(node.puzzle)
        node = node.parent
    return path[::-1]
# tạo văn bản cho từng nút và văn bản về số bước và các nút mở rộng
def draw_puzzle(puzzle, step_count, image_blocks,exe_time,expanded_nodes):
    screen.fill(BACKGROUND_COLOR)

    for i in range(9):
        row, col = i // 3, i % 3
        number = puzzle[i]
        if number != 0:
            x = col * (WIDTH // 3)
            y = row * (HEIGHT // 3)
            screen.blit(image_blocks[number], (x, y))
    pygame.draw.rect(screen, RED, (0, 0, WIDTH, HEIGHT), 2)
    # vẽ các văn bản trên màn hình
    global bfs_button, dfs_button, shuffle_button, play_button, id_button, ucs_button

    bfs_button = pygame.draw.rect(screen, (255, 255, 0), (485, HEIGHT - 50, 85, 30))
    dfs_button = pygame.draw.rect(screen, (255, 255, 0), (485, HEIGHT - 100, 85, 30))
    shuffle_button = pygame.draw.rect(screen, (255, 255, 0), (485, HEIGHT - 150, 95, 30))
    play_button = pygame.draw.rect(screen, (255, 255, 0), (485, HEIGHT - 200, 85, 30))
    id_button = pygame.draw.rect(screen, (255, 255, 0), (485, HEIGHT - 250, 85, 30))
    



    font = pygame.font.Font(None, 36)
    bfs_text = font.render("BFS", True, (0, 0, 0))
    dfs_text = font.render("DFS", True, (0, 0, 0))
    shuffle_text = font.render("Random", True, (0, 0, 0))
    play_text = font.render("Play", True, (0, 0, 0))
    id_text = font.render("ID",True,(0,0,0))
    
    

    bfs_text_rect = bfs_text.get_rect(center=bfs_button.center)
    dfs_text_rect = dfs_text.get_rect(center=dfs_button.center)
    shuffle_text_rect = shuffle_text.get_rect(center=shuffle_button.center)
    play_text_rect = play_text.get_rect(center=play_button.center)
    id_text_rect = id_text.get_rect(center=id_button.center)

    screen.blit(bfs_text, bfs_text_rect.topleft)
    screen.blit(dfs_text, dfs_text_rect.topleft)
    screen.blit(shuffle_text, shuffle_text_rect.topleft)
    screen.blit(play_text, play_text_rect.topleft)
    screen.blit(id_text,id_text_rect.topleft)

    text = font.render(f"So buoc: {step_count}", True, (115, 115, 230 ))
    text_rect = text.get_rect(center=(WIDTH // 1.2, HEIGHT + 20))
    screen.blit(text, text_rect)
    pygame.display.flip()
#Kiem tra xem co giai phap khong 
#được sử dụng để tính toán số lượng các ô không khớp giữa trạng thái hiện tại của ô chữ và trạng thái mong muốn của ô chữ
def heuristic(puzzle, goal):
    count = 0
    for i in range(len(puzzle)):
        if puzzle[i] != goal[i]:
            count += 1
    return count
#được sử dụng để tìm kiếm giải pháp cho ô chữ trượt bằng cách sử dụng thuật toán tìm kiếm có giới hạn độ sâu
#Hàm này chịu trách nhiệm khởi tạo và gọi thuật toán DFS để giải nó 
def dfs_wrapper():
    global stop_bfs,file_path, your_image
    image = pygame.image.load(file_path) #tải ảnh từ tệp 
    image = pygame.transform.scale(image, (WIDTH, HEIGHT)) #Thay đổi kích thướt 
    stop_bfs = False
    image_blocks = {}
    #Lap quan 9 ô và trích xuất bề mặt ảnh. Các khối ảnh được trích xuất được lưu trong image_blocks
    for i in range(9):
        row, col = i // 3, i % 3
        image_blocks[i + 1] = image.subsurface(col * WIDTH // 3, row * HEIGHT // 3, WIDTH // 3, HEIGHT // 3)
    start_time=time.time()
    solution = dfs()
    end_time=time.time()
    # Nếu tìm thấy giải pháp thì thực thi 
    if solution:
            pygame.time.delay(500)
            for step, state in enumerate(solution):
                #này kiểm tra các sự kiện của người dùng. Nếu người dùng nhấn sự kiện QUIT, chương trình sẽ thoát
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                draw_puzzle(state, step, image_blocks,round(end_time-start_time,2),dfs_expanded_nodes)
                pygame.time.delay(100)
                if step < len(solution) - 1:
                    pygame.time.delay(100)
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                pygame.display.flip()
    pygame.display.flip()

def bfs_wrapper():
    global stop_bfs,file_path, your_image
    image = pygame.image.load(file_path)
    image = pygame.transform.scale(image, (WIDTH, HEIGHT))
    stop_bfs = False
    image_blocks = {}
    for i in range(9):
        row, col = i // 3, i % 3
        image_blocks[i + 1] = image.subsurface(col * WIDTH // 3, row * HEIGHT // 3, WIDTH // 3, HEIGHT // 3)
    start_time=time.time()
    solution = bfs()
    end_time=time.time()
    if solution:
            pygame.time.delay(500)
            for step, state in enumerate(solution):
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                draw_puzzle(state, step, image_blocks,round(end_time-start_time,2),bfs_expanded_nodes)
                pygame.time.delay(100)
                if step < len(solution) - 1:
                    pygame.time.delay(100)
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                pygame.display.flip()
    pygame.display.flip()

def game_reset():
    global puzzle_state
    puzzle_state = [2, 6, 5, 0, 8, 7, 4, 3, 1]     
#được sử dụng để khởi động một luồng mới khi nút "BFS" được nhấp
def handle_bfs_button():
    solving_thread = threading.Thread(target=bfs_wrapper)
    solving_thread.start()
#được sử dụng để khởi động một luồng mới khi nút "DFS" được nhấp
def handle_dfs_button():
    solving_thread = threading.Thread(target=dfs_wrapper)
    solving_thread.start()
    
def handle_id_button():
    solving_thread = threading.Thread(target=id_wrapper)
    solving_thread.start()
def main():
    global file_path, your_image, initial_state, goal_state, depth_limit,stop_bfs,current_state
    image = pygame.image.load(file_path)
    image = pygame.transform.scale(image, (WIDTH, HEIGHT))
    your_image = pygame.image.load(file_path)
    your_image = pygame.transform.scale(your_image, (WIDTH2 - WIDTH - 15, 235))
    image_blocks = {}
    for i in range(9):
        row, col = i // 3, i % 3
        image_blocks[i + 1] = image.subsurface(col * WIDTH // 3, row * HEIGHT // 3, WIDTH // 3, HEIGHT // 3)
    solution = None
    draw_puzzle(current_state, 0, image_blocks,0,0)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN:
                if bfs_button.collidepoint(event.pos): #BFS button
                    handle_bfs_button()
                elif dfs_button.collidepoint(event.pos):
                    handle_dfs_button()                
                elif shuffle_button.collidepoint(event.pos): # Shuffle butto
                    current_state = shuffle_puzzle(goal_state)
                    draw_puzzle(current_state, 0, image_blocks,0,0)
                elif play_button.collidepoint(event.pos): 
                    handle_mouse_movement(current_state, image_blocks, goal_state)     
                elif id_button.collidepoint(event.pos):
                    handle_id_button()  

        if solution:
            pygame.time.delay(500)
            for step, state in enumerate(solution):
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                draw_puzzle(state, step, image_blocks,0,0)
                pygame.time.delay(100)
                if step < len(solution) - 1:
                    pygame.time.delay(100)
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                pygame.display.flip()
        pygame.display.flip()

if __name__ == "__main__":
    main()