import pygame

pygame.init()

window_size = (400, 400)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Bludiště")

white = (255,255,255)
black = (0,0,0)
blue = (0,0,255)
green = (0,255,0)

block_size = 40

maze = [
    [1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1],
    [1, 0, 0, 1, 0, 0, 1, 1, 0, 1],
    [1, 1, 0, 0, 0, 1, 1, 1, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
    [1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

player_x = 1
player_y = 1

goal_x = 7
goal_y = 0

player_speed = block_size

running = True
game_won = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_won:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if maze[player_y][player_x - 1] == 0:
                player_x -= 1
        if keys[pygame.K_RIGHT]:
            if maze[player_y][player_x + 1] == 0:
             player_x += 1
        if keys[pygame.K_UP]:
            if maze[player_y - 1][player_x] == 0:
                player_y -= 1
        if keys[pygame.K_DOWN]:
            if maze[player_y + 1][player_x] == 0:
                player_y += 1

        if player_x == goal_x and player_y == goal_y:
            game_won = True

    window.fill(white)
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == 1:
                pygame.draw.rect(window, black, [col * block_size, row * block_size, block_size, block_size])

    pygame.draw.rect(window, green, [goal_x * block_size, goal_y * block_size, block_size, block_size])

    pygame.draw.rect(window, blue, [player_x * block_size, player_y * block_size, block_size, block_size])

    if game_won:
        font = pygame.font.SysFont("bahnschrift", 50)
        message = font.render("Vyhrál jsi!", True, green)
        window.blit(message, [window_size[0] // 4, window_size[1] // 2])
   
    pygame.display.update()

pygame.quit()