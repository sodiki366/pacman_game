import pygame
import random
import math

pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND = (0, 0, 0)
POINT_SIZE = 10
BULLET_SIZE = (20, 10)
PACMAN_SPEED = 4
BULLET_SPEED = 3
POINTS_TO_WIN = 30

# Загружаем изображения Pac-Man'a для каждого направления
try:
    pacman_image = {
        "up": pygame.Surface((30, 30), pygame.SRCALPHA),
        "down": pygame.Surface((30, 30), pygame.SRCALPHA),
        "left": pygame.Surface((30, 30), pygame.SRCALPHA),
        "right": pygame.Surface((30, 30), pygame.SRCALPHA),
        "up_left": pygame.Surface((30, 30), pygame.SRCALPHA),
        "up_right": pygame.Surface((30, 30), pygame.SRCALPHA),
        "down_left": pygame.Surface((30, 30), pygame.SRCALPHA),
        "down_right": pygame.Surface((30, 30), pygame.SRCALPHA)
    }

    # Заполняем цветами для демонстрации (в реальной игре используйте изображения)
    for img in pacman_image.values():
        img.fill((255, 255, 0))
except pygame.error as e:
    print(f"Ошибка загрузки изображений: {e}")
    pygame.quit()
    exit()

# Инициализация экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man Collector")

# Шрифт для отображения счёта
font = pygame.font.SysFont(None, 36)


def get_direction(pos1, pos2):
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]

    direction = "right"  # по умолчанию

    if dy < 0:  # вверх
        if dx < 0:
            direction = "up_left"
        elif dx > 0:
            direction = "up_right"
        else:
            direction = "up"
    elif dy > 0:  # вниз
        if dx < 0:
            direction = "down_left"
        elif dx > 0:
            direction = "down_right"
        else:
            direction = "down"
    else:  # dy == 0
        if dx < 0:
            direction = "left"
        elif dx > 0:
            direction = "right"

    return direction


def move_towards(pos1, pos2, speed):
    x1, y1 = pos1
    x2, y2 = pos2
    dx = x2 - x1
    dy = y2 - y1

    distance = max(1, math.hypot(dx, dy))  # Чтобы избежать деления на 0
    dx = dx / distance
    dy = dy / distance

    x1 += dx * speed
    y1 += dy * speed

    # Проверяем, не прошли ли мы целевую позицию
    if (dx > 0 and x1 > x2) or (dx < 0 and x1 < x2):
        x1 = x2
    if (dy > 0 and y1 > y2) or (dy < 0 and y1 < y2):
        y1 = y2

    return [x1, y1]


# Класс для точек
class Point:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, POINT_SIZE, POINT_SIZE)
        self.spawn()

    def spawn(self, avoid_pos=None, min_distance=100):
        if avoid_pos:
            while True:
                self.rect.x = random.randint(0, SCREEN_WIDTH - POINT_SIZE)
                self.rect.y = random.randint(0, SCREEN_HEIGHT - POINT_SIZE)
                distance = math.hypot(self.rect.centerx - avoid_pos[0], self.rect.centery - avoid_pos[1])
                if distance > min_distance:
                    break
        else:
            self.rect.x = random.randint(0, SCREEN_WIDTH - POINT_SIZE)
            self.rect.y = random.randint(0, SCREEN_HEIGHT - POINT_SIZE)

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, POINT_SIZE // 2)


# Класс для пуль
class Bullet:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BULLET_SIZE[0], BULLET_SIZE[1])
        self.spawn()
        self.speed = BULLET_SPEED

    def spawn(self):
        side = random.randint(0, 3)  # 0 - верх, 1 - право, 2 - низ, 3 - лево

        if side == 0:  # Верх
            self.rect.x = random.randint(0, SCREEN_WIDTH - BULLET_SIZE[0])
            self.rect.y = -BULLET_SIZE[1]
            self.direction = (0, 1)
        elif side == 1:  # Право
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(0, SCREEN_HEIGHT - BULLET_SIZE[1])
            self.direction = (-1, 0)
        elif side == 2:  # Низ
            self.rect.x = random.randint(0, SCREEN_WIDTH - BULLET_SIZE[0])
            self.rect.y = SCREEN_HEIGHT
            self.direction = (0, -1)
        else:  # Лево
            self.rect.x = -BULLET_SIZE[0]
            self.rect.y = random.randint(0, SCREEN_HEIGHT - BULLET_SIZE[1])
            self.direction = (1, 0)

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)

    def is_off_screen(self):
        return (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT)


# Игровые объекты
pacman_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
pacman_rect = pygame.Rect(0, 0, 30, 30)
points = [Point() for _ in range(5)]  # Начнём с 5 точек на экране
bullets = []
score = 0
game_over = False
win = False

# Таймеры
point_spawn_timer = 0
bullet_spawn_timer = 0

# Главный игровой цикл
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0  # Дельта времени в секундах

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and (game_over or win):
            if event.key == pygame.K_r:
                # Перезапуск игры
                pacman_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                points = [Point() for _ in range(5)]
                bullets = []
                score = 0
                game_over = False
                win = False

    if not game_over and not win:
        # Управление Pac-Man'ом
        mouse_pos = pygame.mouse.get_pos()
        direction = get_direction(pacman_pos, mouse_pos)
        pacman_pos = move_towards(pacman_pos, mouse_pos, PACMAN_SPEED)
        pacman_rect.center = pacman_pos

        # Обновление пуль
        bullet_spawn_timer += dt
        if bullet_spawn_timer >= 1.0:  # Каждую секунду новая пуля
            bullets.append(Bullet())
            bullet_spawn_timer = 0

        for bullet in bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                bullets.remove(bullet)
            elif pacman_rect.colliderect(bullet.rect):
                game_over = True

        # Проверка сбора точек
        for point in points[:]:
            if pacman_rect.colliderect(point.rect):
                points.remove(point)
                score += 1
                # Спавним новую точку, не слишком близко к Pac-Man'у
                new_point = Point()
                new_point.spawn(pacman_pos, 100)
                points.append(new_point)

                # Иногда добавляем дополнительную точку
                if random.random() < 0.3 and len(points) < 10:
                    extra_point = Point()
                    extra_point.spawn(pacman_pos, 100)
                    points.append(extra_point)

        # Проверка победы
        if score >= POINTS_TO_WIN:
            win = True

    # Отрисовка
    screen.fill(BACKGROUND)

    # Рисуем точки
    for point in points:
        point.draw()

    # Рисуем пули
    for bullet in bullets:
        bullet.draw()

    # Рисуем Pac-Man'a
    current_image = pacman_image[direction]
    screen.blit(current_image, (pacman_rect.x, pacman_rect.y))

    # Отображаем счёт
    score_text = font.render(f"Счёт: {score}/{POINTS_TO_WIN}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Сообщения о победе/проигрыше
    if game_over:
        game_over_text = font.render("Игра окончена! Нажмите R для перезапуска", True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                     SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
    elif win:
        win_text = font.render("Победа! Нажмите R для перезапуска", True, (0, 255, 0))
        screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2,
                               SCREEN_HEIGHT // 2 - win_text.get_height() // 2))

    pygame.display.flip()

pygame.quit()