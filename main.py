"""The RCade Ball Game!"""
import sys
import sdl2
import sdl2.ext
import random
import math

SCALE = 2
BACKGROUND = sdl2.ext.Color(0,0,0)
RC_GREEN = sdl2.ext.Color(61,192,108)
WHITE = sdl2.ext.Color(255,255,255)

W_HEIGHT = 1500//SCALE
W_WIDTH = 1200//SCALE
G_HEIGHT = 600//SCALE
G_WIDTH = 800//SCALE

width_shift = 200//SCALE
height_shift = 200//SCALE

static_components = []

UPRATE = -1//SCALE
DOWNRATE = 5//SCALE
HORIZ_SPEED = 3//SCALE


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

            if sprite not in static_components:
                sprite.x = max(self.minx,sprite.x)
                sprite.y = max(self.miny,sprite.y)

                if sprite.x + swidth > self.maxx:
                    sprite.x = self.maxx - swidth
                if not sprite == self.player.sprite:
                    if sprite.y + sheight > self.maxy:
                        sprite.y = self.maxy - sheight
                else:
                    if sprite.y + sheight > (self.maxy - 10):
                        sprite.y = self.maxy - 10 - sheight


class SoftwareRenderSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self,window):
        super(SoftwareRenderSystem,self).__init__(window)

    def render(self,components):
        sdl2.ext.fill(self.surface,BACKGROUND)
        super(SoftwareRenderSystem,self).render(reversed(components))


class TextureRenderSystem(sdl2.ext.TextureSpriteRenderSystem):
    def __init__(self,renderer):
        super(TextureRenderSystem,self).__init__(renderer)
        self.renderer = renderer

    def render(self,components):
        tmp = self.renderer.color
        self.renderer.color = BACKGROUND
        self.renderer.clear()
        self.renderer.color = tmp
        super(TextureRenderSystem,self).render(reversed(components))


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
        self.sprite.position = posx, posy
        self.velocity = Velocity()


def generate_row(movement,world,factory,y=G_HEIGHT//100):
    num_gaps = random.randint(1,5)
    for j in range(0,num_gaps):
        min_x = j * G_WIDTH // num_gaps
        gap_width = 20 + random.randint(0,10)
        l_padding = random.randint(1,G_WIDTH//num_gaps - gap_width-1)
        r_width = math.ceil(G_WIDTH/num_gaps - l_padding - gap_width)

        movement.rects.append(Rect(
            world,
            factory.from_color(RC_GREEN,size=(l_padding,20//SCALE)),
            (min_x+width_shift),
            y*100+height_shift+50))
        movement.rects.append(Rect(
            world,
            factory.from_color(RC_GREEN,size=(r_width,20//SCALE)),
            min_x+l_padding+gap_width+width_shift,
            y*100+height_shift+50))

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("RCade Falldown!",size=(W_WIDTH,W_HEIGHT))
    window.show()

    if "-software" in sys.argv:
        print("Using software rendering")
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    else:
        print("(Default) Using hardware acceleration")
        renderer = sdl2.ext.Renderer(window)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE,renderer=renderer)

    world = sdl2.ext.World()

    movement = MovementSystem(width_shift,-10+height_shift,400+width_shift,310+height_shift)
    if factory.sprite_type == sdl2.ext.SOFTWARE:
        spriterenderer = SoftwareRenderSystem(window)
    else:
        spriterenderer = TextureRenderSystem(renderer)

    world.add_system(movement)
    world.add_system(spriterenderer)

    outer_top = Rect(world,factory.from_color(WHITE,size=(1200//SCALE,20//SCALE)),0//SCALE,0//SCALE)
    static_components.append(outer_top.sprite)
    outer_bottom = Rect(world,factory.from_color(WHITE,size=(1200//SCALE,20//SCALE)),0//SCALE,(1500-200)//SCALE)
    static_components.append(outer_bottom.sprite)
    outer_left = Rect(world,factory.from_color(WHITE,size=(20//SCALE,1500//SCALE)),0//SCALE,0//SCALE)
    static_components.append(outer_left.sprite)
    outer_right = Rect(world,factory.from_color(WHITE,size=(20//SCALE,1500//SCALE)),(1200-20)//SCALE,0//SCALE)
    static_components.append(outer_right.sprite)
    border_rect_top = Rect(world,factory.from_color(WHITE,size=(1000//SCALE,100//SCALE)),100//SCALE,100//SCALE)
    static_components.append(border_rect_top.sprite)
    border_rect_bottom = Rect(world,factory.from_color(WHITE,size=(1000//SCALE,100//SCALE)),100//SCALE,800//SCALE)
    static_components.append(border_rect_bottom.sprite)
    border_rect_left = Rect(world,factory.from_color(WHITE,size=(100//SCALE,600//SCALE)),100//SCALE,200//SCALE)
    static_components.append(border_rect_left.sprite)
    border_rect_right = Rect(world,factory.from_color(WHITE,size=(100//SCALE,600//SCALE)),1000//SCALE,200//SCALE)
    static_components.append(border_rect_right.sprite)
    base_mid_left = Rect(world,factory.from_color(WHITE,size=(200//SCALE,100//SCALE)),200//SCALE,1000//SCALE)
    static_components.append(base_mid_left.sprite)
    base_mid_right = Rect(world,factory.from_color(WHITE,size=(200//SCALE,100//SCALE)),800//SCALE,1000//SCALE)
    static_components.append(base_mid_right.sprite)
    base_mid_right2 = Rect(world,factory.from_color(WHITE,size=(30//SCALE,100//SCALE)),970//SCALE,1100//SCALE)
    static_components.append(base_mid_right2.sprite)
    # base_lower_left = Rect(world,factory.from_color(WHITE,size=(100,200)),100,1100)
    # static_components.append(base_lower_left.sprite)
    # base_lower_right = Rect(world,factory.from_color(WHITE,size=(100,200)),1000,1100)
    # static_components.append(base_lower_right.sprite)
    # base_lower_left2 = Rect(world,factory.from_color(WHITE,size=(100,200)),0,1200)
    # static_components.append(base_lower_left2.sprite)

    player = Player(world,factory.from_color(WHITE,size=(20//SCALE,20//SCALE)),(390+width_shift)//SCALE,(270+width_shift)//SCALE)
    movement.player = player

    for y in range(0,(G_HEIGHT)//100):
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

            _,posy = rect.sprite.position
            if posy == -20 + height_shift:
                movement.rects.remove(rect)

        time += 1
        if time % 50 == 0:
            generate_row(movement,world,factory)

        if player.sprite.position[1] == height_shift:
            running = False

        sdl2.SDL_Delay(10)
        world.process()


if __name__ == "__main__":
    sys.exit(run())
