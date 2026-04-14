"""
UI Widgets - Componentes de interfaz de usuario pixel art
Botones, paneles, sliders, texto, tooltips
"""
import pygame
from src.config import Colors, FONT_SIZES
from src.utils.asset_manager import assets


class UIWidget:
    """Widget base"""
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.visible = True
        self.enabled = True
    
    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, surface): pass
    
    def contains(self, pos):
        return self.rect.collidepoint(pos)


class Button(UIWidget):
    """Botón pixel art con estados hover/pressed"""
    
    def __init__(self, x, y, w, h, text, callback=None,
                 font_size='medium', color_normal=None, color_hover=None,
                 color_text=None, border_color=None):
        super().__init__(x, y, w, h)
        self.text = text
        self.callback = callback
        self.font_size = font_size
        
        self.color_normal = color_normal or Colors.UI_BTN_NORMAL
        self.color_hover  = color_hover  or Colors.UI_BTN_HOVER
        self.color_text   = color_text   or Colors.UI_TEXT
        self.border_color = border_color or Colors.UI_PANEL_BORDER
        
        self.hovered  = False
        self.pressed  = False
        self._sfx_hover_played = False
    
    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.hovered
            self.hovered = self.contains(event.pos)
            if self.hovered and not was_hovered:
                self._sfx_hover_played = False
                try:
                    from src.systems.audio_manager import audio
                    audio.play_sfx('hover')
                except Exception:
                    pass
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains(event.pos):
                self.pressed = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.contains(event.pos):
                self.pressed = False
                try:
                    from src.systems.audio_manager import audio
                    audio.play_sfx('click')
                except Exception:
                    pass
                if self.callback:
                    self.callback()
                return True
            self.pressed = False
        
        return False
    
    def draw(self, surface):
        if not self.visible:
            return
        
        # Color de fondo
        if self.pressed:
            color = Colors.UI_BTN_PRESSED
        elif self.hovered:
            color = self.color_hover
        else:
            color = self.color_normal
        
        # Fondo
        pygame.draw.rect(surface, color, self.rect)
        
        # Borde (efecto pixel art: borde doble)
        border_col = Colors.UI_HIGHLIGHT if self.hovered else self.border_color
        pygame.draw.rect(surface, border_col, self.rect, 2)
        
        # Texto centrado
        font = assets.get_font(self.font_size)
        text_surf = font.render(self.text, True, self.color_text)
        text_rect = text_surf.get_rect(center=self.rect.center)
        if self.pressed:
            text_rect.y += 1  # Efecto presionado
        surface.blit(text_surf, text_rect)


class Panel(UIWidget):
    """Panel con borde pixel art"""
    
    def __init__(self, x, y, w, h, title=None, alpha=220):
        super().__init__(x, y, w, h)
        self.title = title
        self.alpha = alpha
        self._surface = None
        self._rebuild()
    
    def _rebuild(self):
        self._surface = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self._surface.fill((*Colors.UI_PANEL, self.alpha))
        # Borde
        pygame.draw.rect(self._surface, Colors.UI_PANEL_BORDER,
                         (0, 0, self.rect.w, self.rect.h), 2)
        # Esquinas decorativas pixel art
        corner_size = 4
        corner_color = Colors.UI_HIGHLIGHT
        for cx, cy in [(0,0), (self.rect.w-corner_size, 0),
                       (0, self.rect.h-corner_size),
                       (self.rect.w-corner_size, self.rect.h-corner_size)]:
            pygame.draw.rect(self._surface, corner_color,
                             (cx, cy, corner_size, corner_size))
    
    def draw(self, surface):
        if not self.visible:
            return
        surface.blit(self._surface, self.rect.topleft)
        
        # Título
        if self.title:
            font = assets.get_font('small')
            title_surf = font.render(self.title, True, Colors.UI_HIGHLIGHT)
            title_rect = title_surf.get_rect(
                centerx=self.rect.centerx,
                top=self.rect.top + 8
            )
            surface.blit(title_surf, title_rect)
            # Línea separadora
            pygame.draw.line(surface, Colors.UI_PANEL_BORDER,
                             (self.rect.left + 8, self.rect.top + 28),
                             (self.rect.right - 8, self.rect.top + 28), 1)


class Slider(UIWidget):
    """Slider para control de volumen"""
    
    def __init__(self, x, y, w, h, min_val=0.0, max_val=1.0,
                 value=0.5, label='', callback=None):
        super().__init__(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self._value = value
        self.label = label
        self.callback = callback
        self.dragging = False
    
    @property
    def value(self): return self._value
    
    @value.setter
    def value(self, v):
        self._value = max(self.min_val, min(self.max_val, v))
    
    def _pos_to_value(self, x):
        ratio = (x - self.rect.left) / self.rect.width
        return self.min_val + ratio * (self.max_val - self.min_val)
    
    def _value_to_x(self):
        ratio = (self._value - self.min_val) / max(0.001, self.max_val - self.min_val)
        return int(self.rect.left + ratio * self.rect.width)
    
    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains(event.pos):
                self.dragging = True
                self.value = self._pos_to_value(event.pos[0])
                if self.callback:
                    self.callback(self._value)
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = self._pos_to_value(event.pos[0])
            if self.callback:
                self.callback(self._value)
            return True
        
        return False
    
    def draw(self, surface):
        if not self.visible:
            return
        
        # Track
        track_rect = pygame.Rect(
            self.rect.left, self.rect.centery - 2,
            self.rect.width, 4
        )
        pygame.draw.rect(surface, Colors.GRAY_DARK, track_rect)
        
        # Fill
        fill_x = self._value_to_x()
        fill_rect = pygame.Rect(
            self.rect.left, self.rect.centery - 2,
            fill_x - self.rect.left, 4
        )
        pygame.draw.rect(surface, Colors.GOLD, fill_rect)
        
        # Handle
        handle_x = fill_x
        handle_rect = pygame.Rect(handle_x - 6, self.rect.centery - 8, 12, 16)
        pygame.draw.rect(surface, Colors.UI_HIGHLIGHT, handle_rect)
        pygame.draw.rect(surface, Colors.GOLD_DARK, handle_rect, 1)
        
        # Label y valor
        if self.label:
            font = assets.get_font('small')
            label_surf = font.render(
                f"{self.label}: {int(self._value * 100)}%",
                True, Colors.UI_TEXT
            )
            surface.blit(label_surf, (self.rect.left, self.rect.top - 18))


class ProgressBar(UIWidget):
    """Barra de progreso"""
    
    def __init__(self, x, y, w, h, value=0.0, color=None, bg_color=None):
        super().__init__(x, y, w, h)
        self.value = value  # 0.0 - 1.0
        self.color = color or Colors.GOLD
        self.bg_color = bg_color or Colors.GRAY_DARK
    
    def draw(self, surface):
        if not self.visible:
            return
        # Fondo
        pygame.draw.rect(surface, self.bg_color, self.rect)
        # Relleno
        fill_w = int(self.rect.width * max(0, min(1, self.value)))
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.left, self.rect.top,
                                    fill_w, self.rect.height)
            pygame.draw.rect(surface, self.color, fill_rect)
        # Borde
        pygame.draw.rect(surface, Colors.UI_PANEL_BORDER, self.rect, 2)


class Label(UIWidget):
    """Etiqueta de texto"""
    
    def __init__(self, x, y, text, font_size='medium', color=None, align='left'):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.font_size = font_size
        self.color = color or Colors.UI_TEXT
        self.align = align
    
    def draw(self, surface):
        if not self.visible or not self.text:
            return
        font = assets.get_font(self.font_size)
        surf = font.render(str(self.text), True, self.color)
        if self.align == 'center':
            rect = surf.get_rect(centerx=self.rect.x, top=self.rect.y)
        elif self.align == 'right':
            rect = surf.get_rect(right=self.rect.x, top=self.rect.y)
        else:
            rect = surf.get_rect(topleft=self.rect.topleft)
        surface.blit(surf, rect)


class Toggle(UIWidget):
    """Toggle switch (checkbox)"""
    
    def __init__(self, x, y, w, h, label='', value=False, callback=None):
        super().__init__(x, y, w, h)
        self.label = label
        self.value = value
        self.callback = callback
        self.hovered = False
    
    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.contains(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains(event.pos):
                self.value = not self.value
                if self.callback:
                    self.callback(self.value)
                return True
        return False
    
    def draw(self, surface):
        if not self.visible:
            return
        # Caja
        box_size = min(self.rect.height, 20)
        box_rect = pygame.Rect(self.rect.x, self.rect.centery - box_size//2,
                               box_size, box_size)
        bg = Colors.UI_BTN_HOVER if self.hovered else Colors.UI_BTN_NORMAL
        pygame.draw.rect(surface, bg, box_rect)
        pygame.draw.rect(surface, Colors.UI_PANEL_BORDER, box_rect, 2)
        
        if self.value:
            # Checkmark
            inner = box_rect.inflate(-6, -6)
            pygame.draw.rect(surface, Colors.UI_HIGHLIGHT, inner)
        
        # Label
        if self.label:
            font = assets.get_font('small')
            lbl = font.render(self.label, True, Colors.UI_TEXT)
            surface.blit(lbl, (box_rect.right + 8, box_rect.centery - lbl.get_height()//2))


class ScrollableList(UIWidget):
    """Lista scrollable de items"""
    
    def __init__(self, x, y, w, h, items=None, item_height=40,
                 on_select=None):
        super().__init__(x, y, w, h)
        self.items = items or []
        self.item_height = item_height
        self.on_select = on_select
        self.scroll_offset = 0
        self.selected_idx = -1
        self.hovered_idx = -1
    
    def set_items(self, items):
        self.items = items
        self.scroll_offset = 0
        self.selected_idx = -1
    
    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            if self.contains(event.pos):
                rel_y = event.pos[1] - self.rect.top + self.scroll_offset
                self.hovered_idx = rel_y // self.item_height
            else:
                self.hovered_idx = -1
        
        elif event.type == pygame.MOUSEWHEEL:
            if self.contains(pygame.mouse.get_pos()):
                max_scroll = max(0, len(self.items) * self.item_height - self.rect.height)
                self.scroll_offset = max(0, min(max_scroll,
                                                self.scroll_offset - event.y * 20))
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains(event.pos):
                rel_y = event.pos[1] - self.rect.top + self.scroll_offset
                idx = rel_y // self.item_height
                if 0 <= idx < len(self.items):
                    self.selected_idx = idx
                    if self.on_select:
                        self.on_select(idx, self.items[idx])
                    return True
        
        return False
    
    def draw(self, surface):
        if not self.visible:
            return
        
        # Clip region
        clip = surface.get_clip()
        surface.set_clip(self.rect)
        
        # Fondo
        pygame.draw.rect(surface, Colors.UI_PANEL, self.rect)
        
        # Items
        for i, item in enumerate(self.items):
            item_y = self.rect.top + i * self.item_height - self.scroll_offset
            if item_y + self.item_height < self.rect.top:
                continue
            if item_y > self.rect.bottom:
                break
            
            item_rect = pygame.Rect(self.rect.left, item_y,
                                    self.rect.width, self.item_height)
            
            # Color de fondo del item
            if i == self.selected_idx:
                pygame.draw.rect(surface, Colors.UI_BTN_HOVER, item_rect)
            elif i == self.hovered_idx:
                pygame.draw.rect(surface, Colors.UI_BTN_NORMAL, item_rect)
            
            # Separador
            pygame.draw.line(surface, Colors.UI_PANEL_BORDER,
                             (item_rect.left, item_rect.bottom - 1),
                             (item_rect.right, item_rect.bottom - 1), 1)
            
            # Texto del item
            if isinstance(item, dict):
                text = item.get('nombre', str(item))
            else:
                text = str(item)
            
            font = assets.get_font('small')
            text_surf = font.render(text, True, Colors.UI_TEXT)
            surface.blit(text_surf, (item_rect.left + 8,
                                     item_rect.centery - text_surf.get_height()//2))
        
        # Borde
        pygame.draw.rect(surface, Colors.UI_PANEL_BORDER, self.rect, 2)
        
        surface.set_clip(clip)
