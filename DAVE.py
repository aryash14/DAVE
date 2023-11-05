import tkinter as tk
import asyncio
import cv2
from PIL import Image, ImageTk
import time 
from gtts import gTTS
import os
from playsound import playsound
import speech_recognition as sr
import threading

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

api_key = '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'

class Model():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://llava.hliu.cc/")
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="component-8"]/div[3]/div/input')))
        self.image_input = self.driver.find_element(By.XPATH, '//*[@id="component-8"]/div[3]/div/input')
        self.prompt_input = self.driver.find_element(By.XPATH, '//*[@id="component-0"]/label/textarea')
        self.send_button = self.driver.find_element(By.XPATH, '//*[@id="component-23"]')

class App:
    def exec(self):
        self.loop = asyncio.get_event_loop()
        self.video = cv2.VideoCapture(0)
        self.model = Model()
        self.window = Window(self.loop, self.model, self.video)
        self.speech = Speech(self.window)

        params = {
            "prompt": "",
            "ready": False,
        }
        t1 = threading.Thread(target=self.speech.exec, name='t1', args =(params, ))
        t1.start()

        self.window.show(params)

class Speech():
    def __init__(self, window):
        self.window = window

    def exec(self, params):
        print("Here")
        r = sr.Recognizer()
        # the index would be your microphone
        #use this code to find index
        # for index, name in enumerate(sr.Microphone.list_microphone_names()):
        #     print(f"Microphone with name '{name}' found for index {index}")
        device_index = 6

        m = sr.Microphone(device_index = device_index)
        hotword = 'dave'

        with m as source:
            while True:
                r.adjust_for_ambient_noise(source)
                print("Waiting for %s" % hotword)
                start_audio = r.listen(source)
                start_txt = r.recognize_whisper_api(start_audio, api_key=api_key)
                
                if hotword in start_txt.lower(): 
                    break 

            print("What is your question?")
            r.adjust_for_ambient_noise(source)
            start_audio = r.listen(source)
            start_txt = r.recognize_whisper_api(start_audio, api_key=api_key)
            params["prompt"] = start_txt

        params["ready"] = True

class Window(tk.Tk):
    def __init__(self, loop, model, video):
        self.video = video
        self.model = model
        self.loop = loop

        self.root = tk.Tk()
        self.titleLabel = tk.Label(self.root, text = "DASZ")
        self.webcamLabel = tk.Label(self.root)
        self.promptLabel = tk.Label(self.root)
        self.responseLabel = tk.Label(self.root)
        self.response = ""
        
        self.titleLabel.pack()
        self.webcamLabel.pack()
        self.promptLabel.pack()
        self.responseLabel.pack()

    def show(self, params):
        while True:
            ret, self.image = self.video.read()
            b,g,r = cv2.split(self.image)
            img = cv2.merge((r,g,b))
            im = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=im) 
            self.webcamLabel["image"] = imgtk
            self.promptLabel["text"] = params["prompt"]
            self.responseLabel["text"] = self.response

            if params["ready"]:
                print("Here")
                t2 = threading.Thread(target=self.capture, name='t2', args=(params, ))
                t2.start()
                params["ready"] = False

            self.root.update()
            time.sleep(0)

    def say(self, text):
        tts = gTTS(text)
        tts_name = 'speech.wav'
        tts.save(tts_name)
        playsound(tts_name)

    def capture(self, params):

        cv2.imwrite("image.png", self.image)
        # update the path with your respective path
        self.model.image_input.send_keys("/home/shamar/Desktop/rpi/hackrpi/image.png")
        # prompt = f"""
        #         Your job is to help the visually impaired by answering the questions they ask given an image. Answer the question to the best of your ability. If you do not have enough information to answer a question, answer "I do not have enough information to answer that question." QUESTION: {params["prompt"]} ANSWER:
        #         """.strip()
        self.model.prompt_input.send_keys("Do i got left or right to get past this chair assuming i am right behind it?")
        self.model.send_button.click()

        response_xpath = '//*[@id="chatbot"]/div[2]/div[2]/div/div[2]/span/p'
            
        current_output = ''
        start = 0
        count = 0
        while True:
            current_output = None

            try:
                element = WebDriverWait(self.model.driver, 5).until(EC.presence_of_element_located((By.XPATH, response_xpath)))
                current_output = element.text
            except:
                current_output = None

            if current_output != None:
                self.response = current_output

                idx = current_output.rfind(".")
                if idx == -1:
                    time.sleep(0.1)
                    continue
                new_text = current_output[start:idx+1].strip()

                if count == 4:
                    break
                try:
                    self.say(new_text)
                except:
                    count += 1
                    time.sleep(0.1)
                    continue
                if idx + 1 == len(current_output):
                    break

                start = idx+1
                count = 0


App().exec()