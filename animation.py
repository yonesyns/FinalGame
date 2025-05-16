import pygame

class Animation:
    def __init__(self, frames, frame_duration, loop=True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame_index = 0  # Renamed for clarity
        self.timer = 0
        self.done = False
    
    def update(self):
        if not self.done:
            self.timer += 1
            if self.timer >= self.frame_duration:
                self.timer = 0
                self.current_frame_index += 1
                if self.current_frame_index >= len(self.frames):
                    if self.loop:
                        self.current_frame_index = 0
                    else:
                        self.current_frame_index = len(self.frames) - 1
                        self.done = True
    
    @property
    def current_frame(self):
        """Property to get current frame surface"""
        return self.frames[self.current_frame_index]
    
    def reset(self):
        self.current_frame_index = 0
        self.timer = 0
        self.done = False