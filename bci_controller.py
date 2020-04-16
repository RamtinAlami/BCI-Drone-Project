import multiprocessing
import threading

import numpy as np

from headset_processor import data_stream, dev_data_stream
from tello import Tello
from tensorflow import keras


class controller:
    def __init__(self, h5_model_location):
        self.tello = Tello()
        self.h5_model_location = h5_model_location

    def start(self, dev_mode=False):
        if dev_mode:
            self.fit_input_queue = dev_data_stream().processed_queue
        else:
            self.fit_input_queue = data_stream().processed_queue

        self.fit_output_queue = multiprocessing.Queue()
        self.run_fitter()
        self.run_tello_thread()

    def run_tello_thread(self):
        print("Starting the tello thread...")
        tello_thread = threading.Thread(target=self.tello_commander)
        tello_thread.daemon = True
        tello_thread.start()

    def emergency_land(self):
        self.tello.emergency_land()

    def tello_commander(self):
        # add assertion
        while True:
            code = self.fit_output_queue.get()
            self.tello_decode_code(code)

    def tello_decode_code(self, code):
        command_bindings = {
            0: self.tello.forward,
            1: self.tello.backward,
            2: self.tello.right,
            3: self.tello.left,
            4: self.tello.takeoff,
            5: self.tello.land,
        }
        command = command_bindings.get(code)
        print("command sent to drone!\n")
        command()

    def run_fitter(self):
        print("starting the fitter process...")
        fitter_process = multiprocessing.Process(
            target=self.fit_signal,
            args=(self.fit_input_queue, self.fit_output_queue, self.h5_model_location),
        )
        fitter_process.daemon = True
        fitter_process.start()

    def fit_signal(self, fit_input_queue, fit_output_queue, h5_model_location):
        print("loading model...")
        model = keras.models.load_model(h5_model_location)
        print("Done loading the model")
        while True:
            signal = fit_input_queue.get()
            signal = signal.reshape(tuple([1] + list(signal.shape)))
            tello_code = int((model.predict(signal)[0] > 0.5)[0])
            fit_output_queue.put(tello_code)
            print(str(tello_code) + " <- Predicted")
