import pygame
import sys
import random
import requests
import math

pygame.init()

WIDTH, HEIGHT = 1440, 960
CELL_SIZE = 30
ROWS, COLS = 32, 48

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BEGINNER_COLOR = (0, 255, 255)
EXPERIENCED_COLOR = (255, 165, 0)
PROFESSIONAL_COLOR = (128, 0, 128)
GRID_COLOR = BLACK
YELLOW = (255, 214, 77)

LEGEND_BTN_COLOR = (200, 200, 200)
LEGEND_BTN_HOVER_COLOR = (150, 150, 150)
LEGEND_BTN_TEXT_COLOR = BLACK

LEGEND_BTN_WIDTH = 100
LEGEND_BTN_HEIGHT = 40

class Grid:
    def __init__(self, path):
        self.path = path
        self.matrix = [['L' for _ in range(COLS)] for _ in range(ROWS)]
        self.free_cells = [(x, y) for y in range(ROWS) for x in range(COLS) if
                           self.matrix[y][x] == 'L' and (y, x) not in self.path]
        self.animals = []
        self.tourists = []
        self.group = None

    def draw(self, win):
        for tourist in self.tourists:
            if not tourist.disappear:
                self.matrix[tourist.y][tourist.x] = "T"
            else:
                self.tourists.remove(tourist)

        self.matrix[self.group.y][self.group.x] = "G"

        for row in range(ROWS):
            for col in range(COLS):
                if self.matrix[row][col] == 'L':
                    pygame.draw.rect(win, GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                elif self.matrix[row][col] == 'P':
                    pygame.draw.rect(win, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                elif self.matrix[row][col] == 'T':
                    if (col, row) in self.path:
                        pygame.draw.rect(win, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    else:
                        pygame.draw.rect(win, GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    tourists_on_tile = [t for t in self.tourists if t.x == col and t.y == row]
                    if len(tourists_on_tile) > 0:
                        offset_step = 5
                        start_offset = -(len(tourists_on_tile) - 1) * offset_step // 2
                        for i, tourist in enumerate(tourists_on_tile):
                            tourist.draw(win, start_offset + i * offset_step, start_offset + i * offset_step)
                elif self.matrix[row][col] == 'Z':
                    if (col, row) in self.path:
                        pygame.draw.rect(win, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    else:
                        pygame.draw.rect(win, GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    animals_on_tile = [animal for animal in self.animals if animal.x == col and animal.y == row]
                    for animal in animals_on_tile:
                        animal.draw(win, col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)
                else:
                    pygame.draw.rect(win, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    self.group.draw(win, self.group.x * CELL_SIZE + CELL_SIZE // 2,
                                    self.group.y * CELL_SIZE + CELL_SIZE // 2)

        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(win, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(win, GRID_COLOR, (0, y), (WIDTH, y))

        self.draw_button(win)
        self.draw_path_difficulty(win)

    def add_animal(self, animal_type, hiking_ability):
        while True:
            x, y = random.choice(self.free_cells)
            if x > 7 and y > 5:
                break
        self.matrix[y][x] = animal_type
        self.animals.append(Animal(x, y, self.path, hiking_ability))

    def add_tourist(self, tourist):
        self.tourists.append(tourist)
        self.matrix[tourist.y][tourist.x] = 'T'

    def move_animals(self):
        current_time = pygame.time.get_ticks()
        for animal in self.animals:
            if current_time - animal.last_move_time > animal.move_delay:
                animal.move(self.matrix)
                animal.last_move_time = current_time

    def add_group(self, hiking_ability):
        self.group = Group(self.path, hiking_ability, "experienced")

    def move_group(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.group.last_move_time > self.group.move_delay:
            self.group.move(self.matrix)
            self.group.last_move_time = current_time
            diff = 0.99 - 0.95
            original_diff = 0.8 - 0.2

            scale_factor = diff / original_diff

            scaled_move_prob = scale_factor * (self.group.move_prob - 0.2) + 0.95
            if random.random()>scaled_move_prob:
                self.tourists.append(
                    Tourist(self.path,self.group.index,self.group.hiking_ability,
                            random.choice(["beginner", "experienced", "professional"]),random.choice([True, False])))

    def draw_button(self, screen):
        pygame.draw.rect(screen, BLACK, (WIDTH - LEGEND_BTN_WIDTH - 10, 10, LEGEND_BTN_WIDTH, LEGEND_BTN_HEIGHT))

        font = pygame.font.SysFont(None, 24)
        text_surface = font.render("Legenda", True, WHITE)
        text_rect = text_surface.get_rect(center=((WIDTH - LEGEND_BTN_WIDTH - 10) + 50, 30))

        screen.blit(text_surface, text_rect)

    def draw_path_difficulty(self, screen):
        font = pygame.font.SysFont(None, 24)

        text_trudna = font.render("Trudna ścieżka", True, BLACK)
        text_rect_trudna = text_trudna.get_rect()
        text_rect_trudna.topleft = (36 * 30 - 15, 12 * 30 - 50)

        text_rect_trudna.inflate_ip(10, 5)

        pygame.draw.rect(screen, WHITE, text_rect_trudna)

        text_x = text_rect_trudna.x + (text_rect_trudna.width - text_trudna.get_width()) // 2
        text_y = text_rect_trudna.y + (text_rect_trudna.height - text_trudna.get_height()) // 2
        screen.blit(text_trudna, (text_x, text_y))
        pygame.draw.polygon(screen, RED,
                            [(40 * 30 - 10, 12 * 30 - 31), (40 * 30 - 10, 12 * 30 - 51), (40 * 30 + 10, 12 * 30 - 41)])

        text_latwa = font.render("Łatwa ścieżka", True, BLACK)
        text_rect_latwa = text_latwa.get_rect()
        text_rect_latwa.topleft = (38 * 30 + 10, 19 * 30 + 5)

        text_rect_latwa.inflate_ip(10, 5)

        pygame.draw.rect(screen, WHITE, text_rect_latwa)

        text_x = text_rect_latwa.x + (text_rect_latwa.width - text_latwa.get_width()) // 2
        text_y = text_rect_latwa.y + (text_rect_latwa.height - text_latwa.get_height()) // 2
        screen.blit(text_latwa, (text_x, text_y))
        pygame.draw.polygon(screen, BLUE,
                            [(42 * 30 + 5, 19 * 30 + 4), (42 * 30 + 5, 19 * 30 + 24), (42 * 30 + 25, 19 * 30 + 14)])

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
            (26, 7), (27, 7), (28, 7), (28, 8), (28, 9), (28, 10), (29, 10), (30, 10), (31, 10),
            (32, 10), (32, 11), (32, 12), (33, 12), (33, 13), (33, 14), (33, 15), (34, 15), (35, 15),
            (36, 15), (36, 14), (37, 14), (37, 13), (38, 13), (38, 12), (39, 12), (40, 12), (40, 11),
            (41, 11), (41, 10), (41, 9), (42, 9), (43, 9), (43, 8), (43, 7), (44, 7), (45, 7), (45, 6), (46, 6),
            (47, 6), (36, 16), (37, 16), (37, 17), (37, 18), (37, 19), (37, 20), (38, 20), (39, 20), (39, 21), (40, 21),
            (41, 21), (41, 22), (42, 22), (42, 23), (43, 23), (43, 24), (43, 24), (43, 25), (44, 25), (44, 26),
            (44, 27), (44, 28),(45, 28), (45, 29), (45, 30), (45, 31)
        ]
        self.grid = Grid(self.path)
        for x, y in self.grid.path:
            self.grid.matrix[y][x] = 'P'
        self.font = pygame.font.SysFont("comicsansms", 19)

        self.alert_font = pygame.font.SysFont(None, 40)
        self.alerts = []
        self.weather_data = self.get_weather('ae1ead0422cc09d560db427bbc7c76c2')

        if not self.weather_data:
            print("Failed to retrieve weather data.")
        else:
            self.weather_text = "Zakopane"
            self.temp_text = f"Temperatura: {self.weather_data[1]}°C"
            self.humidity_text = f"Wilgotnosc: {self.weather_data[2]}%"
            self.wind_text = f"Wiatr: {self.weather_data[3]} m/s"

        self.temperature = self.weather_data[1]
        self.wind = self.weather_data[3]
        self.humidity = self.weather_data[2]
        self.avalanche = 0
        if self.avalanche != 0:
            self.alerts.append("Poziom zagrożenia lawinowego: " + str(self.avalanche))
        self.hiking_ability = self.calculate_hiking_ability()
        self.tourist_levels = ["beginner", "experienced", "professional"]

        self.grid.add_animal('Z', self.hiking_ability)
        self.grid.add_animal('Z', self.hiking_ability)
        self.grid.add_animal('Z', self.hiking_ability)

        self.grid.add_group(self.hiking_ability)

        self.grid.add_tourist(
            Tourist(self.path, 126 if random.random() > 0.6667 else (100 if random.random() < 0.3333 else 0),
                    self.hiking_ability, "experienced"))
        self.grid.add_tourist(
            Tourist(self.path, 126 if random.random() > 0.6667 else (100 if random.random() < 0.3333 else 0),
                    self.hiking_ability, "beginner"))
        self.grid.add_tourist(
            Tourist(self.path, 126 if random.random() > 0.6667 else (100 if random.random() < 0.3333 else 0),
                    self.hiking_ability, "professional"))

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
            hiking_render = "Poziom warunków: " + str(self.hiking_ability)
            text_surface = self.font.render(hiking_render, True, BLACK)

            text_rect = weather_text_render.get_rect()
            text_rect.topleft = (15, 15)
            background_rect = pygame.Rect(text_rect.left - 5, text_rect.top - 5, text_rect.width + 130,
                                          text_rect.height * 4 + 50)

            pygame.draw.rect(self.win, (200, 200, 200), background_rect)
            background_rect = pygame.Rect(text_rect.left - 10, text_rect.top - 10, text_rect.width + 140,
                                          text_rect.height * 4 + 60)

            pygame.draw.rect(self.win, (255, 165, 0), background_rect, 5)

            self.win.blit(weather_text_render, text_rect)

            text_rect.y += text_rect.height + 5
            self.win.blit(temp_text_render, text_rect)

            text_rect.y += text_rect.height + 5
            self.win.blit(humidity_text_render, text_rect)

            text_rect.y += text_rect.height + 5
            self.win.blit(wind_text_render, text_rect)

            text_rect.y += text_rect.height + 5
            self.win.blit(text_surface, text_rect)

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def check_tourist_in_group(self):
        for tourist in self.grid.tourists:
            diff = 0.99 - 0.95
            original_diff = 0.9 - 0.5

            scale_factor = diff / original_diff

            scaled_move_prob = scale_factor * (tourist.move_prob - 0.2) + 0.95
            print(scaled_move_prob)
            if tourist.x == self.grid.group.x and tourist.y == self.grid.group.y and random.random() > scaled_move_prob:
                self.grid.tourists.remove(tourist)

    def check_tourist_position(self):
        for tourist in self.grid.tourists:
            min_dist = float('inf')
            for path_x, path_y in self.path:
                dist = self.distance(tourist.x, tourist.y, path_x, path_y)
                min_dist = min(min_dist, dist)
                if min_dist > 3:
                    self.add_alert("Turysta się zgubił!")
                else:
                    if "Turysta się zgubił!" in self.alerts:
                        self.alerts.remove("Turysta się zgubił!")

    def add_alert(self, alert_text):
        if alert_text not in self.alerts:
            self.alerts.append(alert_text)

    def draw_alerts(self):
        y_offset = HEIGHT - 10
        for alert in self.alerts:
            alert_surface = self.alert_font.render(alert, True, RED)
            alert_rect = alert_surface.get_rect(bottomright=(WIDTH - 10, y_offset - 10))
            pygame.draw.rect(self.win, WHITE, alert_rect)
            self.win.blit(alert_surface, alert_rect)
            y_offset -= alert_rect.height + 5

    def check_tourist_animal_proximity(self):
        alert_tourist = "Turysta zbyt blisko zwierzęcia!"
        any_tourist_close = False

        for tourist in self.grid.tourists[:]:
            tourist_close = False
            for animal in self.grid.animals:
                dist = self.distance(tourist.x, tourist.y, animal.x, animal.y)
                if dist < 5:
                    tourist_close = True
                    any_tourist_close = True
                    animal.closest_tourist = tourist
                    if dist == 0:
                        self.grid.tourists.remove(tourist)
                    break

            if not tourist_close:
                for animal in self.grid.animals:
                    if animal.closest_tourist == tourist:
                        animal.closest_tourist = None

        if any_tourist_close:
            if alert_tourist not in self.alerts:
                self.add_alert(alert_tourist)
        else:
            if alert_tourist in self.alerts:
                self.alerts.remove(alert_tourist)

    def check_group_animal_proximity(self):
        alert_group = "Turyści zbyt blisko zwierzęcia!"

        group_close = False
        for animal in self.grid.animals:
            if self.distance(self.grid.group.x, self.grid.group.y, animal.x, animal.y) < 5:
                group_close = True
                animal.closest_tourist = self.grid.group
                break

        if group_close:
            if alert_group not in self.alerts:
                self.add_alert(alert_group)
        else:
            if alert_group in self.alerts:
                self.alerts.remove(alert_group)

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

    def draw_legend(self, screen):
        BEGINNER_COLOR = (0, 255, 255)
        EXPERIENCED_COLOR = (255, 165, 0)
        PROFESSIONAL_COLOR = (128, 0, 128)
        BLACK = (0, 0, 0)
        GREEN = (0, 200, 0)
        GRAY = (220, 220, 220)
        ORANGE = (255, 165, 0)

        legend_width = 400
        legend_height = 270
        legend_x = (WIDTH - legend_width) // 2
        legend_y = (HEIGHT - legend_height) // 2

        pygame.draw.rect(screen, ORANGE, (legend_x - 5, legend_y - 5, legend_width + 10, legend_height + 10))
        # Rysowanie prostokąta tła
        pygame.draw.rect(screen, GRAY, (legend_x, legend_y, legend_width, legend_height))

        font = pygame.font.SysFont("comicsansms", 36)
        title_text = font.render("Legenda:", True, BLACK)
        title_text_rect = title_text.get_rect(center=(legend_x + legend_width // 2, legend_y + 20))
        screen.blit(title_text, title_text_rect)

        # Rysowanie elementów legendy
        text_y = legend_y + 50
        item_spacing = 30

        font = pygame.font.SysFont("comicsansms", 16)
        text = font.render("Turysta początkujący", True, BLACK)
        screen.blit(text, (legend_x + 50, text_y))
        pygame.draw.rect(screen, BEGINNER_COLOR, (legend_x + 20, text_y, 20, 20))

        text_y += item_spacing

        text = font.render("Turysta średniozaawansowany ", True, BLACK)
        screen.blit(text, (legend_x + 50, text_y))
        pygame.draw.rect(screen, EXPERIENCED_COLOR, (legend_x + 20, text_y, 20, 20))

        text_y += item_spacing

        text = font.render("Turysta profesjonalista", True, BLACK)
        screen.blit(text, (legend_x + 50, text_y))
        pygame.draw.rect(screen, PROFESSIONAL_COLOR, (legend_x + 20, text_y, 20, 20))

        text_y += item_spacing

        text = font.render("Grupa turystów", True, BLACK)
        screen.blit(text, (legend_x + 50, text_y))
        pygame.draw.rect(screen, YELLOW, (legend_x + 20, text_y, 20, 20))

        text_y += item_spacing

        text = font.render("Ścieżka/szlak", True, BLACK)
        screen.blit(text, (legend_x + 50, text_y))
        pygame.draw.rect(screen, BLACK, (legend_x + 20, text_y, 20, 20))

        text_y += item_spacing

        text = font.render("Las", True, BLACK)
        screen.blit(text, (legend_x + 50, text_y))
        pygame.draw.rect(screen, GREEN, (legend_x + 20, text_y, 20, 20))

        text_y += item_spacing

        text = font.render("Dzikie zwierzęta", True, BLACK)
        screen.blit(text, (legend_x + 50, text_y))
        pygame.draw.rect(screen, RED, (legend_x + 20, text_y, 20, 20))

    def run(self):
        running = True
        hover = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    legend_button_x = WIDTH - LEGEND_BTN_WIDTH - 10
                    legend_button_y = 10
                    if (legend_button_x <= mouse_x <= legend_button_x + LEGEND_BTN_WIDTH and
                            legend_button_y <= mouse_y <= legend_button_y + LEGEND_BTN_HEIGHT):
                        hover = True
                        self.draw_legend(self.win)
                    else:
                        hover = False

            if not hover:
                self.win.fill(WHITE)
                self.check_hiking_ability_alert()

                current_time = pygame.time.get_ticks()

                for tourist in self.grid.tourists:
                    if current_time - tourist.last_move_time > tourist.move_delay:
                        tourist.move(self.grid.matrix)
                        tourist.last_move_time = current_time
                        self.check_tourist_animal_proximity()
                        self.check_group_animal_proximity()
                        self.check_tourist_position()
                        self.check_tourist_in_group()

                self.grid.draw(self.win)

                self.grid.move_animals()
                self.grid.move_group()

                self.draw_alerts()

                self.set_weather()

            pygame.display.update()

        pygame.quit()
        sys.exit()

    def calculate_hiking_ability(self):
        if self.temperature > 15 and self.wind < 15 and self.humidity<0.92:
            hiking_ability = 1
        elif self.temperature > 10 and self.wind < 20 and self.avalanche < 2 and self.humidity<0.94:
            hiking_ability = 2
        elif self.temperature > 0 and self.wind < 25 and self.avalanche < 3 and self.humidity<0.96:
            hiking_ability = 3
        elif self.temperature > -5 and self.wind < 30 and self.avalanche < 4 and self.humidity<0.98:
            hiking_ability = 4
        else:
            hiking_ability = 5
        return hiking_ability

class Tourist:
    def __init__(self, path, index, hiking_ability, level,direction=None):
        self.path = path
        self.index = index
        self.x, self.y = path[self.index]
        self.level = level
        self.hiking_ability = hiking_ability
        self.last_move_time = pygame.time.get_ticks()
        self.move_delay = 1000
        self.move_prob = self.calculate_probability()
        self.previous_pos = None
        self.direction = direction if direction is not None else (True if self.index == 0 else False)
        self.disappear = None

    def calculate_probability(self):
        base_probability = {
            1: 0.9,
            2: 0.8,
            3: 0.7,
            4: 0.6,
            5: 0.5
        }.get(self.hiking_ability, 0.5)
        if self.level == "beginner":
            return base_probability * 0.8
        elif self.level == "experienced":
            return base_probability
        elif self.level == "professional":
            return base_probability * 1.1
        else:
            return base_probability

    def move(self, matrix):
        old_x, old_y = self.x, self.y

        self.previous_pos = (old_x, old_y)

        if (old_x, old_y) not in self.path:
            matrix[old_y][old_x] = 'L'
        else:
            matrix[old_y][old_x] = 'P'

        if random.random() <= 1 - self.move_prob:
            self.x, self.y = old_x, old_y
            matrix[self.y][self.x] = 'T'
            return

        if random.random() <= (1 - self.move_prob) / 2:
            possible_positions = []
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                new_x, new_y = old_x + dx, old_y + dy
                if 0 <= new_x < COLS and 0 <= new_y < ROWS and (new_x, new_y) not in self.path:
                    possible_positions.append((new_x, new_y))
                    if self.previous_pos in possible_positions:
                        possible_positions.remove(self.previous_pos)
            if possible_positions:
                self.x, self.y = random.choice(possible_positions)
                matrix[self.y][self.x] = 'T'
                return

        if self.previous_pos in self.path:
            if self.direction:
                if self.index == 100:
                    self.disappear=True
                if self.index <80 or self.index>=101:
                    self.index += 1
                    if self.index >= len(self.path):
                        self.disappear=True
                        return
                    self.pos = self.path[self.index]
                    self.x, self.y = self.pos
                    matrix[self.y][self.x] = 'T'
                elif 80<self.index<100:
                    if random.random()<0.3:
                        self.pos = self.path[self.index]
                        self.x, self.y = self.pos
                        matrix[self.y][self.x] = 'T'
                        return
                    else:
                        self.index+=1
                else:
                    if random.random() < self.move_prob / 3:
                        self.index = 81
                    else:
                        self.index = 101
                self.pos = self.path[self.index]
                self.x, self.y = self.pos
                matrix[self.y][self.x] = 'T'
            else:
                if self.index>101:
                    self.index-=1
                elif self.index == 101 or self.index == 81:
                    self.index = 80
                elif self.index>81 and self.index<=100:
                    if random.random()<0.3:
                        return
                    else:
                        self.index-=1
                else:
                    self.index-=1
                if self.index < 0:
                    self.disappear = True
                    return
                self.pos = self.path[self.index]
                self.x, self.y = self.pos
                matrix[self.y][self.x] = 'T'
        else:
            next_x, next_y = self.path[(self.index + 1) % len(self.path)]
            diff_x, diff_y = next_x - self.x, next_y - self.y
            if random.random() > 0.5:
                if diff_x > 0:
                    self.x += 1
                elif diff_x < 0:
                    self.x -= 1
            else:
                if diff_y > 0:
                    self.y += 1
                elif diff_y < 0:
                    self.y -= 1
            matrix[self.y][self.x] = 'T'

    def draw(self, win, x_offset, y_offset):
        color = BEGINNER_COLOR if self.level == "beginner" else EXPERIENCED_COLOR if self.level == "experienced" else PROFESSIONAL_COLOR
        radius = 10
        pygame.draw.circle(win, color, (
            self.x * CELL_SIZE + CELL_SIZE // 2 + x_offset, self.y * CELL_SIZE + CELL_SIZE // 2 + y_offset), radius)

class Animal:
    def __init__(self, x, y, path, hiking_ability):
        self.x = x
        self.y = y
        self.path = path
        self.move_delay = 1000
        self.last_move_time = pygame.time.get_ticks()
        self.disappeared = False
        self.disappearance_x = None
        self.hiking_ability = hiking_ability
        self.move_prob = self.calculate_probability()
        self.disappearance_y = None
        self.disappear_time = None
        self.closest_tourist = None

    def calculate_probability(self):
        if self.hiking_ability == 1:
            return 0.8
        elif self.hiking_ability == 2:
            return 0.6
        elif self.hiking_ability == 3:
            return 0.5
        elif self.hiking_ability == 4:
            return 0.4
        else:
            return 0.2

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def move(self, matrix):
        old_x, old_y = self.x, self.y

        def dissapear():
            self.disappeared = True
            self.disappearance_x = old_x
            self.disappearance_y = old_y
            self.disappear_time = pygame.time.get_ticks()

        if not self.disappeared:
            matrix[old_y][old_x] = 'L'
            if (old_x, old_y) in self.path:
                matrix[old_y][old_x] = 'P'

        if self.closest_tourist:
            distance = self.distance(self.x, self.y, self.closest_tourist.x, self.closest_tourist.y)
            if distance < 5:
                direction_x = old_x - self.closest_tourist.x
                direction_y = old_y - self.closest_tourist.y
                if direction_x != 0:
                    if random.random() < 0.9:
                        self.x += int(direction_x / abs(direction_x))
                        if self.x < COLS and self.y < ROWS:
                            matrix[self.y][self.x] = 'Z'
                        else:
                            dissapear()
                        return
                    else:
                        self.x -= int(direction_x / abs(direction_x))
                        if self.x < COLS and self.y < ROWS:
                            matrix[self.y][self.x] = 'Z'
                        else:
                            dissapear()
                        return
                if direction_y != 0:
                    if random.random() < 0.8:
                        self.y += int(direction_y / abs(direction_y))
                        if self.x < COLS and self.y < ROWS:
                            matrix[self.y][self.x] = 'Z'
                        else:
                            dissapear()
                        return
                    else:
                        self.y -= int(direction_y / abs(direction_y))
                        if self.x < COLS and self.y < ROWS:
                            matrix[self.y][self.x] = 'Z'
                        else:
                            dissapear()
                        return

        if old_x < 0 or old_x >= COLS or old_y < 0 or old_y >= ROWS:
            dissapear()

        if self.disappeared and self.closest_tourist is None:
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
        else:
            if not self.disappeared:
                if random.random() <= (1 - self.move_prob):
                    self.x, self.y = old_x, old_y
                    matrix[self.y][self.x] = 'Z'
                    return

                x, y = random.choice(
                    [(old_x + 1, old_y), (old_x - 1, old_y), (old_x, old_y + 1), (old_x, old_y - 1)])

                if 0 <= x < COLS and 0 <= y < ROWS:
                    self.x, self.y = x, y
                    matrix[y][x] = 'Z'
                else:
                    dissapear()

    def draw(self, win, center_x, center_y):
        pygame.draw.circle(win, RED, (center_x, center_y), 10)

class Group:
    def __init__(self, path, hiking_ability, level):
        self.path = path
        self.index = 126 if random.random() > 0.6667 else (100 if random.random() < 0.3333 else 0)
        self.x, self.y = self.path[self.index]
        self.level = level
        self.hiking_ability = hiking_ability
        self.last_move_time = pygame.time.get_ticks()
        self.move_delay = 1000
        self.move_prob = self.calculate_probability()
        self.direction = True if self.index == 0 else False

    def calculate_probability(self):
        base_probability = {
            1: 0.8,
            2: 0.7,
            3: 0.6,
            4: 0.5,
            5: 0.4
        }.get(self.hiking_ability, 0.5)

        if self.level == "beginner":
            return base_probability * 0.8
        elif self.level == "experienced":
            return base_probability
        elif self.level == "professional":
            return base_probability * 1.1
        else:
            return base_probability

    def move(self, matrix):
        old_x, old_y = self.x, self.y
        matrix[old_y][old_x] = "P"
        if random.random() < 1 - self.move_prob:
            return
        else:
            if not self.direction:
                if 81 < self.index <= 100:
                    if random.random() < 1-self.move_prob:
                        return
                    else:
                        self.index-=1
                elif self.index == 101:
                    self.index = 80
                else:
                    self.index-=1
            else:
                if self.index == 100:
                    self.index = 0
                elif 81 < self.index < 100:
                    if random.random() < 1-self.move_prob:
                        return
                if self.index != 80:
                    self.index += 1
                    if self.index >= len(self.path):
                        self.index = 0
                else:
                    if random.random() < self.move_prob/2:
                        self.index = 81
                    else:
                        self.index = 101
        self.x, self.y = self.path[self.index]
        matrix[self.y][self.x] = 'G'

    def draw(self, win, center_x, center_y):
        pygame.draw.circle(win, YELLOW, (center_x, center_y), 14)

if __name__ == "__main__":
    game = Game()
    game.run()