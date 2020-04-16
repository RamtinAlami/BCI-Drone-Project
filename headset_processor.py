import threading
from multiprocessing import Queue
from time import sleep

import numpy as np

from tensorflow import keras


class data_stream:
    def __init__(self):
        # This is the queue that data will be added to after processing
        self.buffer_queue = Queue()
        self.processed_queue = Queue()

    def pre_process(self):
        # This is a function that will be applied to all the 100 milisecond data to preprocess
        # This needs to be in a sepeate process
        raise NotImplementedError

    def connect(self):
        # Connect to headset and setup a thread for the IO that will had a cut function as
        raise NotImplementedError

    def data_processor(self):
        print("Starting the data stream thread...")
        while True:
            raise NotImplementedError

    def data_processor_runner(self):
        # May need to change to multiproccessing if data_processor is heavy on CPU
        processor_thread = threading.Thread(target=self.data_processor)
        processor_thread.setDaemon(True)
        processor_thread.start()


class dev_data_stream(data_stream):
    def __init__(self):
        super().__init__()
        feature_file = "/home/ram/Code/BCI_project/PipeLine/EEG_hand_squeeze/patient_B_features.csv"
        label_file = (
            "/home/ram/Code/BCI_project/PipeLine/EEG_hand_squeeze/patient_B_classes.csv"
        )
        input_shape = (62, 100, 1)
        self.X, self.Y = self.fake_data_input(feature_file, label_file, input_shape)
        self.data_processor_runner()

    def fake_data_input(self, feature_file, label_file, input_shape):
        print("Opening files for sample data...")
        X = np.transpose(np.loadtxt(feature_file, delimiter=","))
        Y = np.loadtxt(label_file, delimiter=",")

        signal_duration = input_shape[1]
        num_EEG_channels = input_shape[0]

        if keras.backend.image_data_format() == "channels_first":
            X = X.reshape(X.shape[0], 1, num_EEG_channels, signal_duration)
        else:
            X = X.reshape(X.shape[0], num_EEG_channels, signal_duration, 1)

        Y = Y.reshape(Y.shape[0], 1)
        Y = Y - 1  # shifting the indices

        index = np.argwhere(Y == 0)

        index = index[:, 0]
        Y = Y - 1

        X = np.delete(X, index, 0)
        Y = np.delete(Y, index, 0)
        print("Done with sample data")
        return X, Y

    def data_processor(self):
        print("Starting the data stream thread...")
        while True:
            rand_indx = np.random.randint(0, self.X.shape[0])
            self.processed_queue.put(self.X[rand_indx])
            print(str(self.Y[rand_indx][0]) + " <- real class")
            sleep(1.5)
