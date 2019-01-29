# isort:skip_file

from trezor import ui, io


ui.display.backlight(ui.BACKLIGHT_NORMAL)
#ui.display.backlight(ui.BACKLIGHT_NORMAL)

d = ui.display

d.print("UART Test\n")
d.print("---------\n")

d.print("Init UART... ")

uart = io.SBU()
uart.set_uart(True)
d.print("Done\n")

uart.write("UART Initialized\r\n")
uart.write("Reading and echo\r\n")

while True:
    b = bytearray(4)
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
        except Exception as e:
            uart.write("Exception: {0}".format(e))
            d.print(str(e))
    else:
        uart.write("Receive error\r\n")

