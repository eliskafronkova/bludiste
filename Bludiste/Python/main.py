import pygame
import levels
import math
from enum import Enum
import time
from datetime import timedelta
import mysql.connector
pygame.init()

mydb = mysql.connector.connect(
    host = "dbs.spskladno.cz",
    user = "student10",
    password = "spsnet",
    database = "vyuka10"
    )

mycursor = mydb.cursor()

class TimeMazeC:
    def __init__(self, id, user_id, time, level):
        self.id = id
        self.user_id = user_id
        self.time = time
        self.level = level


def TimeMaze_by_player_id(player_id):
    try:
        query = "SELECT ID, UserID, Time, Level FROM TimeMaze WHERE UserID = %s ORDER BY TimeMaze.Level ASC"
        mycursor.execute(query, (player_id,))
        results = mycursor.fetchall()

        time_maze_instances = [
            TimeMazeC(
                id=row[0],
                user_id=row[1],
                time=timedelta(seconds=int(row[2].total_seconds())) if isinstance(row[2], timedelta) else timedelta(seconds=int(row[2])),
                level=row[3]
            )
            for row in results
        ]  # Vytvoření seznamu objektů TimeMaze
        return time_maze_instances

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

def uloz_score(cas, level):
    global time_mazes

    try:
        # Najdi záznam v seznamu pro daný level
        for time_maze in time_mazes:
            if time_maze.level == level:
                # Porovnej časy
                if cas < time_maze.time.total_seconds():
                    # Aktualizuj čas v seznamu
                    time_maze.time = time.strftime('%H:%M:%S', time.gmtime(cas))

                    # Aktualizuj čas v databázi
                    query = "UPDATE TimeMaze SET Time = %s WHERE UserID = %s AND Level = %s"
                    mycursor.execute(query, (time_maze.time, user_id, level))
                    mydb.commit()
                return

        # Pokud záznam pro daný level neexistuje, vytvoř nový
        query = "INSERT INTO TimeMaze (UserID, Time, Level) VALUES (%s, %s, %s)"
        formatted_time = time.strftime('%H:%M:%S', time.gmtime(cas))
        mycursor.execute(query, (user_id, formatted_time, level))
        mydb.commit()

        # Přidej nový záznam do seznamu
        time_mazes.append(TimeMazeC(id=None, user_id=user_id, time=formatted_time, level=level))

    except mysql.connector.Error as err:
        print(f"Error: {err}")

#barvičky
white = (255,255,255)
black = (0,0,0)
blue = (0,0,255)
green = (0,255,0)
cyan = (0,204,204)
red = (255,0,0)

#Vše o okně
class Window:
    def __init__(self, size_x, size_y):
        self.size_x= size_x 
        self.size_y = size_y

window_size = Window(400,400)
window = pygame.display.set_mode((window_size.size_x, window_size.size_y))
pygame.display.set_caption("Maze")
fps = 60
clock = pygame.time.Clock()
Font = pygame.font.SysFont("bahnschrift", 50)
mini_font=  pygame.font.SysFont("bahnschrift", 16)
#Hráč a Cíl
class Entity:
    def __init__(self, position_x, position_y):
        self.position_x= position_x 
        self.position_y = position_y
    
    def Get_position_x (self):
        return self.position_x
    
    def Get_position_y (self):
        return self.position_y
    
    def Set_position_x(self, x):
        self.position_x = x 
        return self.position_x
    
    def Set_position_y(self, y):
        self.position_y = y 
        return self.position_y  

    def MoveX(self, x):
        self.position_x += x
        return self.position_x
    
    def MoveY(self, y):
        self.position_y += y
        return self.position_y

#Vše o Tlačítkách
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.Font(None, 30)
        

    def draw(self, screen = window):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, current_color, self.rect)

        text_surface = self.font.render(self.text, True, white)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

# Zpracování kliknutí myši na obrazovku
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                self.action()
            return True
        
        else:
            return False
        
# přihlášení
class TextField:
    def __init__(self, x, y, widht, height, placeholder="", is_password=False, font= mini_font, text_color= white, box_color_active= green, box_color_inactive= blue):
        self.rect = pygame.Rect(x, y, widht, height)
        self.placeholder = placeholder
        self.is_password = is_password
        self.font = font
        self.text_color = text_color
        self.box_color_active = box_color_active
        self.box_color_inactive = box_color_inactive
        self.color = self.box_color_inactive
        self.text = ""
        self.active = False
        self.show_password = False
        self.eye_rect = pygame.Rect(self.rect.right + 5, self.rect.y + 10, 20, 20)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            if self.is_password and self.eye_rect.collidepoint(event.pos):
                self.show_password = not self.show_password

            self.color = self.box_color_active if self.active else self.box_color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                prihlaseni()
            else:
                self.text += event.unicode

    def draw(self, screen = window):

        if  len(self.text) > 0:
            if self.is_password and not self.show_password:
                display_text = '*' * len(self.text)
            else:
                display_text = self.text
        else:
            display_text = self.placeholder

        """color = self.text_color if self.text else (150, 150, 150)"""

        
        txt_surface = self.font.render(display_text, True, self.text_color)
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 10))
        pygame.draw.rect(screen, self.color, self.rect, 2)

        if self.is_password:
            pygame.draw.circle(screen, (100, 100, 100), self.eye_rect.center, 8)
            if not self.show_password:
                pygame.draw.line(screen, (150, 0, 0), 
                                 (self.eye_rect.left, self.eye_rect.top), 
                                 (self.eye_rect.right, self.eye_rect.bottom), 2)


    def get_text(self):
        return self.text

        
# hledání pozice hráče 
def najit_pozici(mapa, cislo, osa):
     for row in range(len(mapa)):
        for col in range(len(mapa[row])):
            if cislo == mapa[row][col]:
                if osa == "y":
                    return row
                if osa == "x":
                    return col
                else:
                    print ("Error Osa")

scroll_offset = 0  

game_running = True

#definice stavu hry
def level_select():
    global GameState
    GameState = GameStates.in_level_select

start_time = 0
final_time = 0
best_times = {}



def score():
    global GameState
    GameState = GameStates.in_score  # Přepne stav hry na obrazovku skóre

def zobrazit_tabulku(data, headers, x, y, cell_width, cell_height, font=mini_font, text_color=white, header_color=cyan, line_color=blue):

    # Zobrazení záhlaví
    for col_index, header in enumerate(headers):
        header_rect = pygame.Rect(x + col_index * cell_width, y, cell_width, cell_height)
        pygame.draw.rect(window, header_color, header_rect)
        text_surface = font.render(header, True, text_color)
        text_rect = text_surface.get_rect(center=header_rect.center)
        window.blit(text_surface, text_rect)

    # Zobrazení dat
    for row_index, row in enumerate(data):
        for col_index, cell in enumerate(row):
            cell_rect = pygame.Rect(x + col_index * cell_width, y + (row_index + 1) * cell_height, cell_width, cell_height)
            pygame.draw.rect(window, black, cell_rect)
            pygame.draw.rect(window, line_color, cell_rect, 1)  # Ohraničení buňky
            text_surface = font.render(str(cell), True, text_color)
            text_rect = text_surface.get_rect(center=cell_rect.center)
            window.blit(text_surface, text_rect)


def konec():
    global game_running
    game_running = False

# co se stane když level spustim
def spusteni_levelu():
    global GameState
    global maze
    global start_time
    global CisloRunLevelu  
    
    start_time = time.time()  
    
    maze = levels.maze[CisloRunLevelu - 1]  
    
    player.Set_position_x(najit_pozici(maze, 2, "x"))
    player.Set_position_y(najit_pozici(maze, 2, "y"))
    goal.Set_position_x(najit_pozici(maze, 3, "x"))
    goal.Set_position_y(najit_pozici(maze, 3, "y"))
    
    GameState = GameStates.level_running 

def level_select():
    global GameState
    GameState = GameStates.in_level_select
    create_level_buttons() 


def create_level_buttons():
    global level_buttons
    level_buttons = []
    
    # Výpočet řádky
    DelkaRadku = math.ceil(math.sqrt(len(levels.maze)))# zaokrouhleni nahoru( nadruhou( počet zadání v závorce))


    # Vytvoření tabulky levelu, seřazení kde má jaký být
    TabulkaLevelu = []
    radek = []
    for CisloLevelu in range(1, len(levels.maze)+1, 1):
        radek.append(CisloLevelu)
        if len(radek)==DelkaRadku:
            TabulkaLevelu.append(radek)
            radek = []
    TabulkaLevelu.append(radek)

    level_buttons = []

    CisloRadku = 0
    CisloSloupce = 0

    pocetRadku = len(TabulkaLevelu)
    for CisloRadku in range(pocetRadku):

        pocetSloupcu = len(TabulkaLevelu[CisloRadku])
        for CisloSloupce in range(pocetSloupcu):
    # vytvořeni tlačítek
            level_buttons.append(Button(
                window_size.size_x * (CisloSloupce / pocetSloupcu),
                window_size.size_y * (CisloRadku / pocetRadku),
                window_size.size_x / pocetSloupcu,
                window_size.size_y / pocetRadku,
                f"{TabulkaLevelu[CisloRadku][CisloSloupce]}",
                cyan,
                blue,
                spusteni_levelu
                ))


def menu():
    global GameState
    GameState = GameStates.in_menu

def next_level():
    global CisloRunLevelu
    if CisloRunLevelu <= len(levels.maze)-1:
        CisloRunLevelu += 1
        spusteni_levelu()

password_wrong = False    
def prihlaseni():
    global password_wrong
    if con_prihlaseni(username_field.text, password_field.text):
        menu()
    else:
       password_wrong = True 
       

def con_prihlaseni(username, password):
    global user_id
    global time_mazes

    try:
        query = "SELECT ID, Password FROM UsersMaze WHERE Username = %s" #Vyber sloupce "ID" a "Password" z tabulky "UsersMaze" kde je sloupec "Username" = %s
        mycursor.execute(query, (username,))                   #Nahradí %s za uživatelské jméno 'username'
        result = mycursor.fetchone()                #List který obsahuje ID uživatele a heslo => result = list(ID, heslo)

        if result and result[1] == password:  #protože je result list použijeme index "[1]" result[1] aby jsme dostali věc na 1.(od 0) místě což je heslo
            user_id = result[0]               #Uložílme ID jako user_id bude se hodik k získání časů z tatabáze protože tabulky jsou propojeny přes ID  (protože je result list použijeme index "[0]" result[0] aby jsme dostali věc na 0.(od 0) místě což je ID)
            time_mazes = TimeMaze_by_player_id(user_id)
            return True
        else:
            return False
        
    except mysql.connector.Error as err:    #pokud nastane chyba v databázi vypíšeme jí do konzole (uživatel ja samozřejmě neověřen/nepřihlášen)
        print(f"Error: {err}")
        return False
    


#list se všemi stavy hry
class GameStates(Enum):
    in_menu = 1
    in_level_select = 2
    level_running = 3
    game_won = 4
    in_score = 5
    prihlaseni = 6
    
CisloRunLevelu = 0

GameState = GameStates.prihlaseni

block_size = 40
player_speed = block_size

maze = levels.maze[0]

player = Entity(najit_pozici(maze, 2, "x"), najit_pozici(maze, 2, "y"))
goal = Entity(najit_pozici(maze, 3, "x"), najit_pozici(maze, 3, "y"))


start_but = Button(window_size.size_x / 3, (window_size.size_y * 0.25) / 4,
                   window_size.size_x / 3, window_size.size_y * 0.25,
                   "Start", cyan, blue, level_select)
score_but = Button(window_size.size_x / 3, 2 * (window_size.size_y * 0.25) / 4 + window_size.size_y * 0.25,
                   window_size.size_x / 3, window_size.size_y * 0.25,
                   "Score", cyan, blue, score)
quit_but = Button(window_size.size_x / 3, 3 * (window_size.size_y * 0.25) / 4 + 2 * (window_size.size_y * 0.25),
                  window_size.size_x / 3, window_size.size_y * 0.25,
                  "Quit", cyan, blue, konec)

restart_but = Button(window_size.size_x* 0.1, window_size.size_y* 0.625, 
                    window_size.size_x* 0.3, window_size.size_y*0.125,
                    "Restart", cyan, blue, spusteni_levelu)
next_but = Button(window_size.size_x* 0.6, window_size.size_y* 0.625,
                    window_size.size_x* 0.3, window_size.size_y*0.125,
                    "Next Level", cyan, blue, next_level)
menu_but = Button(window_size.size_x* 0.1, window_size.size_y* 0.8,
                    window_size.size_x* 0.3, window_size.size_y*0.125,
                    "Menu", cyan, blue, menu)
level_menu_but = Button(window_size.size_x* 0.6, window_size.size_y* 0.8,
                    window_size.size_x* 0.3, window_size.size_y*0.125,
                    "Levels", cyan, blue, level_select)
prihlaseni_but = Button(window_size.size_x* 0.1, window_size.size_y* 0.75,
                    window_size.size_x* 0.8, window_size.size_y*0.15,
                    "Login", cyan, blue, prihlaseni)

back_but = Button(window_size.size_x * 0.02, window_size.size_y * 0.02,
                    window_size.size_x * 0.2, window_size.size_y * 0.1,
                    "Back", cyan, blue, menu)

username_field = TextField(window_size.size_x* 0.1, window_size.size_y* 0.25,
                        window_size.size_x* 0.8, window_size.size_y*0.1, "Username")

password_field = TextField(window_size.size_x* 0.1, window_size.size_y* 0.5,
                        window_size.size_x* 0.8, window_size.size_y*0.1, "Password", True)

# Výpočet řádky
DelkaRadku = math.ceil(math.sqrt(len(levels.maze)))# zaokrouhleni nahoru( nadruhou( počet zadání v závorce))


# Vytvoření tabulky levelu, seřazení kde má jaký být
TabulkaLevelu = []
radek = []
for CisloLevelu in range(1, len(levels.maze)+1, 1):
    radek.append(CisloLevelu)
    if len(radek)==DelkaRadku:
        TabulkaLevelu.append(radek)
        radek = []
TabulkaLevelu.append(radek)

level_buttons = []



CisloRadku = 0
CisloSloupce = 0

pocetRadku = len(TabulkaLevelu)
for CisloRadku in range(pocetRadku):

    pocetSloupcu = len(TabulkaLevelu[CisloRadku])
    for CisloSloupce in range(pocetSloupcu):
# vytvořeni tlačítek
        level_buttons.append(Button(
            window_size.size_x * (CisloSloupce / pocetSloupcu),
            window_size.size_y * (CisloRadku / pocetRadku),
            window_size.size_x / pocetSloupcu,
            window_size.size_y / pocetRadku,
            f"{TabulkaLevelu[CisloRadku][CisloSloupce]}",
            cyan,
            blue,
            spusteni_levelu
            ))
        

if __name__ == "__main__":
    while game_running:    # co se stane když hra bezi
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                konec()

            if GameState == GameStates.prihlaseni:
                prihlaseni_but.handle_event(event) 
                username_field.handle_event(event)
                password_field.handle_event(event)
                continue

            #co se stane v menu
            if GameState == GameStates.in_menu:
                start_but.handle_event(event)
                score_but.handle_event(event)
                quit_but.handle_event(event)
                continue

            if GameState == GameStates.in_score:
                back_but.handle_event(event)
                continue

            # co se stane v level selectu
            elif GameState == GameStates.in_level_select:
                for level_but in level_buttons:
                    CisloRunLevelu = int(level_but.text)
                    if level_but.handle_event(event): 
                        break
                continue

            elif GameState == GameStates.game_won:
                restart_but.handle_event(event)
               #if CisloLevelu !=  len(levels.maze):
                next_but.handle_event(event)
                menu_but.handle_event(event)
                level_menu_but.handle_event(event)

                continue

        pygame.display.update()
        keys = pygame.key.get_pressed()
        window.fill(black)
        if GameState == GameStates.prihlaseni:
            message = Font.render("Login", True, white)
            window.blit(message, pygame.Rect(window_size.size_x* 0.1, window_size.size_y* 0.1,
                                            window_size.size_x* 0.9, window_size.size_y*0.9))  
            
            if password_wrong:
                message = mini_font.render("Wrong Username or password", True, red)
                window.blit(message, pygame.Rect(window_size.size_x* 0.1, window_size.size_y* 0.65,
                                            window_size.size_x* 0.8, window_size.size_y*0.1,))  

            prihlaseni_but.draw()
            username_field.draw()
            password_field.draw()
            continue

        if GameState == GameStates.in_menu: #vykresleni tlačítek
            start_but.draw()
            score_but.draw()
            quit_but.draw()
            continue

        if GameState == GameStates.in_score:
            back_but.draw()
            
            cell_width = window_size.size_x // len(["Time", "Level"])
            cell_height = (window_size.size_y - 60) // (len(time_mazes) + 1)

            zobrazit_tabulku(
                [[tm.time, tm.level] for tm in time_mazes],  # Převod objektů na seznamy s pouze časem a levelem
                ["Time", "Level"],  # Hlavičky tabulky
                0, 60, cell_width, cell_height
            )

        if GameState == GameStates.in_level_select: #vykresleni tlačítek
            for level in range(len(level_buttons)):
                level_buttons[level].draw()
            continue

        if GameState == GameStates.level_running: #pokud level běží

            if keys[pygame.K_LEFT]:
                if player.Get_position_x() - 1 >= 0 and maze[player.Get_position_y()][player.Get_position_x() - 1] != 1: 
                    player.MoveX(-1)
                    time.sleep(0.12)

            if keys[pygame.K_RIGHT]:
                if player.Get_position_x() + 1 < len(maze[player.Get_position_y()]) and maze[player.Get_position_y()][player.Get_position_x() + 1] != 1: 
                    player.MoveX(+1)
                    time.sleep(0.12)

            if keys[pygame.K_UP]:
                if player.Get_position_y() - 1 >= 0 and maze[player.Get_position_y() - 1][player.Get_position_x()] != 1:  
                    player.MoveY(-1)
                    time.sleep(0.12)

            if keys[pygame.K_DOWN]:
                if player.Get_position_y() + 1 < len(maze) and maze[player.Get_position_y() + 1][player.Get_position_x()] != 1:  
                    player.MoveY(+1)
                    time.sleep(0.12)



            if player.Get_position_x() == goal.Get_position_x() and player.Get_position_y() == goal.Get_position_y():
                final_time = time.time() - start_time 
                GameState = GameStates.game_won
                uloz_score(final_time, CisloRunLevelu)

            for row in range(len(maze)): #vykreslení herního prostředí
                for col in range(len(maze[row])):
                    if maze[row][col] == 1:
                        pygame.draw.rect(window, cyan, [col * block_size, row * block_size, block_size, block_size])

            pygame.draw.rect(window, blue, [goal.Get_position_x() * block_size, goal.Get_position_y() * block_size, block_size, block_size])  #vykreslení cíle

            pygame.draw.rect(window, green, [player.Get_position_x()* block_size, player.Get_position_y() * block_size, block_size, block_size]) #vykreslení hráče
            continue

        if GameState == GameStates.game_won:
            end_time_rounded = round(final_time, 2)
            time_message = Font.render("Time: {} s".format(end_time_rounded), True, white)

            time_rect = time_message.get_rect(center=(window_size.size_x // 2, window_size.size_y // 2 - 50))
            message = Font.render("You won!", True, green)
            message_rect = message.get_rect(center=(window_size.size_x // 2, window_size.size_y // 2))
    
            window.blit(message, message_rect)
            window.blit(time_message, time_rect)  # Zobrazíme čas vedle zprávy
            restart_but.draw()
            if CisloRunLevelu != len(levels.maze):  # Pokud je k dispozici další level
                next_but.draw()
            menu_but.draw()
            level_menu_but.draw()
            continue


    pygame.quit()