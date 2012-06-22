
import Stack
import Predictor
import Chooser
import inspect


#predictor[]
#chooser[]



#Returns True if the given object has the proper methods for a Predictor
def verify_predictor(test):
    if inspect.ismethod(test.init) == False: return False
    if inspect.ismethod(test.predict) == False: return False
    return True


#Returns True if the given object has the proper methods for a Chooser
def verify_chooser(test):
    if inspect.ismethod(test.init) == False: return False
    if inspect.ismethod(test.choose) == False: return False
    return True

