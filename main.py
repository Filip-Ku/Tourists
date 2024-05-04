import pygame
import sys
import random
import requests
import math

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
WIDTH, HEIGHT = 960, 960
CELL_SIZE = 30
ROWS, COLS = 32, 32

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRID_COLOR = BLACK

class Grid:
    def __init__(self, path):
        self.path = path
        self.matrix = [['L' for _ in range(COLS)] for _ in range(ROWS)]
        self.free_cells = [(x, y) for y in range(ROWS) for x in range(COLS) if self.matrix[y][x] == 'L']
        self.animals = []

        # Dodanie zwierząt na mapie
        self.add_animal('Z')
        self.add_animal('J')

    def draw(self, win):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(win, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(win, GRID_COLOR, (0, y), (WIDTH, y))

        for row in range(ROWS):
            for col in range(COLS):
                if self.matrix[row][col] == 'L':
                    pygame.draw.rect(win, GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                elif self.matrix[row][col] == 'P':
                    pygame.draw.rect(win, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                elif self.matrix[row][col] == 'T':
                    pygame.draw.rect(win, BLUE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                elif self.matrix[row][col] in ['Z', 'J']:
                    pygame.draw.rect(win, RED, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(win, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(win, GRID_COLOR, (0, y), (WIDTH, y))

    def add_animal(self, animal_type):
        x, y = random.choice(self.free_cells)
        self.matrix[y][x] = animal_type
        self.animals.append(Animal(x, y, self.path))

    def move_animals(self):
        current_time = pygame.time.get_ticks()
        for animal in self.animals:
            if current_time - animal.last_move_time > animal.move_delay:
                animal.move(self.matrix)
                animal.last_move_time = current_time


# Zarządzanie grą
class Game:
    def __init__(self):
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Szlak")
        self.path = [
            (0, 29), (1, 29), (1, 30), (2, 30), (2, 31), (3, 31), (4, 31), (5, 31), (5, 30),
            (5, 29), (5, 28), (6, 28), (7, 28), (7, 27), (7, 26), (7, 25), (7, 24), (7, 23),
            (7, 22), (7, 21), (8, 21), (9, 21), (9, 20), (9, 19), (9, 18), (9, 17), (9, 16),
            (10, 16), (11, 16), (11, 15), (11, 14), (12, 14), (13, 14), (13, 13), (13, 12),
            (13, 11), (14, 11), (15, 11), (15, 10), (15, 9), (16, 9), (17, 9), (17, 8), (17, 7),
            (18, 7), (19, 7), (19, 6), (19, 5), (19, 4), (20, 4), (21, 4), (21, 3), (21, 2),
            (22, 2), (23, 2), (23, 3), (23, 4), (24, 4), (24, 5), (24, 6), (25, 6), (25, 7),
            (26, 7), (27, 7), (28, 7), (28, 8), (28, 9), (28, 10), (29, 10), (30, 10), (31, 10)
        ]
        self.grid = Grid(self.path)
        for x, y in self.grid.path:
            self.grid.matrix[y][x] = 'P'
        self.font = pygame.font.SysFont(None, 30)
        self.tourist = Tourist(self.path)
        self.alert_font = pygame.font.SysFont(None, 40)
        self.alert_text = ""
        self.alert_timer = 0

        self.weather_data = self.get_weather('ae1ead0422cc09d560db427bbc7c76c2')

        if not self.weather_data:
            print("Failed to retrieve weather data.")
        else:
            self.weather_text = "Zakopane"
            self.temp_text = f"Temperature: {self.weather_data[1]}°C"
            self.humidity_text = f"Humidity: {self.weather_data[2]}%"
            self.wind_text = f"Wind Speed: {self.weather_data[3]} m/s"

        #Warunki pogodowe
        self.temperature = self.weather_data[1]
        self.wind = self.weather_data[3]
        self.humidity = self.weather_data[2]
        self.avalanche = 2

        self.hiking_ability = self.calculate_hiking_ability()



    def get_weather(self, api_key):
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

    def set_weather(self):
        if self.weather_data:
            weather_text_render = self.font.render(self.weather_text, True, BLACK)
            temp_text_render = self.font.render(self.temp_text, True, BLACK)
            humidity_text_render = self.font.render(self.humidity_text, True, BLACK)
            wind_text_render = self.font.render(self.wind_text, True, BLACK)
            hiking_render = "Hiking level: " + str(self.hiking_ability)
            text_surface = self.font.render(hiking_render, True, BLACK)

            text_rect = weather_text_render.get_rect()
            text_rect.topleft = (10, 10)
            self.win.blit(weather_text_render, text_rect)

            text_rect.y += text_rect.height
            self.win.blit(temp_text_render, text_rect)

            text_rect.y += text_rect.height
            self.win.blit(humidity_text_render, text_rect)

            text_rect.y += text_rect.height
            self.win.blit(wind_text_render, text_rect)

            text_rect.y += text_rect.height
            self.win.blit(text_surface, text_rect)

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def draw_alert(self):
        if self.alert_timer > 0:
            alert_surface = self.alert_font.render(self.alert_text, True, RED)
            alert_rect = alert_surface.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
            pygame.draw.rect(self.win, WHITE, alert_rect)
            self.win.blit(alert_surface, alert_rect)

    def check_tourist_animal_proximity(self):
        tourist_x, tourist_y = self.tourist.x, self.tourist.y
        for animal in self.grid.animals:
            animal_x, animal_y = animal.x, animal.y
            dist = self.distance(tourist_x, tourist_y, animal_x, animal_y)
            if dist <= 10:
                self.alert_text = "Turysta jest za blisko zwierzęcia!"
                self.alert_timer = 3 * 1000
                return
            else:
                self.alert_text=""

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.win.fill(WHITE)

            current_time = pygame.time.get_ticks()
            if current_time - self.tourist.last_move_time > self.tourist.move_delay:
                self.tourist.move(self.grid.matrix)
                self.tourist.last_move_time = current_time

                self.check_tourist_animal_proximity()

            self.grid.draw(self.win)

            self.grid.move_animals()

            self.draw_alert()

            self.set_weather()

            pygame.display.update()

        pygame.quit()
        sys.exit()

    def calculate_hiking_ability(self):
            if self.temperature > 15 and self.wind < 10 and self.humidity < 50:
                hiking_ability = 1
            elif self.temperature > 10 and self.wind < 15 and self.humidity < 60:
                hiking_ability = 2
            elif self.temperature > 5 and self.wind < 20 and self.humidity < 70:
                hiking_ability = 3
            elif self.temperature > 0 and self.wind < 25 and self.humidity < 80:
                hiking_ability = 4
            else:
                hiking_ability = 5
            return hiking_ability


class Tourist:
    def __init__(self, path):
        self.path = path
        self.index = -1
        self.pos = path[self.index]
        self.x, self.y = self.pos
        self.last_move_time = pygame.time.get_ticks()
        self.move_delay = 1000
        self.move_prob = 0.9

    def move(self, matrix):
        old_x, old_y = self.x, self.y
        matrix[old_y][old_x] = 'P'

        if random.random() > self.move_prob:
            matrix[self.y][self.x] = 'T'
            return

        self.index += 1
        if self.index >= len(self.path):
            self.index = 0
        self.pos = self.path[self.index]
        self.x, self.y = self.pos
        matrix[self.y][self.x] = 'T'



class Animal:
    def __init__(self, x, y, path):
        self.x = x
        self.y = y
        self.path = path
        self.move_delay = 1000
        self.last_move_time = pygame.time.get_ticks()
        self.disappeared = False
        self.disappearance_x = None
        self.disappearance_y = None
        self.disappear_time = None

    def move(self, matrix):
        old_x, old_y = self.x, self.y

        if not self.disappeared:
            matrix[old_y][old_x] = 'L'

            if (old_x, old_y) in self.path:
                matrix[old_y][old_x] = 'P'

        if not self.disappeared:
            x, y = random.choice(
                [(old_x + 1, old_y), (old_x - 1, old_y), (old_x, old_y + 1), (old_x, old_y - 1), (old_x, old_y)])

            if x < 0 or x >= COLS or y < 0 or y >= ROWS:
                self.disappeared = True
                self.disappearance_x = old_x
                self.disappearance_y = old_y
                self.disappear_time = pygame.time.get_ticks()
            else:
                self.x, self.y = x, y
                matrix[y][x] = 'Z'

        if self.disappeared and pygame.time.get_ticks() - self.disappear_time > 2000:
            possible_positions = [
                (x, y) for x in range(max(0, self.disappearance_x - 1), min(COLS, self.disappearance_x + 2))
                for y in range(max(0, self.disappearance_y - 1), min(ROWS, self.disappearance_y + 2))
                if matrix[y][x] == 'L'
            ]
            if possible_positions:
                x, y = random.choice(possible_positions)
                self.x, self.y = x, y
                self.disappeared = False
                matrix[y][x] = 'Z'

# Uruchomienie gry
if __name__ == "__main__":
    game = Game()
    game.run()
