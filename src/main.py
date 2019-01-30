# isort:skip_file

from trezor import ui, io
from trezor.crypto import random
from utime import sleep_ms

ui.display.backlight(ui.BACKLIGHT_NORMAL)
ui.display.backlight(ui.BACKLIGHT_NORMAL)

d = ui.display

lcd_screen = ui.display
lcd_screen.clear()
lcd_screen.refresh()

d.print("UART test\n")
d.print("---------\n")

d.print("Init UART... ")

uart = io.SBU()
uart.set_uart(True)
d.print("Done\n")

uart.write("UART Initialized\r\n")

SWIDTH = 240
SHEIGHT = 240
TILE_WIDTH = 4

CTRL_SENS = 3

BEGIN_COORDS = [15, 15]
BEGIN_DIR = [1, 0]

class Tile(object):
    def draw(self, x, y, color=65534):
        for i in range(TILE_WIDTH):
            for j in range(TILE_WIDTH):
                lcd_screen.bar(x + i, y + j, 1, 1, color)

    def render(self):
        return [self.draw(*args) for args in self.points]


class Snake(Tile):
    def __init__(self, uart):
        self.head = BEGIN_COORDS
        self.direction = BEGIN_DIR
        self.points = [self.head]
        self.ctrl = uart

    def _read_dir(self):
        b = bytearray(1)
        if self.ctrl.read(b) < 1:
            return

        ch = bytes(b).decode()

        if ch == 'w':
            self.direction = [-1, 0]
        elif ch == 's':
            self.direction = [1, 0]
        elif ch == 'a':
            self.direction = [0, 1]
        elif ch == 'd':
            self.direction = [0, -1]
        x, y = self.direction
        x *= TILE_WIDTH
        y *= TILE_WIDTH
        return x, y

    def move(self):
        dx, dy = self._read_dir()
        hx = self.head[0] + dx
        hy = self.head[1] + dy
        self.head = [hx, hy]
        self.points.insert(0, self.head)
        self.points.pop()

    def eat(self):
        if len(self.points) == 1:
            newlast = self.head[:]
            newlast[0] -= (self.direction[0] * TILE_WIDTH)
            newlast[1] -= (self.direction[1] * TILE_WIDTH)
        else:
            plast, last = self.points[-2:]
            newlast = last[:]
            if plast[0] == last[0]:
                if plast[1] > last[1]:
                    newlast[1] -= TILE_WIDTH
                else:
                    newlast[1] += TILE_WIDTH
            else:
                if plast[0] > last[0]:
                    newlast[0] -= TILE_WIDTH
                else:
                    newlast[0] += TILE_WIDTH
        self.points.append(newlast)
        self.render()

    def _bite(self):
        return self.head in self.points[1:]

    def _fall_out(self):
        x, y = self.head
        out_width = x > SWIDTH + TILE_WIDTH or x < -TILE_WIDTH
        out_height = y > SHEIGHT + TILE_WIDTH or y < -TILE_WIDTH
        return  out_width or out_height

    def isdead(self):
        return self._fall_out() or self._bite()


class Apple(Tile):
    def __init__(self):
        self.fall()

    def fall(self):
        x = ((ord(random.bytes(1))*8)+ord(random.bytes(1))) % SWIDTH // TILE_WIDTH * TILE_WIDTH - 1
        y = ((ord(random.bytes(1))*8)+ord(random.bytes(1))) % SHEIGHT // TILE_WIDTH * TILE_WIDTH - 1
        self.points = [[x, y]]
        self.render()


def main():
    snake = Snake(uart)
    apple = Apple()

    while not snake.isdead():
        lcd_screen.clear()
        apple.render()
        snake.render()
        lcd_screen.refresh()
        sleep_ms(200)

        if snake.head == apple.points[0]:
            snake.eat()
            apple.fall()
            snake.render()
            lcd_screen.refresh()
        snake.move()

    lcd_screen.print("death...\n")
    sleep_ms(100)


#main()

while True:
    b = bytearray(1)
    r = uart.read(b)
    if r > 0:
        try:
            uart.write(bytes(b).decode())
            uart.write("\r\n")
            d.print("Received: {0}\n".format(bytes(b).decode()))
            if b[0] == 65:
                uart.write('\xba')
            elif b[0] == 66:
                uart.write('\xaa')
            elif b[0] == 67:
                uart.write("Running snake game")
                uart.write("Snake game\r\n")
                uart.write("Usage:\r\n")
                uart.write("Use buttons A and D\r\n")
                main()
        except Exception as e:
            uart.write("Exception: {0}".format(e))
            d.print(str(e))
    else:
        uart.write("Receive error\r\n")

