# -*- coding: utf-8 -*-
'''dim_functions'''
__Title__ = " dim_functions"
__author__ = "romaramnani"

import clr
import os

clr.AddReference("System.Windows.Forms")
clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')

from System.Collections.ObjectModel import ObservableCollection
from System.Windows.Forms           import FolderBrowserDialog
from System.Windows                 import Window
from System.Windows.Controls        import Button
from Autodesk.Revit.DB              import *
from pyrevit                        import revit, forms, script

import Autodesk.Revit.DB            as DB

script_dir = os.path.dirname(__file__)
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document  # type: Document

class MultipleSlidersForm:
    def __init__(self):
        # Load the XAML window
        xaml_path = os.path.join(script_dir, 'Slider.xaml')
        self.window = forms.WPFWindow(xaml_path)

        # Attach event handlers
        self.window.equalValuesCheckBox.Checked += self.OnCheckBoxChecked
        self.window.equalValuesCheckBox.Unchecked += self.OnCheckBoxUnchecked

        try:
            self.window.Sl_left.ValueChanged += self.OnSliderValueChanged
            self.window.Sl_right.ValueChanged += self.OnSliderValueChanged
            self.window.Sl_top.ValueChanged += self.OnSliderValueChanged
            self.window.Sl_bottom.ValueChanged += self.OnSliderValueChanged
        except Exception as ex:
            print("Error while binding ValueChanged event:", ex)

        submit_button = self.window.FindName('Submit')
        submit_button.Click += self.submit_button_click

        self.window.ShowDialog()

    def OnCheckBoxChecked(self, sender, e):
        # Set all sliders to the value of Sl_left and disable other sliders
        value = self.window.Sl_left.Value
        self.window.Sl_right.Value = value
        self.window.Sl_top.Value = value
        self.window.Sl_bottom.Value = value

        self.window.Sl_right.IsEnabled = False
        self.window.Sl_top.IsEnabled = False
        self.window.Sl_bottom.IsEnabled = False

    def OnCheckBoxUnchecked(self, sender, e):
        # Enable all sliders
        self.window.Sl_right.IsEnabled = True
        self.window.Sl_left.IsEnabled = True
        self.window.Sl_top.IsEnabled = True
        self.window.Sl_bottom.IsEnabled = True

    def OnSliderValueChanged(self, sender, e):
        # If the checkbox is checked, synchronize all sliders
        if self.window.equalValuesCheckBox.IsChecked:
            value = sender.Value
            self.window.Sl_left.Value = value
            self.window.Sl_right.Value = value
            self.window.Sl_top.Value = value
            self.window.Sl_bottom.Value = value

    def submit_button_click(self, sender, e):
        # Close the window
        self.window.Close()

class DoubleSlidersForm:
    def __init__(self):
        # Load the XAML window
        xaml_path = os.path.join(script_dir, 'Double_slider.xaml')
        self.window = forms.WPFWindow(xaml_path)

        # Attach event handlers
        self.window.equalValuesCheckBox.Checked += self.OnCheckBoxChecked
        self.window.equalValuesCheckBox.Unchecked += self.OnCheckBoxUnchecked

        try:
            self.window.Sl_left.ValueChanged += self.OnSliderValueChanged
            self.window.Sl_right.ValueChanged += self.OnSliderValueChanged

        except Exception as ex:
            print("Error while binding ValueChanged event:", ex)

        submit_button = self.window.FindName('Submit')
        submit_button.Click += self.submit_button_click

        self.window.ShowDialog()

    def OnCheckBoxChecked(self, sender, e):
        # Set all sliders to the value of Sl_left and disable other sliders
        value = self.window.Sl_left.Value
        self.window.Sl_right.Value = value

        self.window.Sl_right.IsEnabled = False

    def OnCheckBoxUnchecked(self, sender, e):
        # Enable all sliders
        self.window.Sl_right.IsEnabled = True
        self.window.Sl_left.IsEnabled = True

    def OnSliderValueChanged(self, sender, e):
        # If the checkbox is checked, synchronize all sliders
        if self.window.equalValuesCheckBox.IsChecked:
            value = sender.Value
            self.window.Sl_left.Value = value
            self.window.Sl_right.Value = value

    def submit_button_click(self, sender, e):
        # Close the window
        self.window.Close()

class SliderData:
    def __init__(self, name, min_value, max_value, default_value, tick_frequency=1):
        self.Name = name
        self.Min = min_value
        self.Max = max_value
        self.Value = default_value
        self.TickFrequency = tick_frequency

class DynamicSliderForm:
    def __init__(self, slider_definitions):
        #Load the XAML window
        xaml_path = os.path.join(script_dir, 'Slider.xaml')
        self.window = forms.WPFWindow(xaml_path)

        self.sliders_container = self.window.FindName("SlidersContainer")
        if self.sliders_container is None:
            raise ValueError("SlidersContainer not found in XAML")

        self.sliders = []
        self.sliders_container.ItemsSource = self.sliders

        self.load_sliders(slider_definitions)

        #Attach event handlers
        self.window.equalValuesCheckBox.Checked += self.OnCheckBoxChecked
        self.window.equalValuesCheckBox.Unchecked += self.OnCheckBoxUnchecked

        submit_button = self.window.FindName('Submit')
        submit_button.Click += self.submit_button_click

        self.window.ShowDialog()
    
    def add_slider(self, name, min_value, max_value, default_value):
        self.sliders.Add(SliderData(name, min_value, max_value, default_value))

    def load_sliders(self, slider_definitions):
        for name, settings in slider_definitions.items():
            self.add_slider(name, settings["min"], settings["max"], settings["default"])

        slider_definitions = {
            "Left Offset": {"min": 0, "max": 100, "default": 15},
            "Right Offset": {"min": 0, "max": 100, "default": 20},
            "Top Offset": {"min": 0, "max": 100, "default": 10},
            "Bottom Offset": {"min": 0, "max": 100, "default": 25},
        }

    def on_checkbox_checked(self, sender, event):
        #Set all sliders to the same value
        if self.sliders.Count > 0:
            value = self.sliders[0].Value
            for slider in self.sliders:
                slider.Value = value
    
    def on_checkbox_unchecked(self, sender, event):
        pass

    def submit_button_click(self, sender, e):
        slider_values = {slider.Name: slider.Value for slider in self.sliders}
        #Close the window
        self.window.Close()

def convert_to_xyz(float_list):
    # Assuming the float_list contains coordinates in the order [X, Y, Z]
    if len(float_list) == 3:
        return DB.XYZ(float_list[0], float_list[1], float_list[2])
    else:
        forms.alert("List must contain exactly 3 float values.")   

def datum_points(datum_elements, view):
    start_points = []
    end_points = []
    datum_curves = []
    for datum_element in datum_elements:
        grid_curve = datum_element.GetCurvesInView(DB.DatumExtentType.ViewSpecific, view)  # Get the 2D extent curve of the grid line
        
        if grid_curve:
            for curve in grid_curve:
                start_points.append(curve.GetEndPoint(0))
                end_points.append(curve.GetEndPoint(1))
                datum_curves.append(curve)
        else:
            print("No curves found for the grid in the specified view.")

    # Ensure all points are XYZ objects
    start_points = [convert_to_xyz([point.X, point.Y, point.Z]) if not isinstance(point, DB.XYZ) else point for point in start_points]
    end_points = [convert_to_xyz([point.X, point.Y, point.Z]) if not isinstance(point, DB.XYZ) else point for point in end_points]

    return start_points, end_points, datum_curves