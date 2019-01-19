# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# TSL2561
# This code is designed to work with the TSL2561_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Light?sku=TSL2561_I2CS#tabs-0-product_tabset-2

import smbus
import time
import argparse
import os
import threading
import paho.mqtt.client as mqtt

def thread2():

    # Get I2C bus
    bus = smbus.SMBus(1)

    # TSL2561 address, 0x39(57)
    # Select control register, 0x00(00) with command register, 0x80(128)
    #		0x03(03)	Power ON mode
    bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
    # TSL2561 address, 0x39(57)
    # Select timing register, 0x01(01) with command register, 0x80(128)
    #		0x02(02)	Nominal integration time = 402ms
    bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)


    while True:




          time.sleep(1)

          # Read data back from 0x0C(12) with command register, 0x80(128), 2 bytes
          # ch0 LSB, ch0 MSB
          data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)

          # Read data back from 0x0E(14) with command register, 0x80(128), 2 bytes
          # ch1 LSB, ch1 MSB
          data1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)

          # Convert the data
          ch0 = data[1] * 256 + data[0]
          ch1 = data1[1] * 256 + data1[0]

          # Output data to screen

          #print ("Full Spectrum(IR + Visible) :%d lux" %ch0)
          #print ("Infrared Value :%d lux" %ch1)
          print ("Visible Value :%d lux" %(ch0 - ch1))

          visible = ch0 - ch1

          client.publish(args.mqtt_topic_get_lux, str(visible), qos=0, retain=False)

def thread1():
    global client

    while True:

        client.on_connect = on_connect
        client.on_message = on_message

        try_to_connect = True

        while try_to_connect:
            try:
                client.connect(args.mqtt_server_ip, int(args.mqtt_server_port), 60)
                try_to_connect = False
                break
            except Exception as e:
                print(e)



        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        client.loop_forever()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe(args.mqtt_topic_set_temperature)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    pass

# Argparse
parser = argparse.ArgumentParser()
parser.add_argument("--mqtt_server_ip", help="")
parser.add_argument("--mqtt_server_port", help="")
parser.add_argument("--mqtt_topic_get_lux", help="")
args = parser.parse_args()


client = mqtt.Client()

t1= threading.Thread(target=thread1)
t2= threading.Thread(target=thread2)

t1.start()
time.sleep(1)
t2.start()
