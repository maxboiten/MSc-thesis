from ipywidgets import widgets
from IPython.display import display, clear_output, HTML
import json

class codingTool:
    '''
    Class that contains an interactive coding tool for Jupyter Notebook.

    Run .code() method to start coding
    '''
    
    def __init__(self, to_code, categories):
        '''
        Creates an instance of codingTool

        keyword arguments:
        to_code -- An iterable object (e.g. list) with elements to code
        categories -- An iterable object with coding categories
        '''
        
        self.coded = dict()
        
        self.to_code = list(to_code)
        
        self.at_item = 0
        self.categories = list(categories)
        
        self.options = widgets.ToggleButtons(
            options= self.categories,
            value = None,
            description= '',
            disabled=False,
            button_style='',
            tooltips=['Description of slow', 'Description of regular', 'Description of fast']
        )
        self.options.layout.align_self = 'center'
        
        self.item = widgets.Label(value = self.to_code[0])
        self.item.layout.align_self = 'center'
        
        self.next = widgets.Button(description = 'Next')
        self.next.on_click(self.next_clicked)
        
        self.previous = widgets.Button(description = 'Previous')
        self.previous.on_click(self.previous_clicked)
        
        self.stop = widgets.Button(description = 'Stop coding')
        self.stop.on_click(self.stop_clicked)
        
        bottom_rule = widgets.HBox([self.previous,self.next,self.stop])
        bottom_rule.layout.justify_content = 'space-between'
        
        self.tool = widgets.VBox([self.item,self.options,bottom_rule])
        self.tool.layout.justify_content = 'space-around'
        
    def code(self):
        '''
        Open the coding app
        '''
        if self.at_item == len(self.to_code):
            print("All items are already coded.")
        else:
            display(self.tool)
            display(HTML('''<style>.widget-label{ font-size: 32px; }</style>'''))
    
    def previous_clicked(self, b):
        '''
        Response function to event of Previous button being clicked
        '''
        if self.at_item > 0:
            self.at_item -= 1
            
            self.options.value = self.coded[self.to_code[self.at_item]]
            self.options.description = self.to_code[self.at_item]
    
    def next_clicked(self, b):
        '''
        Response function to event of Next button being clicked
        '''
        self.coded[self.to_code[self.at_item]] = self.options.value
        
        self.at_item += 1 
        if self.at_item == len(self.to_code):
            clear_output()
            print('Done!')
        else:     
            self.options.value = None
            self.options.description = self.to_code[self.at_item]
    
    def stop_clicked(self, b):
        '''
        Response function to event of Stop button being clicked
        '''
        clear_output()
    
    def to_json(self, fname):
        '''
        Saves object in a json file to continue later

        keyword arguments:
        fname -- filename for json file
        '''
        class_dict = {
            'coded' : self.coded,
            'to_code' : self.to_code,
            'at_item' : self.at_item,
            'categories' : self.categories
        }

        with open(fname,'w+') as f:
            json.dump(class_dict,f)

def from_json(json_str):
    ''' 
    Reads json files to continue coding.

    Keyword arguments:
    json_str -- A read json file returned by the `to_json` method from codingTool
    ''' 
    class_dict = json.loads(json_str)

    coding_object = codingTool(class_dict['to_code'],class_dict['categories'])
    coding_object.coded = class_dict['coded']

    coding_object.at_item = class_dict['at_item']
    coding_object.options.description = coding_object.to_code[coding_object.at_item]

    return coding_object
