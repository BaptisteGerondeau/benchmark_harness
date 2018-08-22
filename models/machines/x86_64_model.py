#!/usr/bin/env python3
from models.machines.MachineModel import MachineModel

class ModelImplementation(MachineModel):
    def __init__(self):
        super().__init__()
        self.arch = 'x86_64'
