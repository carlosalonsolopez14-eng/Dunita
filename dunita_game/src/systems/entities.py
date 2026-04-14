"""
Entities System - Gestión de enemigos nocturnos y NPCs visitantes
"""
import pygame
import random
import math
from src.config import (
    TILE_SIZE, Colors, ENEMY_BASE_HP, ENEMY_BASE_DAMAGE, ENEMY_SPEED
)
from src.utils.asset_manager import assets

class Entity:
    def __init__(self, x, y, sprite_key):
        self.px = x
        self.py = y
        self.sprite_key = sprite_key
        self.sprite_size = 32
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.anim_timer = 0
        
    def update(self, dt, player, world):
        pass
        
    def draw(self, surface, camera_x, camera_y):
        if not self.alive: return
        sx, sy = int(self.px - camera_x), int(self.py - camera_y)
        sprite = assets.get_sprite(self.sprite_key)
        if sprite.get_size() != (self.sprite_size, self.sprite_size):
            sprite = pygame.transform.scale(sprite, (self.sprite_size, self.sprite_size))
        
        # Animación simple
        bob = int(math.sin(pygame.time.get_ticks() * 0.01) * 2)
        surface.blit(sprite, (sx - self.sprite_size//2, sy - self.sprite_size//2 + bob))
        
        # Barra de vida si es enemigo y ha recibido daño
        if isinstance(self, Enemy) and self.hp < self.max_hp:
            self._draw_hp_bar(surface, sx, sy)

    def _draw_hp_bar(self, surface, sx, sy):
        bar_w = 30
        bar_h = 4
        fill_w = int(bar_w * (self.hp / self.max_hp))
        pygame.draw.rect(surface, (50, 0, 0), (sx - bar_w//2, sy - 25, bar_w, bar_h))
        pygame.draw.rect(surface, (255, 0, 0), (sx - bar_w//2, sy - 25, fill_w, bar_h))

class Enemy(Entity):
    def __init__(self, x, y, day_multiplier=1.0):
        super().__init__(x, y, 'creature_scorpion') # Usar escorpión como enemigo base
        self.max_hp = int(ENEMY_BASE_HP * day_multiplier)
        self.hp = self.max_hp
        self.damage = int(ENEMY_BASE_DAMAGE * day_multiplier)
        self.speed = ENEMY_SPEED + random.randint(-10, 10)
        self.detection_range = 300 # Solo atacan si el jugador está cerca
        
    def update(self, dt, player, world):
        if not self.alive: return
        
        # Seguir al jugador si está en rango
        dx = player.px - self.px
        dy = player.py - self.py
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < self.detection_range and dist > 5:
            vx = (dx / dist) * self.speed
            vy = (dy / dist) * self.speed
            
            # Intentar mover con colisiones de terreno
            new_px = self.px + vx * dt
            new_py = self.py + vy * dt
            
            tx, ty = int(new_px // TILE_SIZE), int(new_py // TILE_SIZE)
            if world.is_walkable(tx, ty):
                self.px = new_px
                self.py = new_py
            else:
                # Intentar deslizarse por las paredes
                if world.is_walkable(int(new_px // TILE_SIZE), int(self.py // TILE_SIZE)):
                    self.px = new_px
                elif world.is_walkable(int(self.px // TILE_SIZE), int(new_py // TILE_SIZE)):
                    self.py = new_py
            
        # Daño al jugador por contacto
        if dist < 20:
            player.hp -= self.damage * dt
            if player.hp <= 0:
                player.hp = 0

class Projectile:
    def __init__(self, x, y, target_x, target_y, damage, speed=400, sprite_key='ui_projectile'):
        self.px = x
        self.py = y
        self.damage = damage
        self.speed = speed
        self.sprite_key = sprite_key
        self.alive = True
        self.lifetime = 2.0 # Segundos antes de desaparecer
        
        # Calcular dirección
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
            self.angle = math.degrees(math.atan2(-dy, dx))
        else:
            self.vx = speed
            self.vy = 0
            self.angle = 0
            
    def update(self, dt, enemies):
        if not self.alive: return
        
        self.px += self.vx * dt
        self.py += self.vy * dt
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.alive = False
            return
            
        # Comprobar colisión con enemigos
        for enemy in enemies:
            if not enemy.alive: continue
            dist = math.sqrt((enemy.px - self.px)**2 + (enemy.py - self.py)**2)
            if dist < 20:
                enemy.hp -= self.damage
                self.alive = False
                if enemy.hp <= 0:
                    enemy.alive = False
                return

    def draw(self, surface, camera_x, camera_y):
        if not self.alive: return
        sx, sy = int(self.px - camera_x), int(self.py - camera_y)
        
        sprite = assets.get_sprite(self.sprite_key)
        if sprite:
            rotated_sprite = pygame.transform.rotate(sprite, self.angle)
            surface.blit(rotated_sprite, (sx - rotated_sprite.get_width()//2, sy - rotated_sprite.get_height()//2))
        else:
            pygame.draw.circle(surface, (255, 255, 0), (sx, sy), 4)

class Visitor(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 'ui_player') # Usar sprite de jugador pero con otro color
        self.speed = 40
        self.target_pos = self._get_random_target(x, y)
        self.wait_timer = 0
        
    def _get_random_target(self, x, y):
        return (x + random.randint(-200, 200), y + random.randint(-200, 200))
        
    def update(self, dt, player, world):
        if self.wait_timer > 0:
            self.wait_timer -= dt
            return
            
        dx = self.target_pos[0] - self.px
        dy = self.target_pos[1] - self.py
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 5:
            vx = (dx / dist) * self.speed
            vy = (dy / dist) * self.speed
            self.px += vx * dt
            self.py += vy * dt
        else:
            self.wait_timer = random.uniform(2, 5)
            self.target_pos = self._get_random_target(self.px, self.py)

    def draw(self, surface, camera_x, camera_y):
        # Dibujar visitante con un tinte diferente
        sx, sy = int(self.px - camera_x), int(self.py - camera_y)
        sprite = assets.get_sprite(self.sprite_key).copy()
        sprite.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
        if sprite.get_size() != (self.sprite_size, self.sprite_size):
            sprite = pygame.transform.scale(sprite, (self.sprite_size, self.sprite_size))
        surface.blit(sprite, (sx - self.sprite_size//2, sy - self.sprite_size//2))

class Mercenary(Entity):
    def __init__(self, x, y, is_elite=False):
        super().__init__(x, y, 'ui_player')
        self.is_elite = is_elite
        self.speed = 100 if is_elite else 70
        self.hp = 150 if is_elite else 80
        self.max_hp = self.hp
        self.damage = 25 if is_elite else 12
        self.range = 15 * TILE_SIZE # 15 bloques
        self.target_enemy = None
        
    def update(self, dt, player, world, enemies):
        if not self.alive: return
        
        # Buscar enemigo más cercano si no tiene uno o el actual murió
        if not self.target_enemy or not self.target_enemy.alive:
            self.target_enemy = self._find_nearest_enemy(enemies)
            
        if self.target_enemy:
            dx = self.target_enemy.px - self.px
            dy = self.target_enemy.py - self.py
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < self.range:
                # Atacar si está cerca
                if dist < 40:
                    self.target_enemy.hp -= self.damage * dt
                else:
                    # Acercarse al enemigo
                    vx = (dx / dist) * self.speed
                    vy = (dy / dist) * self.speed
                    self.px += vx * dt
                    self.py += vy * dt
            else:
                self.target_enemy = None # Fuera de rango
        else:
            # Volver cerca del jugador si no hay enemigos
            dx = player.px - self.px
            dy = player.py - self.py
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 100:
                vx = (dx / dist) * self.speed
                vy = (dy / dist) * self.speed
                self.px += vx * dt
                self.py += vy * dt

    def _find_nearest_enemy(self, enemies):
        nearest = None
        min_dist = self.range
        for e in enemies:
            if not e.alive: continue
            dist = math.sqrt((e.px - self.px)**2 + (e.py - self.py)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = e
        return nearest

    def draw(self, surface, camera_x, camera_y):
        sx, sy = int(self.px - camera_x), int(self.py - camera_y)
        sprite = assets.get_sprite(self.sprite_key).copy()
        # Color distintivo: Rojo para mercenarios, Verde para reclutas
        color = (255, 100, 100, 255) if self.is_elite else (100, 255, 100, 255)
        sprite.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        
        if sprite.get_size() != (self.sprite_size, self.sprite_size):
            sprite = pygame.transform.scale(sprite, (self.sprite_size, self.sprite_size))
        
        # Animación simple
        bob = int(math.sin(pygame.time.get_ticks() * 0.01) * 2)
        surface.blit(sprite, (sx - self.sprite_size//2, sy - self.sprite_size//2 + bob))
        
        if self.hp < self.max_hp:
            self._draw_hp_bar(surface, sx, sy)
