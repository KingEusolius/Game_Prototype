class Observer:
    def __init__(self):
        pass

    def on_event(self):
        pass


class Subject:
    def __init__(self):
        self.observer = []

    def notify_observer(self):
        for obs in self.observer:
            obs.on_event()

    def register_observer(self, obs):
        if obs not in self.observer:
            self.observer.append(obs)

    def remove_observer(self, obs):
        if obs in self.observer:
            self.observer.remove(obs)
