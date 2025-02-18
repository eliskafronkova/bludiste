import pygame
import levels

pygame.init()

window_size = (400, 400)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Bludiště")

fps = 60
clock = pygame.time.Clock()

white = (255,255,255)
black = (0,0,0)
blue = (0,0,255)
green = (0,255,0)

block_size = 40

maze = levels.maze[0]

class Player:
    def __init__(self, position_x, position_y):
        self.position_x= position_x 
        self.position_y = position_y
    
    def Get_position_x (self):
        return self.position_x
    
    def Get_position_y (self):
        return self.position_y
    
    def Set_position_x (self, x):
        self.position_x = x 
        return self.position_x
    
    def Set_position_y (self, y):
        self.position_y = y 
        return self.position_y    


class Goal:
    def __init__(self, position_x, position_y):
        self.position_x= position_x 
        self.position_y = position_y

    def Get_position_x (self):
        return self.position_x
    
    def Get_position_y (self):
        return self.position_y
    
    def Set_position_x (self, x):
        self.position_x = x 
        return self.position_x
    
    def Set_position_y (self, y):
        self.position_y = y 
        return self.position_y    


def najit_pozici( mapa, cislo, osa):
     for row in range(len(mapa)):
        for col in range(len(mapa[row])):
            print(f"x={row}", "y={col}")
            if cislo == mapa[row[col]]:
                if osa == "x":
                    return row
                if osa == "y":
                    return col
                else:
                    print ("Error Osa")
                    
            
player = Player(najit_pozici(maze, 2, "x"), najit_pozici(maze, 2, "y"))

goal = Goal(najit_pozici(maze, 3, "x"), najit_pozici(maze, 3, "y"))

player_speed = block_size

running = True
game_won = False

level = 0

while running:

    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_won:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if maze[player.Get_position_y()][player.Get_position_x()- 1] == 0:
                player.Get_position_x()-= 1
        if keys[pygame.K_RIGHT]:
            if maze[player.Get_position_y()][player.Get_position_x()+ 1] == 0:
             player.Get_position_x()+= 1
        if keys[pygame.K_UP]:
            if maze[player.Get_position_y() - 1][player.Get_position_x()] == 0:
                player.Get_position_y() -= 1
        if keys[pygame.K_DOWN]:
            if maze[player.Get_position_y() + 1][player.Get_position_x()] == 0:
                player.Get_position_y() += 1

        if player.Get_position_x()== goal.Get_position_x() and player.Get_position_y() == goal.Get_position_y():
            game_won = True

    window.fill(white)
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col] == 1:
                pygame.draw.rect(window, black, [col * block_size, row * block_size, block_size, block_size])

    pygame.draw.rect(window, green, [goal.Get_position_x() * block_size, goal.Get_position_y() * block_size, block_size, block_size])

    pygame.draw.rect(window, blue, [player.Get_position_x()* block_size, player.Get_position_y() * block_size, block_size, block_size])

    if game_won:
        font = pygame.font.SysFont("bahnschrift", 50)
        message = font.render("Vyhrál jsi!", True, green)
        window.blit(message, [window_size[0] // 4, window_size[1] // 2])
   
    pygame.display.update()

pygame.quit()