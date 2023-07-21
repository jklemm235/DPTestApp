from FeatureCloud.app.engine.app import AppState, app_state, Role, DPNoisetype
import time

# FeatureCloud requires that apps define the at least the 'initial' state.
# This state is executed after the app instance is started.
@app_state('initial')
class InitialState(AppState):

    def register(self):
        self.register_transition('getValue', Role.BOTH)

    def run(self):
        self.configure_dp(epsilon = 0.9, delta =  0.1,
                     sensitivity = 10,
                     clippingVal = None,
                     noisetype = DPNoisetype.GAUSS)
        data = [1,2,3]
        print("sending data: {}".format(data))
        self.send_data_to_coordinator(data,
                                      send_to_self = True,
                                      use_smpc = False,
                                      use_dp = True)
        return 'getValue'

@app_state('getValue')
class getValue(AppState):

    def register(self):
        self.register_transition('terminal', Role.BOTH)

    def run(self):
        if self.is_coordinator:
            aggNoisedData = self.aggregate_data(use_smpc = False,
                                                use_dp = True)
            print("got the following noised and aggregated data: {}".format(
                aggNoisedData))
            print("noising data again")
            self.send_data_to_participant(aggNoisedData,
                                          destination = self.id,
                                          use_dp = True)
            noisedx2Data = self.await_data(n = 1,
                                           unwrap = True,
                                           is_json = True)
            print("got the following 2x noised data: {}".format(noisedx2Data))
            print("broadcasting data")
            self.broadcast_data(noisedx2Data,
                                send_to_self = True,
                                use_dp = True)
            time.sleep(15)
            return "terminal"
        else:
            noisedx3Data = self.await_data(n = 1,
                                           unwrap = True,
                                           is_json = False)
            print("got the following 3x noised data from broadcast: {}".format(
                noisedx3Data))
            while True:
                time.sleep(5)
