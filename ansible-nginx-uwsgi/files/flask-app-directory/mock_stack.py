class MockStack:
    def __init__(self, input_stack=[]):
        self.stack = input_stack

    def get_values_list(self):
        return self.stack

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        self.stack.pop()

    def clear(self):
        self.stack = []

    def top(self):
        return self.stack[-1]

    def size(self):
        return len(self.stack)

    def empty(self):
        return self.size() == 0