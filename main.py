"""The RC Ball Game!"""
import sys
import sdl2
import sdl2.ext
import random

BACKGROUND = sdl2.ext.Color(0,0,0)
RC_GREEN = sdl2.ext.Color(61,192,108)
WHITE = sdl2.ext.Color(255,255,255)

GHEIGHT = 600
GWIDTH = 800

UPRATE = -1
DOWNRATE = 2
HORIZ_SPEED = 3


class CollisionSystem(sdl2.ext.Applicator):
    def __init__(self,minx,miny,maxx,maxy):
        super(CollisionSystem,self).__init__()
        self.componenttypes = Velocity,sdl2.ext.Sprite
        self.player = None
        self.rects = []
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def _overlap(self,collitem):
        sprite = collitem[1]
        if sprite == self.player.sprite:
            return False

        left,top,right,bottom = sprite.area
        bleft,btop,bright,bbottom = self.player.sprite.area

        return (bleft < right and bright > left and
                btop < bottom and bbottom > top)

    def process(self,world,componentsets):
        collitems = [comp for comp in componentsets if self._overlap(comp)]
        if len(collitems) != 0:
            self.player.velocity.vy = UPRATE
        else:
            self.player.velocity.vy = DOWNRATE

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self,minx,miny,maxx,maxy):
        super(MovementSystem,self).__init__()
        self.componenttypes = Velocity,sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def process(self,world,componentsets):
        for velocity,sprite in componentsets:
            swidth,sheight = sprite.size
            sprite.x += velocity.vx
            sprite.y += velocity.vy

            sprite.x = max(self.minx,sprite.x)
            sprite.y = max(self.miny,sprite.y)

            if sprite.x + swidth > self.maxx:
                sprite.x = self.maxx - swidth
            if sprite.y + sheight > self.maxy:
                sprite.y = self.maxy - sheight


class SoftwareRenderSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self,window):
        super(SoftwareRenderSystem,self).__init__(window)

    def render(self,components):
        sdl2.ext.fill(self.surface,BACKGROUND)
        super(SoftwareRenderSystem,self).render(components)


class TextureRenderSystem(sdl2.ext.TextureSpriteRenderSystem):
    def __init__(self,renderer):
        super(TextureRenderSystem,self).__init__(renderer)
        self.renderer = renderer

    def render(self,components):
        tmp = self.renderer.color
        self.renderer.color = BACKGROUND
        self.renderer.clear()
        self.renderer.color = tmp
        super(TextureRenderSystem,self).render(components)


class Velocity(object):
    def __init__(self):
        super(Velocity,self).__init__()
        self.vx = 0
        self.vy = 0


class Player(sdl2.ext.Entity):
    def __init__(self,world,sprite,posx=0,posy=0,score=0):
        self.sprite = sprite
        self.sprite.position = posx,posy
        self.playerscore= score
        self.velocity = Velocity()


class Rect(sdl2.ext.Entity):
    def __init__(self,world,sprite,posx=0,posy=0):
        self.sprite = sprite
        self.sprite.position= posx ,posy
        self.velocity = Velocity()


def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("The RCade Ball Game!",size=(GWIDTH,GHEIGHT))
    window.show()

    if "-hardware" in sys.argv:
        print("Using hardware (gpu) acceleration")
        renderer = sdl2.ext.Renderer(window)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE,renderer=renderer)
    else:
        print("Using software rendering")
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    world = sdl2.ext.World()

    movement = MovementSystem(0,-20,800,620)
    collision = CollisionSystem(0,0,800,640)
    if factory.sprite_type == sdl2.ext.SOFTWARE:
        spriterenderer = SoftwareRenderSystem(window)
    else:
        spriterenderer = TextureRenderSystem(renderer)

    world.add_system(movement)
    world.add_system(collision)

    sp_rect1 = factory.from_color(RC_GREEN,size=(100,20))
    sp_rect2 = factory.from_color(RC_GREEN,size=(100,20))
    sp_platform = factory.from_color(RC_GREEN,size=(100,20))
    sp_ball = factory.from_color(WHITE,size=(20,20))

    world.add_system(spriterenderer)

    player = Player(world,sp_ball,390,270)
    collision.player = player
    # collision.rects.append(Rect(world,factory.from_color(RC_GREEN,size=(100,20)),390,290))
    # collision.rects.append(Rect(world,factory.from_color(RC_GREEN,size=(100,20)),530,290))

    for y in range(0,GHEIGHT//100):
        num_gaps = random.randint(1,5)
        for j in range(0,num_gaps):
            min_x = j * GWIDTH // num_gaps
            gap_width = 40 + random.randint(0,20)
            l_padding = random.randint(0,GWIDTH//num_gaps - gap_width)
            r_width = GWIDTH//num_gaps - l_padding - gap_width

            collision.rects.append(Rect(
                world,
                factory.from_color(RC_GREEN,size=(l_padding,20)),
                min_x,
                y*100))
            collision.rects.append(Rect(
                world,
                factory.from_color(RC_GREEN,size=(r_width,20)),
                min_x+l_padding+gap_width,
                y*100))
            # collision.rects.append(Rect(
            #     world,
            #     factory.from_color(RC_GREEN,size=(10,20)),
            #     10,
            #     10))
            # collision.rects.append(Rect(
            #     world,
            #     factory.from_color(RC_GREEN,size=(10,20)),
            #     10,
            #     10))

    running = True
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
                if event.key.keysym.sym in (sdl2.SDLK_LEFT,sdl2.SDLK_RIGHT):
                    player.velocity.vx = 0

        for rect in collision.rects:
            rect.velocity.vy = UPRATE
            if rect.sprite.position[1] == -20:
                collision.rects.remove(rect)

        if player.sprite.position[1] < 0:
            running = False

        sdl2.SDL_Delay(10)
        world.process()


if __name__ == "__main__":
    sys.exit(run())
