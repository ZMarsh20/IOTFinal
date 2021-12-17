import serial
from datetime import datetime
from time import sleep
import socket
import sqlite3
import select

HOST = '127.0.0.1'
PORT = 50000

def sendWord(word, conn):
    conn.sendall(word.encode("utf-8"))
    for c in word:
        mySerial.write(bytes(c.encode()))
    mySerial.write(bytes('\n'.encode()))

def setWords(category):
    db = sqlite3.connect("words.db")
    cursor = db.cursor()
    for row in cursor.execute('SELECT word FROM words WHERE category = "' + category + '" ORDER BY RANDOM();'):
        row = str(row)[2:-3]
        yield row


mySerial = serial.Serial("COM4", 57600, timeout=5)
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        try:
            word = setWords(conn.recv(1024).decode("utf-8"))
            s.settimeout(3)
            with conn:
                nextWord = next(word)
                sendWord(nextWord, conn)
                f = open(datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + ".csv", 'w')
                while True:
                    if int(conn.recv(8).decode("utf-8")):
                        input = mySerial.readline().decode("utf-8").strip()
                        if input == chr(5):
                            sendWord(nextWord, conn)
                            continue
                        conn.sendall(str(input).encode("utf-8"))
                        if int(input) >= 600:
                            f.write(nextWord.replace("_", " ") + " -> TIMED OUT")
                            break
                        if int(input) < 0:
                            f.write(nextWord.replace("_", " "))
                            if int(input)+2:
                                f.write(" -> PASS\n")
                            else:
                                f.write(" -> CORRECT\n")
                            nextWord = next(word)
                            sendWord(nextWord, conn)

                    else:
                        mySerial.write(bytes(chr(27).encode()))
                        break
        except:
            mySerial.write(bytes(chr(27).encode()))
            mySerial.close()
            mySerial = serial.Serial("COM4", 57600, timeout=5)
        finally:
            s.close()
            try:
                f.close()
            except:
                pass