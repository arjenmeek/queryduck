from .exceptions import GeneralError

class CrunchyClient(object):

    def __init__(self, config):
        self.config = config

    def run(self, action, *params):
        func_name = 'action_{}'.format(action)
        if hasattr(self, func_name):
            func = getattr(self, func_name)
        else:
            raise GeneralError("No such action: {}".format(action))

        return func(*params)

    def action_hello(self, subject='World'):
        print("Hello {}!".format(subject))
