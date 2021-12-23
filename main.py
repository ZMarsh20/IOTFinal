from tkinter import *

import socket
import threading
from time import sleep

global categorySelected, correct, passes, afterID, gameStarted

master = Tk()
lab = Label(master)
lab.pack()
correct = 0
passes = 0
gameStarted = False

HOST = '127.0.0.1'
PORT = 50000
end = False
category = ""
timer = 0.0
word = ""

def myThread(category):
    global end, timer, word, gameStarted
    try:
        value = 0
        gameStarted = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(category.encode("utf-8"))
            end = False
            while True:
                line = s.recv(1024).decode("utf-8")

                if line.isnumeric() and int(line) >= 600:
                    passAnswer()
                    currentWordLabel.config(
                        text="GAME OVER: Your Score: Correct: " + str(correct) + " Passes: " + str(passes))
                    timerLabel.config(text='0')
                    break
                if end:
                    s.sendall('0'.encode("utf-8"))
                    break
                else:
                    s.sendall('1'.encode("utf-8"))

                if line.isnumeric():
                    timer = 60 - (float(line)/10)
                    timer = round(timer, 1)

                else:
                    if line[1].isnumeric():
                        try:
                            value = int(line)
                        except:
                            value = -int(line[1])
                            word = line[2:]

                        if value + 2:
                            passAnswer()
                        else:
                            correctAnswer()
                    else:
                        word = line

                currentWordLabel.config(text=word.replace("_"," "))
                timerLabel.config(text=str(timer))

    except:
        print("Something failed. Please check base station and try again momentarily.")
    finally:
        gameStarted = False

def startButtonClicked():
    global categorySelected, timer, gameStarted, end, var, correct, passes
    categorySelected = var.get()
    pastWordsListBox.delete(0, "end")
    correct = 0
    passes = 0

    if gameStarted:
        end = True
        sleep(1)

    thread = threading.Thread(target=myThread, args=(var.get(),))
    thread.start()

def correctAnswer():
    global correct
    if gameStarted and timer > 0:
        correct += 1
        currentWord = currentWordLabel.cget("text")
        pastWordsListBox.insert("end", currentWord)
        pastWordsListBox.itemconfig(pastWordsListBox.size() - 1, {'fg': 'green'})

def passAnswer():
    global passes
    if gameStarted and timer > 0:
        passes += 1
        currentWord = currentWordLabel.cget("text")
        pastWordsListBox.insert("end", currentWord)
        pastWordsListBox.itemconfig(pastWordsListBox.size() - 1, {'fg': 'orange'})

def stopButtonClicked():
    global end
    end = True
    currentWordLabel.config(text="")
    timerLabel.config(text="")
    pastWordsListBox.delete(0, "end")


var = StringVar(master)
welcomeLabel = Label(master, text="Welcome to Arduino Heads Up!", font=("Helvetica", 16), fg="orange")
instructions = Label(master, text="Please select a category:", font=("Helvetica", 14))
currentWordLabel = Label(master, text="", font=("Helvetica", 35))
pastWordsListBox = Listbox(master, font=("Helvetica", 14), justify=CENTER, height = 25)
timerLabel = Label(master, text="", font=("Helvetica", 24))

startGameButton = Button(master, text="Start Game!", command=startButtonClicked)
stopGameButton = Button(master, text="Stop Game", command=stopButtonClicked)

var.set("adjective")
master.geometry("1000x1000")
categories = OptionMenu(master, var, "adjective", "brands", "celebrities", "clothes", "superheroes", "harry potter", "western cs")

timerLabel.pack()
welcomeLabel.pack()
instructions.pack()
categories.pack()
startGameButton.pack()
stopGameButton.pack()
currentWordLabel.pack()
pastWordsListBox.pack()

mainloop()
