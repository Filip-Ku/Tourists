import pygame
import sys
import random
import requests
from pygame import font

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
WIDTH, HEIGHT = 640, 640
CELL_SIZE = 20
ROWS, COLS = 32, 32

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


# Ustawienia siatki
GRID_COLOR = BLACK

# Macierz
matrix = [['L' for _ in range(32)] for _ in range(32)]

free_cells = [(x, y) for y in range(32) for x in range(32) if matrix[y][x] == 'L']
niedzwiedz,jelen = random.sample(free_cells, 2)
matrix[niedzwiedz[1]][niedzwiedz[0]] = 'Z'
matrix[jelen[1]][jelen[0]] = 'Z'

# Ścieżka z punktu początkowego do punktu końcowego
path = [
    (0, 29), (1, 29), (1, 30), (2, 30), (2, 31), (3, 31), (4, 31), (5, 31), (5, 30),
    (5, 29), (5, 28), (6, 28), (7, 28), (7, 27), (7, 26), (7, 25), (7, 24), (7, 23),
    (7, 22), (7, 21), (8, 21), (9, 21), (9, 20), (9, 19), (9, 18), (9, 17), (9, 16),
    (10, 16), (11, 16), (11, 15), (11, 14), (12, 14), (13, 14), (13, 13), (13, 12),
    (13, 11), (14, 11), (15, 11), (15, 10), (15, 9), (16, 9), (17, 9), (17, 8), (17, 7),
    (18, 7), (19, 7), (19, 6), (19, 5), (19, 4), (20, 4), (21, 4), (21, 3), (21, 2),
    (22, 2), (23, 2), (23, 3), (23, 4), (24, 4), (24, 5), (24, 6), (25, 6), (25, 7),
    (26, 7), (27, 7), (28, 7), (28, 8), (28, 9), (28, 10), (29, 10), (30, 10), (31, 10)
]

for x, y in path:
    matrix[y][x] = 'P'

# Utworzenie okna
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Szlak")

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(win, GRID_COLOR, (x,0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(win, GRID_COLOR, (0,y), (WIDTH, y))


def get_weather(api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Zakopane&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        return weather, temperature, humidity, wind_speed
    else:
        print("Failed to retrieve weather data.")
        return None

def set_weather():
    weather_data = get_weather('ae1ead0422cc09d560db427bbc7c76c2')
    if not weather_data:
        return
    font = pygame.font.SysFont(None, 30)
    # Konwersja danych pogodowych na tekst
    weather_text = "Weather: " + weather_data[0]
    temp_text = f"Temperature: {weather_data[1]}°C"
    humidity_text = f"Humidity: {weather_data[2]}%"
    wind_text = f"Wind Speed: {weather_data[3]} m/s"

    # Wyświetlenie danych pogodowych w prawym górnym rogu
    weather_text_render = font.render(weather_text, True, BLACK)
    temp_text_render = font.render(temp_text, True, BLACK)
    humidity_text_render = font.render(humidity_text, True, BLACK)
    wind_text_render = font.render(wind_text, True, BLACK)

    text_rect = weather_text_render.get_rect()
    text_rect.topleft = (10, 10)
    win.blit(weather_text_render, text_rect)

    text_rect.y += text_rect.height
    win.blit(temp_text_render, text_rect)

    text_rect.y += text_rect.height
    win.blit(humidity_text_render, text_rect)

    text_rect.y += text_rect.height
    win.blit(wind_text_render, text_rect)


def fill_grid():
    for row in range(ROWS):
        for col in range(COLS):
            if matrix[row][col] == 'L':
                pygame.draw.rect(win, GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif matrix[row][col] == 'P':
                pygame.draw.rect(win, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif matrix[row][col] == 'T':
                pygame.draw.rect(win, BLUE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif matrix[row][col] == 'Z':
                pygame.draw.rect(win, RED, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Rysowanie siatki
    draw_grid()
    # Ustawianie pogody
    set_weather()

def move_tourist(path, matrix, turysta):
    index = 0
    while index < len(path):
        pos = path[index]
        old_x, old_y = turysta  # Zapamiętaj starą pozycję turysty
        matrix[old_y][old_x] = 'P'  # Przywróć poprzednią pozycję turysty

        # Losowanie czy turysta pozostaje na tej samej kratce
        if random.random() < 0.1:
            x, y = old_x, old_y
        else:
            x, y = pos

        matrix[y][x] = 'T'  # Ustaw nową pozycję turysty

        pygame.display.update()

        draw_grid()
        fill_grid()
        turysta = (x, y)

        # Sprawdzamy czy turysta został na tej samej kratce
        if (x, y) == (old_x, old_y):
            index += 0  # Przejdź do następnej kratki
            pygame.time.delay(2000)
        else:
            index += 1  # Jeśli przesunął się o jedną kratkę, przejdź do kolejnej kratki
            pygame.time.delay(500)

def move_animal(matrix, animal):

    old_x, old_y = animal  # Zapamiętaj starą pozycję zwierzęcia
    matrix[old_y][old_x] = 'L'  # Przywróć poprzednią pozycję turysty
    x, y = random.choice([(old_x + 1, old_y), (old_x - 1, old_y), (old_x, old_y + 1), (old_x, old_y - 1), (old_x, old_y)])
    matrix[y][x] = 'Z'  # Ustaw nową pozycję turysty
    draw_grid()
    fill_grid()
    pygame.display.update()
    return x, y



def main():
    start = (0, 29)
    end = (31, 10)
    turysta = start if random.random() < 0.5 else end
    x, y = turysta
    matrix[y][x] = 'T'
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Wypełnienie tła
        win.fill(WHITE)

        # Wykonanie ruchu turysty
        move_tourist(path, matrix, turysta)

        # Wypełnienie siatki
        fill_grid()

        # Aktualizacja ekranu
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

