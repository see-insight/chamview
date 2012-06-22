class BaseChooser(object):

    def setup(self):
        #Called by ChamView before the plugin has to do anything. Create GUI
        #elements, etc. here
        raise NotImplementedError

    def teardown(self):
        #Called to allow the plugin to free any resources or delete temporary
        #files
        raise NotImplementedError

    def choose(self,stack,predicted):
        #Determine which predicted point to use. 'predicted' is in the format
        #[predictor name][point kind][row,column,confidence]. Must return one of
        #the predictor names from 'predicted'
        raise NotImplementedError

