from pygame import *
from random import randint
from time import time as timer

#фоновая музыка
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

font.init()
font1 = font.Font(None, 80)
win = font1.render('YOU WIN', True, (0,250,0))
lose= font1.render('GAME OVER', True, (250,0,0))

font2 = font.Font(None, 36)

score = 0
lost = 0
max_lost = 10
# ! жизни игрока
life = 3

#нам нужны такие картинки:
img_back = "galaxy.jpg" # фон игры
img_hero = "rocket.png" # герой
img_enemy = "ufo.png" # враг
img_bullet = 'bullet.png' # пуля

#класс-родитель для других спрайтов
class GameSprite(sprite.Sprite):
    #конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        #Вызываем конструктор класса (Sprite):
        sprite.Sprite.__init__(self)


        #каждый спрайт должен хранить свойство image - изображение
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        #каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    #метод, отрисовывающий героя на окне
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


#класс главного игрока
class Player(GameSprite):
    #метод для управления спрайтом стрелками клавиатуры
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
    #метод "выстрел" (используем место игрока, чтобы создать там пулю)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 10, 20, -10)
        bullets.add(bullet)

#класс спрайта-врага
class Enemy(GameSprite):
    #движение врага
    def update(self):
        self.rect.y += self.speed
        global lost
        #исчезает, если дойдет до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = -40
            lost += 1

#класс спрайта-метеора
class Meteor(GameSprite):
    #движение метеора
    def update(self):
        self.rect.y += self.speed
        #исчезает, если дойдет до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = -40


class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

#Создаём окошко
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))


#создаём спрайты
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)


monsters = sprite.Group()
for i in range(5):
    monster = Enemy('ufo.png', randint(80, win_width - 80), -40, 80, 40, randint(1,5))
    monsters.add(monster)

meteors = sprite.Group()
for i in range(2):
    meteor = Meteor('asteroid.png', randint(80, win_width - 80), -40, 80, 40, randint(1,5))
    meteors.add(meteor)

bullets = sprite.Group()

#переменная "игра закончилась": как только там True, в основном цикле перестают работать спрайты
finish = False
#Основной цикл игры:
run = True #флаг сбрасывается кнопкой закрытия окна

rel_time = False #! флаг ответственный за перезарядку
num_fire = 0 #! переменная для посдчета выстрелов

while run:
    #событие нажатия на кнопку “Закрыть”
    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_SPACE:
                # ! уловие проверки лимита выстрелов и не идет ли сейчас перезарядка
                if num_fire < 5 and rel_time == False:
                    num_fire += 1
                    ship.fire()

                if num_fire >= 5 and rel_time == False:
                    last_time = timer()
                    rel_time = True

    if not finish:
        #обновляем фон
        window.blit(background,(0,0))

        text_score = font2.render('Счет: ' + str(score), True, (255,0,0))
        window.blit(text_score,(10,20))

        text_lost = font2.render('Пропущено: ' + str(lost), True, (255,0,0))
        window.blit(text_lost,(10,50))

        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy('ufo.png', randint(80, win_width - 80), -40, 80, 40, randint(1,5))
            monsters.add(monster)

        ship.update()
        ship.reset()

        monsters.draw(window)
        monsters.update()

        meteors.draw(window)
        meteors.update()

        bullets.draw(window)
        bullets.update()

        if rel_time == True:
            now_time = timer()
            print(now_time - last_time)
            if now_time - last_time < 3:
                reload = font2.render('Wait, reload...', True, (255,0,0))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0
                rel_time = False

        if sprite.spritecollide(ship, monsters, True):
            monster = Enemy('ufo.png', randint(80, win_width - 80), -40, 80, 40, randint(1,5))
            monsters.add(monster)
            life -= 1
        if sprite.spritecollide(ship, meteors, True):
            meteor = Meteor('asteroid.png', randint(80, win_width - 80), -40, 80, 40, randint(1,5))
            meteors.add(meteor)
            life -= 1

        if life == 3:
            life_color = (0, 250, 0)
        elif life == 2:
            life_color = (0, 250, 250)
        elif life == 1:
            life_color = (200, 0, 0)
        elif life == 0:
            life_color = (255, 0, 0)

        text_life = font1.render(str(life), True, life_color)
        window.blit(text_life,(650, 10))
        display.update()

        if lost >= max_lost or life == 0:
            window.blit(lose,(200, win_height // 2))
            display.flip()
            finish = True

        if score == 10:
            window.blit(win,(200, win_height // 2))
            display.flip()
            finish = True

    time.delay(50)
