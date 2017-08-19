"""The RC Ball Game!"""
import sys
import sdl2
import sdl2.ext

BACKGROUND = sdl2.ext.Color(0, 0, 0)
RC_GREEN = sdl2.ext.Color(61, 192, 108)
WHITE = sdl2.ext.Color(255, 255, 255)

UPRATE = 0
BALL_SPEED = 3


class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def process(self, world, componentsets):
        for velocity, sprite in componentsets:
            swidth, sheight = sprite.size
            sprite.x += velocity.vx
            sprite.y += velocity.vy

            sprite.x = max(self.minx, sprite.x)
            sprite.y = max(self.miny, sprite.y)

            if sprite.x + swidth > self.maxx:
                sprite.x = self.maxx - swidth
            if sprite.y + sheight > self.maxy:
                sprite.y = self.maxy - sheight


class SoftwareRenderSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderSystem, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, BACKGROUND)
        super(SoftwareRenderSystem, self).render(components)


class TextureRenderSystem(sdl2.ext.TextureSpriteRenderSystem):
    def __init__(self, renderer):
        super(TextureRenderSystem, self).__init__(renderer)
        self.renderer = renderer

    def render(self, components):
        tmp = self.renderer.color
        self.renderer.color = BACKGROUND
        self.renderer.clear()
        self.renderer.color = tmp
        super(TextureRenderSystem, self).render(components)


class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0



class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0, score=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.playerscore= score
        self.velocity = Velocity()


class Rect(sdl2.ext.Entity):
    def __init__(self, world, sprite, posy=0):
        self.sprite = sprite
        self.sprite = posy


def run():
    print("starting")
    sdl2.ext.init()
    window = sdl2.ext.Window("The RC Ball Game!", size=(800, 600))
    window.show()

    if "-hardware" in sys.argv:
        print("Using hardware (gpu) acceleration")
        renderer = sdl2.ext.Renderer(window)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
    else:
        print("Using software rendering")
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    sp_rect = factory.from_color(RC_GREEN, size=(100, 20))
    sp_ball = factory.from_color(WHITE, size=(20, 20))

    world = sdl2.ext.World()

    movement = MovementSystem(0, 0, 800, 600)
    if factory.sprite_type == sdl2.ext.SOFTWARE:
        spriterenderer = SoftwareRenderSystem(window)
    else:
        spriterenderer = TextureRenderSystem(renderer)

    world.add_system(movement)
    world.add_system(spriterenderer)

    player = Player(world, sp_ball, 0, 250)
    rect1 = Rect(world, sp_rect, 290)

    running = True
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    player.velocity.vx = -BALL_SPEED
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    player.velocity.vx = BALL_SPEED
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT):
                    player.velocity.vx = 0
        sdl2.SDL_Delay(10)
        world.process()


if __name__ == "__main__":
    sys.exit(run())
