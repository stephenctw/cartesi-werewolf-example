import subprocess
import jsonpickle

class Network:

    def send_on_chain(self, payload):
        subprocess.check_output(['yarn', 'start', 'input', 'send', '--payload', payload])

    def inspect(self, payload):
        return jsonpickle.decode(
            subprocess.check_output(['yarn', 'start', 'inspect', '--payload', payload]))



