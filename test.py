from bci_controller import controller

if __name__ == "__main__":
    controller = controller("/home/ramtin/Code/BCI-Drone-Project/model.h5")
    controller.start(True)
