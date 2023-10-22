import subprocess
import jsonpickle

class Network:

    def send_on_chain(self, payload, account_index):
        subprocess.check_output(['yarn', 'start', 'input', 'send', '--payload', payload, '--accountIndex', account_index])

    def inspect(self, payload, account_index):
        return jsonpickle.decode(
            subprocess.check_output(['yarn', 'start', 'inspect', '--payload', payload, '--accountIndex', account_index]))



