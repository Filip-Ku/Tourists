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

        self.alert_font = pygame.font.SysFont(None, 40)
        self.alerts = []

        self.weather_data = self.get_weather('ae1ead0422cc09d560db427bbc7c76c2')

        if not self.weather_data:
            print("Failed to retrieve weather data.")
        else:
            self.weather_text = "Zakopane"
            self.temp_text = f"Temperature: {self.weather_data[1]}°C"
            self.humidity_text = f"Humidity: {self.weather_data[2]}%"
            self.wind_text = f"Wind Speed: {self.weather_data[3]} m/s"

        self.temperature = self.weather_data[1]
        self.wind = self.weather_data[3]
        self.humidity = self.weather_data[2]
        self.avalanche = 0
        if self.avalanche!=0:
            self.alerts.append("Poziom zagrożenia lawinowego: " + str(self.avalanche))
        self.hiking_ability = self.calculate_hiking_ability()
        self.tourist = Tourist(self.path,self.hiking_ability)


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

    def check_tourist_position(self):
        for i in self.path:
            distance=distance(i[0],i[1],self.tourist.x,self.tourist.y)
            if distance>3:
                self.alerts.append("Turysta się zgubił!")

    def add_alert(self, alert_text):
        if alert_text not in self.alerts:
            self.alerts.append(alert_text)

    def draw_alerts(self):
        y_offset = HEIGHT - 10
        for alert in self.alerts:
            alert_surface = self.alert_font.render(alert, True, RED)
            alert_rect = alert_surface.get_rect(bottomright=(WIDTH - 10, y_offset-10))
            pygame.draw.rect(self.win, WHITE, alert_rect)
            self.win.blit(alert_surface, alert_rect)
            y_offset -= alert_rect.height + 5

    def check_tourist_animal_proximity(self):
        tourist_x, tourist_y = self.tourist.x, self.tourist.y
        tourist_close = False
        for animal in self.grid.animals:
            animal_x, animal_y = animal.x, animal.y
            dist = self.distance(tourist_x, tourist_y, animal_x, animal_y)
            if dist < 8:
                tourist_close = True
                break

        if tourist_close and "Turysta zbyt blisko zwierzęcia!" not in self.alerts:
            self.add_alert("Turysta zbyt blisko zwierzęcia!")
        elif not tourist_close and "Turysta zbyt blisko zwierzęcia!" in self.alerts:
            self.alerts.remove("Turysta zbyt blisko zwierzęcia!")

    def check_hiking_ability_alert(self):
        if self.hiking_ability == 5:
            self.add_alert("Ekstremalnie niebezpieczne warunki pogodowe!")
        elif self.hiking_ability == 4:
            self.add_alert("Niebezpieczne warunki pogodowe!")
        else:
            if "Ekstremalnie niebezpieczne warunki pogodowe!" in self.alerts:
                self.alerts.remove("Ekstremalnie niebezpieczne warunki pogodowe!")
            elif "Niebezpieczne warunki pogodowe!" in self.alerts:
                self.alerts.remove("Niebezpieczne warunki pogodowe!")

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.win.fill(WHITE)
            self.check_hiking_ability_alert()

            current_time = pygame.time.get_ticks()
            if current_time - self.tourist.last_move_time > self.tourist.move_delay:
                self.tourist.move(self.grid.matrix)
                self.tourist.last_move_time = current_time
                self.check_tourist_animal_proximity()


            self.grid.draw(self.win)

            self.grid.move_animals()

            self.draw_alerts()

            self.set_weather()

            pygame.display.update()

        pygame.quit()
        sys.exit()

    def calculate_hiking_ability(self):
            if self.temperature > 15 and self.wind < 10:
                hiking_ability = 1
            elif self.temperature > 10 and self.wind < 15:
                hiking_ability = 2
            elif self.temperature > 5 and self.wind < 20:
                hiking_ability = 3
            elif self.temperature > 0 and self.wind < 25:
                hiking_ability = 4
            else:
                hiking_ability = 5
            return hiking_ability

class Tourist:
    def __init__(self, path,hiking_ability):
        self.path = path
        self.index = -1
        self.pos = None
        self.x, self.y = 0, 29
        self.hiking_ability=hiking_ability
        self.last_move_time = pygame.time.get_ticks()
        self.move_delay = 1000
        self.move_prob = self.calculate_probability()
        self.previous_pos = None

    def calculate_probability(self):
        if self.hiking_ability == 1:
            return 0.9
        elif self.hiking_ability == 2:
            return 0.8
        elif self.hiking_ability == 3:
            return 0.7
        elif self.hiking_ability == 4:
            return 0.6
        else:
            return 0.5

    def move(self, matrix):
        old_x, old_y = self.x, self.y

        # Zapisz poprzednią pozycję przed ruchem
        self.previous_pos = (old_x, old_y)

        if (old_x, old_y) not in self.path:
            matrix[old_y][old_x] = 'L'
        else:
            matrix[old_y][old_x] = 'P'

        if random.random() <= (1 - self.move_prob)*2-0.2:
            self.x, self.y = old_x,old_y
            matrix[self.y][self.x] = 'T'
            return

        # Sprawdź, czy turysta ma opuścić szlak
        if random.random() <= 1-self.move_prob:
            possible_positions = []
            self.index -=1
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                new_x, new_y = old_x + dx, old_y + dy
                if 0 <= new_x < COLS and 0 <= new_y < ROWS and matrix[new_y][new_x] == 'L':
                    possible_positions.append((new_x, new_y))

            if possible_positions:
                self.x, self.y = random.choice(possible_positions)
                matrix[self.y][self.x] = 'T'  # Umieść turystę w nowej pozycji
                return

        # Pozostanie na trasie
        self.index += 1
        if self.index >= len(self.path):
            self.index = 0
        self.pos = self.path[self.index]
        self.x, self.y = self.pos
        matrix[self.y][self.x] = 'T'  # Aktualizuj pozycję turysty

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
