#!/usr/bin/env python3
"""
Spin-off of the Missile Commander Arcade game.
"""
import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN
from mcdlib import Game, set_display_size, set_game_sprites, get_enemy_freq


def main():
    """Start here! Initialize and start the game."""
    #Initialize pygame
    pygame.init()
    #Adjust the screen size
    #Not needed as it feeds the defaults. Used to showcase when and how to use it.
    set_display_size((960, 720))
    #Adjust the sprites the game is going to use.
    #Not needed as it feeds the defaults. Used to showcase when and how to use it.
    set_game_sprites({
        'BG_IMG' : 'img/background.png',
        'CROSS_IMG' : 'img/crosshair.png',
        'CITY_IMG' : 'img/city.png',
        'CITI_DEST' : 'img/city_dmg.png',
        'MISSILE_IMG' : 'img/missile.png'
    })
    #Create an instance of Game object
    main_game = Game()
    #Game's "Brain" aka the main loop
    game_running = True
    mills = 0
    #While no exit condition is met
    while game_running:
        for cur_event in pygame.event.get():
            if cur_event.type == QUIT:
                #On Quit, exit.
                game_running = False
            elif cur_event.type == KEYDOWN:
                if cur_event.key == K_ESCAPE:
                    #On Esc, exit.
                    game_running = False
            elif cur_event.type == MOUSEBUTTONDOWN:
                #On mouse press, shoot missile.
                shooting_pos = pygame.mouse.get_pos()
                main_game.shoot_missile(shooting_pos)
        #Control enemy missile frequency.
        if mills > get_enemy_freq():
            mills = 0
            main_game.generate_missile()
        #Render game garaphics.
        main_game.render()
        #Increase time since last enemy missile.
        mills += main_game.clock_tick()
        #Adjust game dificulty (if needed).
        main_game.adjust_dificulty()
        #Check for Game Over.
        if main_game.is_over():
            main_game.game_over()
            game_running = False
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
