from Animation.WaveformReader import WaveformReader
from Animation.EnvironmentReader import EnvironmentReader

class MainWin:
    ''' Object which updates the environment and waveform windows. '''
    
    def __init__(self, step):
        #self.iter_num = 0
        self.iter_num = 58000
        self.step = step
        self.ER = None
        self.WR = None
    
    def init_ER(self,vl, room_shape):
        self.start_iter = min(vl['Iter num'])
        self.ER = EnvironmentReader(vl, room_shape,self.start_iter)
        
    def init_WR(self, wv, cl, wv_iters):
        self.WR = WaveformReader(wv,cl,wv_iters,self.start_iter)
        
    def add_predictor(self, predictor):
        self.CPr = predictor
    
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
        
        if self.ER: xs,ys,vxs,vys = self.ER.read(iteration=self.iter_num)
        if self.WR: signal, spks = self.WR.read(iteration=self.iter_num)
        
        if self.ER: self.ER.draw(xs,ys,vxs,vys)
        if self.WR: self.WR.draw(signal, spks)
        
        self.iter_num += self.step
        
        if self.iter_num > 60000:
            return False
        else:
            return True
