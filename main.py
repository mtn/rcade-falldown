"""The RCade Ball Game!"""
import sys
import sdl2
import sdl2.ext
import random
import math

BACKGROUND = sdl2.ext.Color(0,0,0)
RC_GREEN = sdl2.ext.Color(61,192,108)
WHITE = sdl2.ext.Color(255,255,255)

GHEIGHT = 600
GWIDTH = 800

UPRATE = -1
DOWNRATE = 5
HORIZ_SPEED = 3


class MovementSystem(sdl2.ext.Applicator):
    def __init__(self,minx,miny,maxx,maxy,player=None,rects=[]):
        super(MovementSystem,self).__init__()
        self.componenttypes = Velocity,sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.player = player
        self.rects = rects

    def will_collide(self,velocity):
        pleft,ptop,pright,pbottom = self.player.sprite.area
        for rect in self.rects:
            left,top,right,bottom = rect.sprite.area

            if pleft+velocity.vx < right and pright+velocity.vx > left and ptop+velocity.vy < bottom and pbottom+velocity.vy > top:
                return rect
        return None

    def process(self,world,componentsets):
        for velocity,sprite in componentsets:
            swidth,sheight = sprite.size
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
                        for y in reversed(range(UPRATE,DOWNRATE)):
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

            sprite.x = max(self.minx,sprite.x)
            sprite.y = max(self.miny,sprite.y)

            if sprite.x + swidth > self.maxx:
                sprite.x = self.maxx - swidth
            if not sprite == self.player.sprite:
                if sprite.y + sheight > self.maxy:
                    sprite.y = self.maxy - sheight
            else:
                if sprite.y + sheight > (self.maxy - 20):
                    # print("in here")
                    sprite.y = self.maxy - 20 - sheight


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


def generate_row(movement,world,factory,y=GHEIGHT-1//100):
    num_gaps = random.randint(1,5)
    for j in range(0,num_gaps):
        min_x = j * GWIDTH // num_gaps
        gap_width = 40 + random.randint(0,20)
        l_padding = random.randint(1,GWIDTH//num_gaps - gap_width-1)
        r_width = math.ceil(GWIDTH/num_gaps - l_padding - gap_width)

        movement.rects.append(Rect(
            world,
            factory.from_color(RC_GREEN,size=(l_padding,20)),
            min_x,
            y*100))
        movement.rects.append(Rect(
            world,
            factory.from_color(RC_GREEN,size=(r_width,20)),
            min_x+l_padding+gap_width,
            y*100))

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("The RCade Ball Game!",size=(GWIDTH,GHEIGHT))
    window.show()

    if "-software" in sys.argv:
        print("Using software rendering")
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    else:
        print("(Default) Using hardware acceleration")
        renderer = sdl2.ext.Renderer(window)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE,renderer=renderer)

    world = sdl2.ext.World()

    movement = MovementSystem(0,-20,800,620)
    if factory.sprite_type == sdl2.ext.SOFTWARE:
        spriterenderer = SoftwareRenderSystem(window)
    else:
        spriterenderer = TextureRenderSystem(renderer)

    world.add_system(movement)
    world.add_system(spriterenderer)

    player = Player(world,factory.from_color(WHITE,size=(20,20)),390,270)
    movement.player = player

    for y in range(0,(GHEIGHT+100)//100):
        generate_row(movement,world,factory,y)

    running = True
    time = 0
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

        for rect in movement.rects:
            # rect.velocity.vy = 0
            rect.velocity.vy = UPRATE

        time += 1
        if time % 100 == 0:
            generate_row(movement,world,factory)

        if player.sprite.position[1] < 0:
            running = False

        sdl2.SDL_Delay(10)
        world.process()


if __name__ == "__main__":
    sys.exit(run())
