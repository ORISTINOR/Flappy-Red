import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 400, 600
GRAVITY = 0.5
BIRD_SIZE = 30

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Урок 2")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)  # шрифт


# ДОБАВЛЕНО Класс трубы
class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 60
        self.gap = 150  # Размер свободного пространства между трубами для пролета
        self.speed = 3  # Скорость движения труб влево

        # Случайная высота для верхней трубы
        self.top_height = random.randint(50, HEIGHT - self.gap - 50)
        # Вычисляем высоту нижней трубы, исходя из общей высоты экрана и зазора
        self.bottom_height = HEIGHT - self.top_height - self.gap
        self.passed = False  # Флаг: пролетела ли птица эту трубу (нужен для счета)

    def update(self):
        # Двигаем трубу влево
        self.x -= self.speed

    def draw(self, screen):
        # Рисуем верхнюю трубу
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top_height))
        # Рисуем нижнюю трубу
        pygame.draw.rect(screen, GREEN, (self.x, HEIGHT - self.bottom_height, self.width, self.bottom_height))

    def get_rects(self):
        # Возвращаем два хитбокса (для верхней и нижней трубы отдельно)
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_rect = pygame.Rect(self.x, HEIGHT - self.bottom_height, self.width, self.bottom_height)
        return top_rect, bottom_rect


# Класс птицы
class Bird:
    def __init__(self):  # конструктор
        self.width = BIRD_SIZE  # self говорит о том, что принадлежит конкретному классу
        self.height = BIRD_SIZE
        self.x = WIDTH // 4  # Пункт 1.1: W:4 от левого края
        self.y = HEIGHT // 2  # Пункт 1.1: H:2 от верхнего края
        self.velocity = 0
        self.gravity = GRAVITY

    def update(self):  # мы обновляем статус птицы
        # Пункт 2.1: падение со скоростью g
        self.velocity += self.gravity
        self.y += self.velocity

        # Пункт 2.2: проверка достижения земли
        if self.y >= HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.velocity = 0
        # ПУНКТ 2.3: Проверка столкновения с потолком
        if self.y <= 0:
            self.y = 0
            self.velocity = 0  # Обнуляем скорость, чтобы птица не "копила" инерцию в потолок

    def jump(self):  # функция для прыжка
        self.velocity = -10

    def draw(self, screen):  # рисуем пташку
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))  # рисуем птичку

    def get_rect(self):  # хитбокс
        return pygame.Rect(self.x, self.y, self.width, self.height)


# Класс кнопки
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color  # мышка наводится на кнопку, цвет меняется
        self.current_color = color

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):  # проверка, находится ли курсор на кнопке
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

        pygame.draw.rect(screen, self.current_color, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 1 здесь для проверки левой кнопки
            return self.rect.collidepoint(event.pos)
        return False


# Функция стартового экрана
def show_start_screen():
    start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50,
                          "START", GREEN, (0, 200, 0))  # создаем кнопку

    waiting = True
    while waiting:  # бесконечный цикл пока что-нибудь не произойдет
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if start_button.is_clicked(event):
                waiting = False

        screen.fill(WHITE)

        # Заголовок
        title_text = font.render("FLAPPY BIRD", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_text, title_rect)

        # Инструкция
        inst_text = font.render("Нажми START чтобы начать", True, BLACK)
        inst_rect = inst_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        screen.blit(inst_text, inst_rect)

        start_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)


# Основная игра
def game():  # игровой цикл - сердце любой игры
    bird = Bird()  # создаем пташку

    # ДОБАВЛЕНО список для хранения труб, начальный счет и таймер появления труб
    pipes = []
    score = 0
    pipe_spawn_time = 0

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.jump()

        # Обновление птицы
        bird.update()

        # ДОБАВЛЕНО Логика появления труб
        pipe_spawn_time += 1
        if pipe_spawn_time >= 90:
            pipes.append(Pipe(WIDTH))  # Создаем новую трубу за правым краем экрана
            pipe_spawn_time = 0

        # ДОБАВЛЕНО Обновление труб и проверка столкновений
        bird_rect = bird.get_rect()

        for pipe in pipes[:]:  # Используем срез [:], чтобы безопасно удалять элементы во время цикла
            pipe.update()

            # Проверка столкновения птицы с трубами
            top_pipe_rect, bottom_pipe_rect = pipe.get_rects()
            if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
                print(f"Game Over! Столкновение с трубой. Счёт: {score}")
                return True  # Возвращаемся в стартовое меню

            # Проверка начисления очков (если птица пролетела мимо трубы)
            if not pipe.passed and pipe.x + pipe.width < bird.x:
                pipe.passed = True
                score += 1

            # Удаление труб, которые улетели за левый край экрана
            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)

        # Проверка проигрыша (падение на землю)
        if bird.y >= HEIGHT - bird.height:
            print(f"Game Over! Птица упала на землю. Счёт: {score}")
            return True  # Возвращаемся в стартовое меню

        # Отрисовка
        screen.fill(WHITE)  # очищаем экран

        # ДОБАВЛЕНО Рисуем все трубы из списка
        for pipe in pipes:
            pipe.draw(screen)

        bird.draw(screen)  # рисуем пташку

        # ИЗМЕНЕНО: Отображение динамического счета вместо статического "Счёт: 0"
        score_text = font.render(f"Счёт: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()  # показываем все на экране
        clock.tick(60)  # ждем до 60 кадров в секунду

    return True


# Главный цикл
def main():
    while True:
        show_start_screen()
        if not game():
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()