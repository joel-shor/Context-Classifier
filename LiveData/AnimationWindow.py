from LiveData.WaveformReader import WaveformReader
from LiveData.EnvironmentReader import EnvironmentReader

class MainWin:
    ''' Object which updates the environment and waveform windows. '''
    def __init__(self, vl, room_shape, wv, cl, wv_iters):
        start_iter = min(vl['Iter num'])
        self.ER = EnvironmentReader(vl, room_shape,start_iter)
        self.WR = WaveformReader(wv,cl,wv_iters,start_iter)
        self.iter_num = 0
    
    def add_predictor(self, predictor):
        self.HMM = predictor
    
    def _make_prediction(self, actual_is_clockwise):
        ''' This is going to cheat and look into the future. '''
        cnt = self.ER.count
        
        prediction = self.HMM.predictions[cnt]
        
        if prediction == -1:
            self.predicted_counter.set_text('None')
        elif prediction == 1:
            self.predicted_counter.set_text('Clockwise')
        elif prediction == 0:
            self.predicted_counter.set_text('Counterclockwise')
        else:
            raise Exception
        if prediction == actual_is_clockwise:
            self.predicted_counter.set_color('g')
        else:
            self.predicted_counter.set_color('r')
    
    def update(self):
        #self.txt.set_text(self.iter_num)
        
        xs,ys,vxs,vys = self.ER.read()
        #context = is_clockwise(x,y,vx,vy)
        signal = self.WR.read()
        
        self.ER.draw(xs,ys,vxs,vys)
        self.WR.draw(signal)
        
        self.iter_num += 1
        
        return True
