import pygame
import sys
import random
import numpy as np
import matplotlib.pyplot as plt
from inputBox import InputBox
from label import Label

size = (width, height) = 550, 550
bottom_footer_size = (width, height) = 500, 50
block_size = 2
board = pygame.display.set_mode(size)
background_color = (30, 30, 30)
pause = False
P = 0.5
P_HEAL = 0.1
INFECTED_TIME = 3
ITERATION = 10000
POPULATION_DENSITY = 70
FONT = pygame.font.Font('freesansbold.ttf', 15)


def game_intro():
    global P, P_HEAL, INFECTED_TIME, ITERATION, POPULATION_DENSITY
    clock = pygame.time.Clock()
    label_1 = Label(20, 50, "Percentage of infection:")
    label_2 = Label(20, 100, "Percentage of infection for patients:")
    label_3 = Label(20, 150, "Number of iterations takes to recover:")
    label_4 = Label(20, 200, "Maximum number of iterations:")
    label_5 = Label(20, 250, "Population density (in percent):")
    label_6 = Label(20, 450, "To pause the animation press space.")
    label_7 = Label(20, 500, "To start the animation press Enter.")
    label_boxes = [label_1, label_2, label_3, label_4, label_5, label_6, label_7]
    input_box1 = InputBox(420, 40, 50, 32, str(P))
    input_box2 = InputBox(420, 90, 50, 32, str(P_HEAL))
    input_box3 = InputBox(420, 140, 50, 32, str(INFECTED_TIME))
    input_box4 = InputBox(420, 190, 50, 32, str(ITERATION))
    input_box5 = InputBox(420, 240, 50, 32, str(POPULATION_DENSITY))
    input_boxes = [input_box1, input_box2, input_box3, input_box4, input_box5]
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for box in input_boxes:
                box.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    P = float(input_box1.text)
                    P_HEAL = float(input_box2.text)
                    INFECTED_TIME = float(input_box3.text)
                    ITERATION = float(input_box4.text)
                    POPULATION_DENSITY = float(input_box5.text)
                    done = True

        for box in input_boxes:
            box.update()

        board.fill(background_color)
        for box in input_boxes:
            box.draw(board)

        for box in label_boxes:
            box.draw(board)

        pygame.display.flip()
        clock.tick(30)


def show_graph(current_iteration, infected_percent, title):
    iter = np.arange(1, current_iteration + 1)
    infected_np = np.array(infected_percent)
    plt.title(title)
    plt.plot(iter, infected_np)
    plt.ylabel('infected percent')
    plt.xlabel('Iteration')
    plt.show()


def paused(current_iteration, infected_percent):
    global pause
    show_graph(current_iteration, infected_percent, "paused in iteration: " + str(current_iteration))
    while (pause):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause = False


def infected_count(grid, x, y):
    c = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            row = (x + i + rows) % rows
            col = (y + j + cols) % cols
            if grid[row][col] <= 0:
                c += 1
    if grid[x][y] <= 0:
        c -= 1
    return c

""""
כדי לטפל בהתנגשויות עבדנו בצורה הבאה:
נתנו למשבצת להגריל 20 פעם מקום חדש (כשבתכלס יש רק 9 אפשרויות מה לעשות)
 אם הצלחת באחת מהם ומצאת מקום פנוי מעולה אם לא בסוף 20 הניסיונות
 שמנו אותו במשבצת באלכסון ימינה-למטה. בצורה כזאת בטוח לא יהיה התנגשות משום
 שאנחנו עוברים על המשבצות על פי העמודות ועדיין לא יכול להיות ששמנו במשבצת הזאת מישהו חדש.
 כמובן שאם יש שם מישהו כשנגיע אליו הוא יצטרך לעבור למקום חדש על פי אותם חוקים.
"""
def move(grid, x, y):
    try_count = 20
    while try_count > 0:
        i = random.randint(-1, 1)
        j = random.randint(-1, 1)
        row = (x + i + rows) % rows
        col = (y + j + cols) % cols
        if grid[row][col] == 3:
            return row, col
        try_count -= 1
    row = (x + 1 + rows) % rows
    col = (y + 1 + cols) % cols
    return row, col


def is_infected(probability, infected):
    coefficient = (1 - probability) ** infected
    num = random.random()
    if num > coefficient:
        return True
    return False


def new_grid_func():
    new_grid = []
    for i in range(rows):
        arr = []
        for j in range(cols):
            arr.append(3)
        new_grid.append(arr)
    return new_grid


def text_objects(text, font):
    textSurface = font.render(text, True, (255, 255, 255), background_color)
    return textSurface, textSurface.get_rect()


def update_data(text, data, width, height):
    TextSurf, TextRect = text_objects(text + str(data), FONT)
    TextRect.center = (width, height)
    board.blit(TextSurf, TextRect)


# main
if __name__ == '__main__':
    # pygame.init()
    current_iteration = 0
    cols, rows = int(board.get_width() / block_size), int((board.get_height() - 50) / block_size)
    infected_percent = []
    infected_sum = 1
    game_intro()

    grid = []
    POPULATION_DENSITY = POPULATION_DENSITY / 100
    for i in range(rows):
        arr = []
        for j in range(cols):
            num = np.random.choice(np.arange(1, 4),
                                   p=[POPULATION_DENSITY / 2, POPULATION_DENSITY / 2, 1 - POPULATION_DENSITY])
            if num == 2:
                num = 0
            arr.append(num)
        grid.append(arr)

    while current_iteration < ITERATION and infected_sum != 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause = True
                    paused(current_iteration, infected_percent)

        # black empty 3
        # green heal 2
        # whit human 1
        # red infected <= 0
        healed_sum, infected_sum, regular_sum = 0, 0, 0
        for i in range(cols):
            for j in range(rows):
                x = i * block_size
                y = j * block_size
                if grid[j][i] == 2:
                    pygame.draw.rect(board, (128, 255, 0), (x, y, block_size, block_size))
                    healed_sum += 1
                elif grid[j][i] <= 0:
                    pygame.draw.rect(board, (255, 0, 0), (x, y, block_size, block_size))
                    infected_sum += 1
                elif grid[j][i] == 1:
                    pygame.draw.rect(board, (255, 255, 255), (x, y, block_size, block_size))
                    regular_sum += 1
                else:
                    pygame.draw.rect(board, (0, 0, 0), (x, y, block_size, block_size))
                pygame.draw.line(board, (20, 20, 20), (x, y), (x, height))
                pygame.draw.line(board, (20, 20, 20), (x, y), (width, y))

        new_grid = new_grid_func()

        # update role
        for i in range(cols):
            for j in range(rows):
                infected = infected_count(grid, j, i)
                state = grid[j][i]
                # calculate Infection coefficient
                if state == 1:
                    if is_infected(P, infected):
                        state = 0
                elif state == 2:
                    if is_infected(P_HEAL, infected):
                        state = 0
                elif state <= 0:
                    if state == 1 - INFECTED_TIME:
                        state = 2
                    else:
                        state -= 1
                if state != 3:
                    row, col = move(new_grid, j, i)
                    new_grid[row][col] = state

        grid = new_grid
        current_iteration += 1

        # update the bottom footer
        pygame.draw.rect(board, background_color, (0, 500, 500, 50))
        update_data("Iteration: ", current_iteration, 70
                    , board.get_height() - bottom_footer_size[1] / 2)
        update_data("Infected: ", infected_sum, board.get_width() / 2.1
                    , board.get_height() - bottom_footer_size[1] / 2)
        update_data("Healed: ", healed_sum, board.get_width() - 80
                    , board.get_height() - bottom_footer_size[1] / 2)
        infected_percent.append((float(infected_sum) * 100) / float(infected_sum + healed_sum + regular_sum))
        pygame.display.update()

    show_graph(current_iteration, infected_percent, "end in iteration: " + str(current_iteration))
