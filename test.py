from bci_controller import controller

if __name__ == "__main__":
    controller = controller("/home/ram/Code/BCI_project/PipeLine/model.h5")
    controller.start(True)
