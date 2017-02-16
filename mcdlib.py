#!/usr/bin/env python3
"""
The library behind Missile-Commander's Spin-off.
"""
from math import atan2, degrees, radians, cos, sin
from random import randint
from time import sleep
import pygame
from pygame.sprite import Sprite


#Anwterou epipedou klash - klhronomei apo Sprite
class Entity(Sprite):
    """
    Declare basic game entity aspects. Use this as a parent class.
    """
    def __init__(self, root, dim, img_name, screen):
        """
        Initialize Entity's Rectangle and Image.
        """
        Sprite.__init__(self)
        self.rect = pygame.Rect(root[0], root[1], dim[0], dim[1])
        self.image = pygame.image.load(img_name)
        screen.blit(self.image, self.rect)

    def update(self, screen):
        """
        Update the Entity on the screen object.
        """
        screen.blit(self.image, self.rect)


class InteractiveEntity(Entity):
    """
    Expand Entity with interactive elements.
    """
    def check_explode(self):
        """
        Hook. Meant to signal the class should be implemented on childs.
        """
        pass

    def explode(self, all_groups, screen):
        """
        Explode current interactive object.
        """
        #Create a new explosion at current location and add it the explosions Group
        all_groups['explosions'].add(Explosion(self.rect.topleft[0],\
                                               self.rect.topleft[1], screen))
        #Remove current object from all Groups
        self.kill()


class Background(Entity):
    """
    Define and control Game's Background.
    """
    def __init__(self, root, dim, img_name, screen):
        """
        Initialize Game's Background.
        """
        Entity.__init__(self, root, dim, img_name, screen)

class Crosshair(Entity):
    """
    Define and control Game's Crosshair.
    """
    def __init__(self, dim, img_name, screen):
        Entity.__init__(self, (0, 0), dim, img_name, screen)

    def move(self, pos):
        """
        Move the Crosshair.
        """
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

class City(InteractiveEntity):
    """
    Define and control City objects.
    """
    #Epektash methodou ths InteractiveEntity - Ypoklashs ths Entity
    def __init__(self, root, dim, img_name, screen):
        """
        Initialize City's Rect, image and parameters.
        """
        InteractiveEntity.__init__(self, root, dim, img_name, screen)
        self.is_destroyed = False
        self.missile_stock = 10
        self.centerx = root[0] + (dim[0]/2)

    #Epektash ths synarthshs update ths Entity
    def update(self, screen):
        """
        Extends parent's update function, to also render available Missiles.
        """
        if not self.is_destroyed:
            self.display_missile_stock(screen)
        InteractiveEntity.update(self, screen)

    def restock(self):
        """
        Restock city's missile stock.
        """
        self.missile_stock = 10

    def display_missile_stock(self, screen):
        """
        Render the display of Missile stock.
        """
        #Select font.
        missiles_font = pygame.font.SysFont(None, 18)
        #Format String (Text, Colour and Background).
        missiles_text = missiles_font.render("Missiles: "+\
                                             str(self.missile_stock), True,\
                                             (0, 0, 0), (155, 255, 255))
        #Position Display of Number of Missiles aprox. at the Center of the City
        screen.blit(missiles_text, (self.rect.left+50, self.rect.bottom+10))

    def check_explode(self, all_groups, img_name, screen):
        """
        Implementation of parent's Hook. Detect collision with explosions.
        """
        #Check for collision with members of the explosions Sprite Group
        if pygame.sprite.spritecollideany(self, all_groups['explosions']) is not None:
            self.destroy(img_name, all_groups, screen)

    def destroy(self, img_name, all_groups, screen):
        """
        Destroy City. Change City's Rect and Image.
        """
        #Change flag.
        self.is_destroyed = True
        #Change Rect and Image.
        self.rect = pygame.Rect(self.rect.left-80, self.rect.top + 46, 296, 34)
        self.image = pygame.image.load(img_name)
        #Update display.
        self.update(screen)
        #Create explosions.
        self.explode(all_groups, screen)
        #Add to des_cities Sprite Group.
        all_groups['des_cities'].add(self)

    #Polymorfismos ths synarthshs explode ths klashs InteractiveEntity
    def explode(self, all_groups, screen):
        """
        Create three explosions and remove city form all Groups.
        """
        all_groups['explosions'].add(Explosion(self.rect.centerx,\
                                               self.rect.centery, screen))
        all_groups['explosions'].add(Explosion(self.rect.centerx-25,\
                                               self.rect.centery, screen))
        all_groups['explosions'].add(Explosion(self.rect.centerx+25,\
                                               self.rect.centery, screen))
        self.kill()

    def shoot(self, target, screen, missiles, img_name):
        """
        Shoot a Missile from current City to crosshair's target.
        """
        missiles.add(Missile((self.centerx, 580), (22, 10), (target[0], target[1]),
                             img_name, screen))
        self.missile_stock -= 1


class Missile(InteractiveEntity):
    """
    Define and control Missile objects.
    """
    speed_magnitude = 12
    def __init__(self, root, dim, dest, img_name, screen):
        """
        Initialize Missile's Rect and Image. Calculate rotation and vector speed.
        """
        InteractiveEntity.__init__(self, root, dim, img_name, screen)
        self.startx = root[0]
        self.dest = dest
        #Calculate image rotation.
        offset = (self.dest[1]-self.rect.centery, self.dest[0]-self.rect.centerx)
        self.angle = -degrees(atan2(*offset))
        #Rotate image and adjust Rect.
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        #Calculate vector speed.
        self.angle = -radians(self.angle)
        self.move = [self.rect.x, self.rect.y]
        self.speed = (Missile.speed_magnitude*cos(self.angle),
                      Missile.speed_magnitude*sin(self.angle))
        #Update display.
        self.update(screen)

    def move_me(self, all_groups, screen):
        """
        Calculate new Position for Missile's topleft part and update the screen.
        """
        #Calculate new position (x,y)
        self.move[0] += self.speed[0]
        self.move[1] += self.speed[1]
        #Set calculated position as rect's topleft position
        self.rect.topleft = self.move
        #Update display.
        self.update(screen)
        #Check for explosion conditions.
        self.check_explode(all_groups, screen)

    def check_explode(self, all_groups, screen):
        """
        Check if Missile has reached it's destination.
        """
        if self.rect.collidepoint(self.dest[0], self.dest[1]):
            self.explode(all_groups, screen)


class EnemyMissile(Missile):
    """
    Define and control Enemy Missiles.
    """
    points_worth = 100
    speed_magnitude = 1
    def __init__(self, root, dim, dest, img_name, screen):
        """
        Initialize Parent class and adjust speed Settings.
        """
        Missile.__init__(self, root, dim, dest, img_name, screen)
        self.speed = (EnemyMissile.speed_magnitude*cos(self.angle),
                      EnemyMissile.speed_magnitude*sin(self.angle))

    def move_me(self, all_groups, screen):
        """
        Expand Parent class. Add trailing line behind Missile.
        """
        Missile.move_me(self, all_groups, screen)
        #Create trailing line.
        pygame.draw.line(screen, (255, 255, 255), (self.startx, 0),\
                         (self.rect.centerx, self.rect.centery))

    def check_explode(self, all_groups, screen):
        """
        Polymorph Parent class. Check collision with explosions,cities or ground.
        """
        if pygame.sprite.spritecollideany(self, all_groups['explosions']) is not None:
            Game.score += self.points_worth
            self.explode(all_groups, screen)
        elif self.rect.bottom > 640:
            self.explode(all_groups, screen)
        else:
            col_town = pygame.sprite.spritecollideany(self, all_groups['cities'])
            if col_town is not None and not col_town.is_destroyed:
                self.explode(all_groups, screen)


class Explosion(Entity):
    """
    Define and control Explosions.
    """
    def __init__(self, centX, centY, screen):
        """
        Initialize Rect, Image and clock ticks since creation.
        """
        Entity.__init__(self, (centX, centY), (40, 40), 'img/explosion.png', screen)
        self.rect.centerx = centX
        self.rect.centery = centY
        self.ticks = 0

    def update(self, screen):
        """
        Make the explosion bigger until it disapears after 15 clock ticks.
        """
        if self.ticks <= 15:
            self.image = pygame.transform.smoothscale(self.image,\
                                                      (40+(2*self.ticks),\
                                                       40+(2*self.ticks)))
            self.rect = self.image.get_rect(center=self.rect.center)
            screen.blit(self.image, self.rect)
            self.ticks += 1
        else:
            self.kill()


class Game(object):
    """
    Book-keeping class and library Interface. Constants, settings and functions.
    """
    score = 0
    last_score_thou = 0
    enemy_freq = 4000
    HORIZ = 960
    VERT = 720
    #Settings about img directories
    IMG_DICT = {
        'BG_IMG' : 'img/background.png',
        'CROSS_IMG' : 'img/crosshair.png',
        'CITY_IMG' : 'img/city.png',
        'CITI_DEST' : 'img/city_dmg.png',
        'MISSILE_IMG' : 'img/missile.png'
    }
    def __init__(self):
        """
        Initialize objects and sprites.
        """
        #City Center = 130px*NumOfTown + City width*(NumOfTown-1) + 1/2 of city width
        self.CITY_CENTERS = (204, 482, 760)
        #Initialize clock, screen and Background
        self.game_clock = pygame.time.Clock()
        self.main_screen = pygame.display.set_mode((self.HORIZ, self.VERT),\
                                                   0, 32)
        pygame.display.set_caption('Missile Commander')
        self.main_background = Background((0, 0), (self.HORIZ, self.VERT),\
                                          self.IMG_DICT['BG_IMG'],\
                                          self.main_screen)
        #Hide cursor.
        pygame.mouse.set_visible(False)
        self.crosshair = Crosshair((55, 56), self.IMG_DICT['CROSS_IMG'],
                                   self.main_screen)
        #Create Sprite Groups for Cities Missiles and Explosions
        self.all_groups = {
            'cities' : pygame.sprite.Group(),
            'des_cities' : pygame.sprite.Group(),
            'missiles' : pygame.sprite.Group(),
            'en_missiles' : pygame.sprite.Group(),
            'explosions' : pygame.sprite.Group(),
        }
        #Create and add City objects (Space between them 130px) to cities Sprite Group
        for i in range(0, 3):
            city_x = (130*(i+1)+(148*i))
            self.all_groups['cities'].add(City((city_x, 580), (148, 80),
                                               self.IMG_DICT['CITY_IMG'],
                                               self.main_screen))

    def clock_tick(self):
        """
        Tick the game clock and return the elapsed time in milliseconds.
        """
        return self.game_clock.tick(120)

    def generate_missile(self):
        """
        Generate an enemy Missile from a random top position towards a random city.
        """
        #Choose a random starting point.
        root = (randint(0, 960), 0)
        dim = (22, 10)
        #Choose a random City.
        dest = (self.CITY_CENTERS[randint(0, 2)], 580)
        self.all_groups['en_missiles'].add(EnemyMissile(root, dim, dest,
                                                        self.IMG_DICT['MISSILE_IMG'],
                                                        self.main_screen))

    def shoot_missile(self, target):
        """
        Find nearest, non-destroyed city with available missiles and shoot one.
        """
        dist_min = self.HORIZ
        dist_tmp = 0
        city_min = None
        for city_n in self.all_groups['cities']:
            dist_tmp = abs(city_n.centerx - target[0])
            if dist_tmp < dist_min and city_n.missile_stock != 0 and not city_n.is_destroyed:
                dist_min = dist_tmp
                city_min = city_n
        if city_min is not None:
            city_min.shoot(target, self.main_screen, self.all_groups['missiles'],
                           self.IMG_DICT['MISSILE_IMG'])


    def render(self):
        """
        Handle screen display. Render Images and sprites in the correct order.
        """
        #Render Background first (so it's at the "bottom" of the display stack).
        self.main_background.update(self.main_screen)
        #Check if a City should be destroyed and render it.
        for cur_city in self.all_groups['cities']:
            cur_city.check_explode(self.all_groups, self.IMG_DICT['CITI_DEST'],
                                   self.main_screen)
            cur_city.update(self.main_screen)
        #Render destroyed Cities.
        for cur_dest_city in self.all_groups['des_cities']:
            cur_dest_city.update(self.main_screen)
        #Render Score. Done here so missiles "pass" over it.
        self.print_score()
        #Render allied missiles.
        for cur_missile in self.all_groups['missiles']:
            cur_missile.move_me(self.all_groups, self.main_screen)
        #Render enemy missiles.
        for cur_missile in self.all_groups['en_missiles']:
            cur_missile.move_me(self.all_groups, self.main_screen)
        #Render explosions.
        for cur_explosion in self.all_groups['explosions']:
            cur_explosion.update(self.main_screen)
        self.crosshair.move(pygame.mouse.get_pos())
        self.crosshair.update(self.main_screen)
        #Update display.
        pygame.display.update()

    def print_score(self):
        """
        Create a Rect and display Game Score in it.
        """
        #Select font.
        score_font = pygame.font.SysFont(None, 46)
        #Format String (Text, Colour and Background).
        score_text = score_font.render("Score: " + str(Game.score), True,
                                       (0, 0, 0), (155, 255, 255))
        self.main_screen.blit(score_text, (self.HORIZ*0.05, 20))

    def adjust_dificulty(self):
        """
        Calculate dificulty. Based on player progress.
        """
        if int(Game.score/1000) > Game.last_score_thou:
            #Increase score for next "step".
            Game.last_score_thou = int((Game.last_score_thou + 1)*1.15)
            if Game.enemy_freq < 1600:
                EnemyMissile.speed_magnitude += 0.15
            else:
                #Increase enemy spawn frequency.
                Game.enemy_freq = Game.enemy_freq/1.15
            #Increase the score worh of every enemy missile.
            EnemyMissile.points_worth = round(EnemyMissile.points_worth* 1.15)
            #Restock all "active" cities.
            for cur_city in self.all_groups['cities']:
                cur_city.restock()

    def is_over(self):
        """
        Return True if all cities are destroyed.
        """
        return bool(not self.all_groups['cities'])

    def game_over(self):
        """
        Handle the End of Game.
        """
        #Fill a black screen.
        self.main_screen.fill((0, 0, 0))
        #Select font.
        game_over_font = pygame.font.SysFont(None, 58)
        #Format String (Text, Colour and Background).
        game_over_text = game_over_font.render("GAME OVER.", True, (0, 0, 0),
                                               (155, 255, 255))
        #Position Display of Game Over aprox. at the Midle of the screen.
        self.main_screen.blit(game_over_text, (self.HORIZ*0.40, self.VERT*0.40))
        #Print score so it's visible on Game Over screen.
        self.print_score()
        #Update display.
        pygame.display.update()
        #Sleep 5 sec. before returning (and probably exiting).
        sleep(5)

def set_display_size(dims):
    """
    Change class attributes. Set screen dimensions.
    """
    Game.HORIZ = dims[0]
    Game.VERT = dims[1]

def set_game_sprites(sprite_dict):
    """
    Change class attributes. Set the sprite dictionary.
    """
    Game.IMG_DICT = sprite_dict

def get_enemy_freq():
    """
    Interface for class attribute enemy_freq.
    """
    return Game.enemy_freq
