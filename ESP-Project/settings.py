import gc
import json
import os
class Settings():
    # mode 'session','toss'
    def __init__(self,set=None, val=None):
        self.set = set
        self.val = val 
        if 'settings.json' in os.listdir():    
            gc.collect()
            with open('settings.json') as f:
                self.data = json.load(f)
                if val==None:
                    try:
                        val = self.data[set]
                    except:
                        # json.dump({set: val}, f)
                        self.data[set] = val
                        # json.dump(self.data, f)
                        self.set(val)
                    f.close()
                else:
                    self.val = val      
            self.set = set  
            self.val = val
            print(f"set '{set}' {val}")
        else:
            with open('settings.json', 'w') as f:
                json.dump({set: val}, f)
                f.close()
            gc.collect()
            self.val = val        
        
    @property
    def get(self):
        return self.val

    def change(self):
        if self.val == None :
            print('No Change Value Indicated')
            return
        print(f'Changing {self.set} to {self.val}')
        with open('settings.json', 'w') as f:
            self.data[self.set] = self.val
            json.dump(self.data, f)
            f.close()
        gc.collect()
        print(f"Set {self.set} to {self.val}")
        self.val = self.val
        return self.val