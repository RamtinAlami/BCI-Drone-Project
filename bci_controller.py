import threading
import multiprocessing
import numpy as np
from tensorflow import keras
from headset_processor import data_stream, dev_data_stream
from tello import Tello
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class controller:
    def __init__(self, h5_model_location):
        self.tello = Tello()
        self.last_brain_read = "NaN"
        self.h5_model_location = h5_model_location
        self.state = "Stand-by"

    def start(self, dev_mode=False):
        if dev_mode:
            self.fit_input_queue = dev_data_stream().processed_queue
        else:
            self.fit_input_queue = data_stream().processed_queue

        self.fit_output_queue = multiprocessing.Queue()
        self.run_fitter()
        self.run_tello_thread()

    def run_tello_thread(self):
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
        def temp_func(): self.state = "Running  "
        command_bindings = {
            0: self.tello.forward,
            1: self.tello.backward,
            2: self.tello.right,
            3: self.tello.left,
            4: self.tello.takeoff,
            5: self.tello.land,
            00: temp_func}
        command = command_bindings.get(code)
        command()

    def run_fitter(self):
        fitter_process = multiprocessing.Process(
            target=self.fit_signal,
            args=(self.fit_input_queue, self.fit_output_queue,
                  self.h5_model_location),
        )
        fitter_process.daemon = True
        fitter_process.start()

    def fit_signal(self, fit_input_queue, fit_output_queue, h5_model_location):
        model = keras.models.load_model(h5_model_location)
        # signalling start
        fit_output_queue.put(00)
        while True:
            signal = fit_input_queue.get()
            signal = signal.reshape(tuple([1] + list(signal.shape)))
            tello_code = int((model.predict(signal)[0] > 0.5)[0])
            fit_output_queue.put(tello_code)
