from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton
from magicgui import magic_factory

"""
Qt Designer version
"""
from .flood_tool import Ui_MainWindow
from skimage.io import imread
from PyQt5.QtWidgets import QMainWindow

def flood_qt(image, delta):
    new_level = delta*85
    label_image = image <= new_level
    label_image = label_image.astype(int)*13 # label 13 is blue in napari
    return(label_image, new_level)

# Define the main window class
class Qt_Designer_flood(QMainWindow,  Ui_MainWindow):
    def __init__(self, napari_viewer):          # include napari_viewer as argument (it has to have this name)
        super().__init__()
        self.viewer = napari_viewer
        self.setupUi(self)                     # Initialize GUI
        
        self.label_layer = None                # stored label layer variable
        self.pushButton.clicked.connect(self._apply_delta)
    
    def _apply_delta(self):
        image = self.viewer.layers['napari_island'].data    # We use the layer name to find the correct image layer
        delta = self.doubleSpinBox.value()
        label, level = flood_qt(image, delta)
        if self.label_layer is None:
            self.label_layer = self.viewer.add_labels(label)
        else:
            self.label_layer.data = label
        self.horizontalSlider.setValue(level)
        
"""
magicgui version
"""
from magicgui import magicgui
from napari.types import ImageData, LabelsData
@magic_factory(delta={'label': 'Temperature Increase (Δ°C):', 
                                           'min': 0, 'max' : 3, 'step': 0.1},
               new_level={'label':'Sea Level (dm):', 'widget_type':'Slider',
                         'min': 0, 'max' : 255})
def flood_magic_factory(image: ImageData, delta: float=0, new_level: int=0) -> LabelsData: 
    new_level = delta*85
    label_image = image <= new_level
    label_image = label_image.astype(int)*13 # label 13 is blue in napari
    return(label_image)

"""
FunctionGui version
"""
from magicgui.widgets import FunctionGui
from napari.types import LayerDataTuple
def flood_fgui(image: ImageData, delta: float=0, new_level: int=0) -> LayerDataTuple: 
    new_level = delta*85
    label_image = image <= new_level
    label_image = label_image.astype(int)*13 # label 13 is blue in napari
    return((label_image, {'name': 'flood result','metadata': {'new_level':new_level}}))

class FunctionGui_flood(FunctionGui):
    def __init__(self):
        super().__init__(
          flood_fgui,
          call_button=True,
          layout='vertical',
          param_options={'delta':
                             {'label': 'Temperature Increase (Δ°C):', 
                              'min': 0, 'max' : 3, 'step': 0.1},
                        'new_level':
                            {'label':'Sea Level (dm):', 'widget_type':'Slider',
                             'min': 0, 'max' : 255}}
        )
        
    def __call__(self):
        label_image = super().__call__()
        new_level = round(label_image[1]['metadata']['new_level'])
        self.new_level.value = new_level

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return [Qt_Designer_flood, flood_magic_factory, FunctionGui_flood]
