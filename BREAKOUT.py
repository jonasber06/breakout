import pygame as pg
import math as m
from random import randint as r

BREDDE = 800
HOYDE = 600
clock = pg.time.Clock()



class App:
    def __init__(self):
        self._seier = False
        self._trykket = False

        """
        gjør følgende
        1. initialiserer vindu og objekter for ball, paddle og blokkene
        2. håndterer kollisjoner ball/paddle og ball/blokker
        3. tegner oppdatert grafikk
        4. game loop
        
        """
        pg.init()
        self.vindu = pg.display.set_mode((BREDDE,HOYDE))
        self.vindu.fill((255,255,255))

        self.blokker = Blokker()
        self.paddle = Paddle()
        self.ball = Ball()
        self.score = 0
        pg.display.set_caption(f"score: {self.score}")

    def kollisjon_paddle(self):
        x_rekt = self.paddle.hent_xpos()
        y_rekt = self.paddle.hent_ypos()

        b = self.paddle.hent_b() #høyde og bredde som paddle har
        h = self.paddle.hent_h()

        x_ball = self.ball.xpos
        y_ball = self.ball.ypos

        # finner nærmeste punkt på paddle til sirkelens radius
        self.x1 = max(x_rekt, min(x_ball,x_rekt+b))
        self.y1 = max(y_rekt, min(y_ball,y_rekt+h))

        avstand = m.sqrt((x_ball - self.x1)**2+(y_ball-self.y1)**2)

        #snur om på retningen slik at ballen 'spretter'
        if avstand <= self.ball.r:
            self.ball.dy *= -1

    def kollisjon_blokk(self):
        blokker = self.blokker._hent_blokker()

        for block in blokker:

            x_rekt = block[0]
            y_rekt = block[1]

            x_ball = self.ball.xpos
            y_ball = self.ball.ypos

            b = ((BREDDE-10*11)/10)
            h = ((HOYDE)/3 - 10*7)/6

            x1 = max(x_rekt, min(x_ball,x_rekt+b))
            y1 = max(y_rekt, min(y_ball,y_rekt+h))

            avstand = m.sqrt((x_ball - x1)**2+(y_ball-y1)**2)

            if avstand <= self.ball.r:
                self.ball.dy *= -1

                self.score += 1
                print(f"score: {self.score}")
                pg.display.set_caption(f"score: {self.score}")

                self.blokker.fjern_blokk(block)

                #øker vanskelighetsgraden
                if self.score == 15:
                    self.ball.dx *= 1.3
                    self.ball.dy *= 1.3
                
                #60 poeng tilsvarer at alle blokkene er borte, og brettet er tomt.
                if self.score == 60:
                    self._seier = True

    def vunnet(self):
        #når alle blokkene er borte kjøres denne metoden, og spillet stoppes
        self.ball.dx = 0
        self.ball.dy = 0
        font = pg.font.SysFont(None,30)
        text = font.render(f'Gratulerer! Spillet er vunnet!', True, (0, 0, 0))        
        self.vindu.blit(text, (BREDDE // 2 -125, HOYDE // 2))
        pg.display.flip()
        pg.time.delay(3000)
    
    def render(self,vindu):
        vindu.fill((255,255,255))
        self.blokker.render(vindu)
        self.paddle.render(vindu)
        self.ball.render(vindu)

        #tekstinstruks for å starte spillet
        if not self._trykket:
            font = pg.font.SysFont(None,25)
            text = font.render(f'Trykk på piltast til høyre/venstre', True, (0, 0, 0))        
            self.vindu.blit(text, (BREDDE // 2 -125 , HOYDE // 2+50))

        pg.display.flip()

    def run(self): 
        self.blokker.lag_blokker()
        self.render(self.vindu)

        running = True
        while running: #gameloop
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False


            #slik begynner ikke spillet før spilleren har trykket på en av pilene
            if not self._trykket:
                if self.paddle._sjekk_trykket():
                    self.ball._begynn_bevegelse()
                    self._trykket = True
            
            if self._trykket:
                self.kollisjon_blokk()
                self.paddle.bevegelse()
                self.ball.kollisjon_vegg()
                self.kollisjon_paddle()
                self.ball.beveg()

                #dersom spilleren ikke klarer å holde ballen oppe
                if self.ball.ypos >= HOYDE:
                    running = False
                    print("game over") 
                

                            
                if self._seier:
                    #når spillet er vunnet, stoppes spill-loop, og det vises en gratulasjon på skjermen
                    running = False
                    self.vunnet()

            self.render(self.vindu) #oppdatering
            clock.tick(60) #60 fps


class Blokker:
    def __init__(self):
        self._blokker = []
    
    def lag_blokker(self):

        #genererer liste med [x,y] koordinater for blokkene
        kol = 10
        rad = 6
        mellomrom = BREDDE // 100                      

        self.b = BREDDE // 10
        self.h = HOYDE // 30
        for i in range(0,kol):       #kolonner
            x = mellomrom * (i+1) + i * self.b
            for k in range(0,rad):    #rader
                y = mellomrom * (k+1) + k * self.h
                self._blokker.append([x,y])


    def render(self,vindu):

        #tegner det som er i listen av blokkenes posisjoner
        #muliggjør også fjerning av blokker når de kollideres med.

        for blokk in self._blokker:
            x = blokk[0]
            y = blokk[1]

            pg.draw.rect(vindu,(0,255,0),pg.Rect(x,y,self.b,self.h))
    
    def _hent_blokker(self):
        return self._blokker
    
    def fjern_blokk(self,el):
        self._blokker.remove(el)

class Paddle:
    def __init__(self):

        self.b = BREDDE // 10
        self.h = HOYDE // 30
        self.ypos = HOYDE - self.h*2
        self.xpos = BREDDE // 2 - self.b/2
        self.farge = (255,0,0)
        self.fart = 7.5

    def bevegelse(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_RIGHT] and self.xpos + self.fart < BREDDE - self.b:
            self.xpos += self.fart

        if keys[pg.K_LEFT] and self.xpos > 0:
            self.xpos -= self.fart

    def _sjekk_trykket(self):
        keys = pg.key.get_pressed()


        if keys[pg.K_RIGHT] or keys[pg.K_LEFT]:
            return True
        return False
    
    def hent_b(self):
        return self.b
    
    def hent_h(self):
        return self.h
    
    def hent_xpos(self):
        return self.xpos
    
    def hent_ypos(self):
        return self.ypos

    def render(self,vindu):
        #b = ((BREDDE-10*11)/10)+10
        #h = ((HOYDE)/3 - 10*7)/6
        #pg.draw.rect(vindu,self.farge,pg.Rect(self.xpos,self.ypos,b,h))
        pg.draw.rect(vindu,self.farge,pg.Rect(self.xpos,self.ypos,self.b,self.h))
    
class Ball:
    def __init__(self):
        self.xpos = BREDDE // 2
        self.ypos = HOYDE // 2
        self.farge = (0,0,255)
        self.r = 10
        self.dx = 0
        self.dy = 0

    def beveg(self):
        self.xpos += self.dx
        self.ypos += self.dy

    def kollisjon_vegg(self):
        if self.xpos >= BREDDE or self.xpos <=0:
            self.dx *= -1
        
        if self.ypos <= 0:
            self.dy *= -1
    
    def kollisjon_paddle(self):
            self.dy *= -1

    def _begynn_bevegelse(self):
        self.dy = 4
        self.dx = 4 * (-1) ** r(1,2) #randint, slik at det er tilfeldig hvilken retning ballen begynner

    def _sjekk_bevegelse(self):
        if self.dy == 0:
            return False
        return True

    def render(self,vindu):
        pg.draw.circle(vindu,self.farge,(self.xpos,self.ypos),self.r)

a = App()
a.run()

