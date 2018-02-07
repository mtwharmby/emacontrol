class EmaApi:
    def __init__(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def mount_sample(self, n):
        return self.mount_samples([n])

    def mount_samples(self, mn):
        pass

    def unmount_sample(self):
        pass

    def clear_sample(self):
        pass

    def make_safe(self):
        pass


class EmaException(Exception):
    """
    A base class for all custom exceptions that might be thrown from the EMA
    classes
    """
    def __init__(self, msg=None, *args):
        if msg is None:
            msg = "An error occurred executing EMA motion"
        super().__init__(msg, *args)