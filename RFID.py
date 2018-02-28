from pirc522 import RFID
import signal
import smbus
import _thread
import time
import RPi.GPIO as GPIO
import mysql.connector

# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1


def lcd_init():
    # Initialise display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)


def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command

    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)


def lcd_string(message, line):
    # Send string to display

    message = message.ljust(LCD_WIDTH, " ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)


def init_screen():
    # Main program block

    # Initialise display
    lcd_init()

    while True:
        # Send some test
        lcd_string("Datarch        <", LCD_LINE_1)
        lcd_string("Archaeology    <", LCD_LINE_2)

        time.sleep(3)

        # Send some more text
        lcd_string(">        Datarch", LCD_LINE_1)
        lcd_string(">    Archaeology", LCD_LINE_2)

        time.sleep(3)

def write_to_screen(isSuccess ,tag_id):
    if isSuccess:
        lcd_string("Register Success", LCD_LINE_1)
    else:
        lcd_string("Error",LCD_LINE_1)
    lcd_string(kart_uid, LCD_LINE_2)

def register(tag_id):
    try:
        connector = mysql.connector.connect(user="root", password="", host="localhost", database="datarch")
        cursor = connector.cursor()
        add_tag = ("INSERT INTO artifact(id) VALUES(%s)")
        #do insert
        cursor.execute(add_tag, tag_id)

        connector.commit()

        write_to_screen(True, tag_id)

        cursor.close()
        connector.close()

    except mysql.connector.Error as err:
        write_to_screen(False,tag_id)

def detect():
    #ledpin = 7 #gpio4
    #buzzerpin = 15 #gpio22
    #GPIO.setmode(GPIO.BOARD)
    #GPIO.setup(ledpin, GPIO.OUT)
    #GPIO.setup(buzzerpin, GPIO.OUT)

    rdr = RFID()
    util = rdr.util()
    util.debug = True
    print("Waiting for Tag...")
    rdr.wait_for_tag()
    (error, data) = rdr.request()

    if not error:
     print("Tag Detected!")

     (error, uid) = rdr.anticoll()
     if not error:
         #GPIO.output(ledpin, GPIO.HIGH)
         #GPIO.output(buzzerpin, GPIO.HIGH)
         #wait 0.1 seconds
         #time.sleep(100)
         #GPIO.output(ledpin, GPIO.LOW)
         #GPIO.output(buzzerpin, GPIO.LOW)
         kart_uid = str(uid[0])+" "+str(uid[1])+" "+str(uid[2])+" "+str(uid[3])+" "+str(uid[4])
         print(kart_uid)
         return kart_uid
try:
    _thread.start_new_thread(init_screen, ("Thread-1",2, ))
except:
    print("Error While Creating Thread")

while True:
    tag_id = detect()
    if tag_id!=null:
        register(tag_id)
    else:
        print("There was an error while reading tag")
