#!/usr/bin/env python3

"""The RCade Ball Game!"""
import sys
import sdl2
import sdl2.ext
import random
import math

BACKGROUND = sdl2.ext.Color(0, 0, 0)
RC_GREEN = sdl2.ext.Color(61, 192, 108)
WHITE = sdl2.ext.Color(255, 255, 255)

P_HEIGHT = 10
W_HEIGHT = 750
W_WIDTH = 600
G_HEIGHT = 300
G_WIDTH = 400

width_shift = 100
height_shift = 100

static_components = []

UPRATE = -1
DOWNRATE = 3
HORIZ_SPEED = 2


class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy, player=None, rects=[]):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.player = player
        self.rects = rects

    def will_collide(self, velocity):
        pleft, ptop, pright, pbottom = self.player.sprite.area
        for rect in self.rects:
            left, top, right, bottom = rect.sprite.area

            if (
                pleft + velocity.vx < right
                and pright + velocity.vx > left
                and ptop + velocity.vy < bottom
                and pbottom + velocity.vy > top
            ):
                return rect
        return None

    def process(self, world, componentsets):
        for comp in componentsets:
            velocity, sprite = comp
            swidth, sheight = sprite.size
            _, posy = sprite.position

            if not sprite == self.player.sprite:
                sprite.x += velocity.vx
                sprite.y += velocity.vy
            else:
                velocity.vy = DOWNRATE
                if not self.will_collide(velocity):
                    sprite.x += velocity.vx
                    sprite.y += velocity.vy
                else:
                    velocity.vy = UPRATE
                    if not self.will_collide(velocity):
                        for y in reversed(range(UPRATE, DOWNRATE)):
                            velocity.vy = y
                            if not self.will_collide(velocity):
                                sprite.y += velocity.vy
                                sprite.x += velocity.vx
                                break
                    else:
                        vx = velocity.vx
                        velocity.vx = 0
                        if not self.will_collide(velocity):
                            sprite.y += velocity.vy

            if sprite not in static_components:
                sprite.x = max(self.minx, sprite.x)
                sprite.y = max(self.miny, sprite.y)

                if sprite.x + swidth > self.maxx:
                    sprite.x = self.maxx - swidth
                if not sprite == self.player.sprite:
                    if sprite.y + sheight > self.maxy:
                        sprite.y = self.maxy - sheight
                else:
                    if sprite.y + sheight > (self.maxy - 10):
                        sprite.y = self.maxy - 10 - sheight


class SoftwareRenderSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderSystem, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, BACKGROUND)
        super(SoftwareRenderSystem, self).render(reversed(components))


class TextureRenderSystem(sdl2.ext.TextureSpriteRenderSystem):
    def __init__(self, renderer):
        super(TextureRenderSystem, self).__init__(renderer)
        self.renderer = renderer

    def render(self, components):
        tmp = self.renderer.color
        self.renderer.color = BACKGROUND
        self.renderer.clear()
        self.renderer.color = tmp

        super(TextureRenderSystem, self).render(reversed(components))


class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0


class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0, score=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.playerscore = score
        self.velocity = Velocity()


class Rect(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()


def generate_row(movement, world, factory, y=G_HEIGHT // 100):
    num_gaps = random.randint(1, 5)
    r_width = 0
    for j in range(0, num_gaps):
        min_x = j * G_WIDTH // num_gaps
        gap_width = 20 + random.randint(0, 10)
        l_padding = random.randint(1, G_WIDTH // num_gaps - gap_width - 1)

        movement.rects.append(
            Rect(
                world,
                factory.from_color(RC_GREEN, size=(l_padding + r_width, P_HEIGHT)),
                min_x + width_shift - r_width,
                y * 100 + height_shift + 50,
            )
        )

        r_width = G_WIDTH // num_gaps - l_padding - gap_width

        if j == num_gaps - 1:
            movement.rects.append(
                Rect(
                    world,
                    factory.from_color(RC_GREEN, size=(r_width, P_HEIGHT)),
                    min_x + l_padding + gap_width + width_shift,
                    y * 100 + height_shift + 50,
                )
            )


def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("RCade Falldown!", size=(W_WIDTH, W_HEIGHT))
    window.show()

    if "-software" in sys.argv:
        print("Using software rendering")
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    else:
        print("(Default) Using hardware acceleration")
        renderer = sdl2.ext.Renderer(window)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)

    world = sdl2.ext.World()

    movement = MovementSystem(
        width_shift, -10 + height_shift, 400 + width_shift, 310 + height_shift
    )
    if factory.sprite_type == sdl2.ext.SOFTWARE:
        spriterenderer = SoftwareRenderSystem(window)
    else:
        spriterenderer = TextureRenderSystem(renderer)

    world.add_system(movement)
    world.add_system(spriterenderer)

    outer_top = Rect(world, factory.from_color(WHITE, size=(600, 10)), 0, 0)
    static_components.append(outer_top.sprite)
    outer_bottom = Rect(world, factory.from_color(WHITE, size=(600, 10)), 0, 740)
    static_components.append(outer_bottom.sprite)
    outer_left = Rect(world, factory.from_color(WHITE, size=(10, 750)), 0, 0)
    static_components.append(outer_left.sprite)
    outer_right = Rect(world, factory.from_color(WHITE, size=(10, 750)), 590, 0)
    static_components.append(outer_right.sprite)

    border_rect_top = Rect(world, factory.from_color(WHITE, size=(500, 50)), 50, 50)
    static_components.append(border_rect_top.sprite)
    border_rect_bottom = Rect(world, factory.from_color(WHITE, size=(500, 50)), 50, 400)
    static_components.append(border_rect_bottom.sprite)
    border_rect_left = Rect(world, factory.from_color(WHITE, size=(50, 300)), 50, 100)
    static_components.append(border_rect_left.sprite)
    border_rect_right = Rect(world, factory.from_color(WHITE, size=(50, 300)), 500, 100)
    static_components.append(border_rect_right.sprite)

    base_mid_left = Rect(world, factory.from_color(WHITE, size=(175, 50)), 0, 500)
    static_components.append(base_mid_left.sprite)
    base_mid_right = Rect(world, factory.from_color(WHITE, size=(175, 50)), 425, 500)
    static_components.append(base_mid_right.sprite)

    base_mid_left2 = Rect(world, factory.from_color(WHITE, size=(50, 50)), 550, 550)
    static_components.append(base_mid_left2.sprite)
    base_mid_right2 = Rect(world, factory.from_color(WHITE, size=(50, 50)), 0, 550)
    static_components.append(base_mid_right2.sprite)

    letter0 = Rect(world, factory.from_color(WHITE, size=(45, 45)), 150, 605)
    static_components.append(letter0.sprite)
    letter1 = Rect(world, factory.from_color(WHITE, size=(45, 45)), 240, 605)
    static_components.append(letter1.sprite)
    letter2 = Rect(world, factory.from_color(WHITE, size=(45, 45)), 330, 605)
    static_components.append(letter2.sprite)
    letter3 = Rect(world, factory.from_color(WHITE, size=(45, 45)), 420, 605)
    static_components.append(letter3.sprite)
    letter4 = Rect(world, factory.from_color(WHITE, size=(45, 45)), 105, 650)
    static_components.append(letter4.sprite)
    letter5 = Rect(world, factory.from_color(WHITE, size=(45, 45)), 195, 650)
    static_components.append(letter5.sprite)
    letter6 = Rect(world, factory.from_color(WHITE, size=(45, 45)), 285, 650)
    static_components.append(letter6.sprite)
    letter7 = Rect(world, factory.from_color(WHITE, size=(45, 45)), 375, 650)
    static_components.append(letter7.sprite)

    player = Player(
        world,
        factory.from_color(WHITE, size=(10, 10)),
        200 + width_shift,
        300 + height_shift,
    )
    movement.player = player

    for y in range(0, (G_HEIGHT) // 100):
        generate_row(movement, world, factory, y)

    running = True
    time = 0
    last_score = 0
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    player.velocity.vx = -HORIZ_SPEED
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    player.velocity.vx = HORIZ_SPEED
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT):
                    player.velocity.vx = 0

        for rect in movement.rects:
            rect.velocity.vy = UPRATE

            _, posy = rect.sprite.position
            if posy == height_shift - 10:
                world.delete(rect)
                movement.rects.remove(rect)

        time += 1
        if time % 50 == 0:
            generate_row(movement, world, factory)

        if not last_score == time // 10:
            print("Score: {}".format(last_score))
        last_score = time // 10

        if player.sprite.position[1] == height_shift:
            running = False
            print("You graduated :(")

        sdl2.SDL_Delay(10)
        world.process()


if __name__ == "__main__":
    sys.exit(run())
