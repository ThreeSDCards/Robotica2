class Ball:
    def __init__(self):
        self.old_pos = None
        self.new_pos = None

    def update(self, pos):
        self.old_pos = self.new_pos
        self.new_pos = pos

