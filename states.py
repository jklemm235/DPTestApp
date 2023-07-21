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
        data = [1,2,3,]
        print("sending data: {}".format(data))
        self.send_data_to_coordinator(data,
                                      send_to_self = False,
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
                                          destination = self.id)
            noisedx2Data = self.await_data(n = 1,
                                           unwrap = True,
                                           is_json = True)
            print("got the following 2x noised data: {}".format(noisedx2Data))
            return "terminal"
        else:
            while True:
                time.sleep(3)
