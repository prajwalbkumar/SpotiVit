# -*- coding: utf-8 -*-
'''doc_functions'''
__Title__ = " doc_functions"
__author__ = "romaramnani"
__doc__ = 'Functions on document to refer in main scripts.'

from Autodesk.Revit.DB          import *
from pyrevit                    import revit, forms, script
from Autodesk.Revit.UI          import TaskDialog
from Autodesk.Revit.DB          import WorksharingUtils
from System.Collections.Generic import List

output = script.get_output()

# Define a method to get the active document with a null check
def get_active_document():
    active_doc = revit.doc
    if active_doc is None:
        TaskDialog.Show("Active Document", "No active document found")
        return None
    else:
        TaskDialog.Show("Active Document", "Active Document Title: {}".format(active_doc.Title))
        return active_doc

def get_view_on_sheets(doc, view_types):
    # Define all possible view types for selection
    '''
    view_types = {
        'Floor Plans': ViewType.FloorPlan,
        'Reflected Ceiling Plans': ViewType.CeilingPlan,
        'Area Plans': ViewType.AreaPlan, 
        'Sections' : ViewType.Section, 
        'Elevations': ViewType.Elevation
    }
    '''
    # Show a dialog box for selecting desired view types
    selected_view_type_names = forms.SelectFromList.show(
        sorted(view_types.keys()),            # Sorted list of view type names
        title='Select View Types',                # Title of the dialog box
        multiselect=True                          # Allow multiple selections
    )
    if not selected_view_type_names:
        forms.alert("No view type was selected. Exiting script.", 
                    exitscript=True)
        
    selected_view_types = [view_types[name] 
                        for name in selected_view_type_names 
                        if name in view_types] # Convert the selected view type names to their corresponding ViewType enums

    if not selected_view_types:
        forms.alert("No view was selected. Exiting script.", 
                    exitscript=True)
        
    # Collect all views in the document
    views_collector = FilteredElementCollector(doc).OfClass(View)

    # Filter views by the selected types
    filtered_views = [view for view in views_collector 
                    if view.ViewType in selected_view_types 
                    and not view.IsTemplate]
    if not filtered_views:
        forms.alert("No views of the selected types were found in the document.", exitscript=True) # If no views found, show a message and exit

    # Collect all Viewport elements in the document
    viewports_collector = FilteredElementCollector(doc).OfClass(Viewport)
    views_on_sheets_ids = {viewport.ViewId for viewport in viewports_collector} # Get the IDs of all views that are placed on sheets
    filtered_views_on_sheets = [
        view for view in filtered_views
        if view.Id in views_on_sheets_ids  # Check that the view is placed on a sheet
    ]
    if not filtered_views_on_sheets:
        forms.alert("No views of the selected types were found on sheets in the document.", 
                    exitscript=True) # If no views found, show a message and exit
    view_dict = {view.Name: view for view in filtered_views_on_sheets} # Create a dictionary for view names and their corresponding objects

    # Show the selection window for the user to choose views
    selected_view_names = forms.SelectFromList.show(
        sorted(view_dict.keys()),          # Sort and display the list of view names
        title='Select Views',              # Title of the selection window
        multiselect=True                   # Allow multiple selections
    )

    if selected_view_names:
        # Get the selected views from the dictionary
        selected_views = [view_dict[name] for name in selected_view_names]
        
        # Output or perform actions with the selected views
        #for view in selected_views:
        #    print("Selected View: {}".format(view.Name))
    else:
        forms.alert("No views were selected.")
    
    return selected_views 

def filter_element_ownership(doc, collected_elements):
    owned_elements = []
    unowned_elements = []
    elements_to_checkout = List[ElementId]()

    for element in collected_elements:
        element_id = element.Id
        elements_to_checkout.Add(element_id)
        #print (type(element_id))

    if doc.IsWorkshared:
        WorksharingUtils.CheckoutElements(doc, elements_to_checkout)
        
        for element in collected_elements:    
            worksharingStatus = WorksharingUtils.GetCheckoutStatus(doc, element.Id)
            if not worksharingStatus == CheckoutStatus.OwnedByOtherUser:
                owned_elements.append(element)
    
            else:
                unowned_elements.append(element) 
        #print("owned : {}".format(owned_elements))
           
    else:
        owned_elements = collected_elements
        
    unowned_element_data = []
    if unowned_elements:
        for element in unowned_elements:
            try:
                unowned_element_data.append([output.linkify(element.Id), element.Category.Name.upper(), "REQUEST OWNERSHIP", WorksharingUtils.GetWorksharingTooltipInfo(doc, element.Id).Owner])
            except:
                pass
            
        #print("unowned : {}".format(unowned_elements))
        output.print_md("##⚠️ Elements Skipped ☹️") # Markdown Heading 2
        output.print_md("---") # Markdown Line Break
        output.print_md("❌ Make sure you have Ownership of the Elements - Request access. Refer to the **Table Report** below for reference")  # Print a Line
        output.print_table(table_data = unowned_element_data, columns=["ELEMENT ID", "CATEGORY", "TO-DO", "CURRENT OWNER"]) # Print a Table
        print("\n\n")
        output.print_md("---") # Markdown Line Break
    
    return owned_elements
