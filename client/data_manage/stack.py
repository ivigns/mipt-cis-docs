from collections import deque


class Stack(deque):
    def __init__(self, values):
        super().__init__(values)

    def push(self, item):
        self.append(item)

    def top(self):
        return self[-1]

    def empty(self):
        return not self
