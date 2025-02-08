# -*- coding: utf-8 -*-
'''view_functions'''
__Title__ = " view_functions"
__author__ = "romaramnani"

# # Imports
import time
from pyrevit            import revit, forms, script
from Autodesk.Revit.DB  import *
from Extract.RunData    import get_run_data
from doc_functions      import filter_element_ownership
from dim_functions      import MultipleSlidersForm, DoubleSlidersForm

output = script.get_output()

def ensure_view_is_cropped(view):
    if isinstance(view, View):
        if not view.CropBoxActive:
            view.CropBoxActive = True

def get_grids_in_view(doc, view):
    # Filter to collect grids in the specific view
    grids_collector = FilteredElementCollector(doc, view.Id) \
                    .OfCategory(BuiltInCategory.OST_Grids) \
                    .WhereElementIsNotElementType()

    # Convert to a list and return the grids
    grids_in_view = list(grids_collector)

    if doc.IsWorkshared:
        owned_grids = filter_element_ownership(doc, grids_in_view)
        return owned_grids
    else: 
        return grids_in_view 

def align_grids(doc, selected_views):
    
    # Instantiate the form
    gaps = MultipleSlidersForm()

    # Retrieve slider values
    extension_distance_1 = gaps.window.Sl_left.Value
    extension_distance_2 = gaps.window.Sl_right.Value
    extension_distance_3 = gaps.window.Sl_top.Value
    extension_distance_4 = gaps.window.Sl_bottom.Value

    def new_point(exisiting_point, direction, bbox_curves, start_point = None):
        possible_points = []
        projected_points = []

        for curve in bbox_curves:
            if isinstance(curve, Curve):
                project = curve.Project(exisiting_point).XYZPoint
                projected_points.append(XYZ(project.X, project.Y, 0))

        exisiting_point = XYZ(exisiting_point.X, exisiting_point.Y, 0)

        try:
            for point in projected_points:
                if (exisiting_point - point).Normalize().IsAlmostEqualTo(direction) or (exisiting_point - point).Normalize().IsAlmostEqualTo(direction.Negate()):
                    possible_points.append(point)

            if start_point:
                if start_point.IsAlmostEqualTo(possible_points[0]):
                        new_point = possible_points[1]
                else:
                    new_point = possible_points[0]

            else:
                if point.DistanceTo(possible_points[0]) > point.DistanceTo(possible_points[1]):
                    new_point = possible_points[0]
                else:
                    new_point = possible_points[1]
        
            return new_point

        except:
            return exisiting_point

    try:
        t = Transaction(doc, "Align Grids")
        t.Start()

        start_time = time.time()

        manual_time = 108.4 

        total_grid_count = 0
        total_view_count = 0
        view_list_length =0

        for view in selected_views:

            grids_collector = get_grids_in_view(doc, view)
            s_factor = view.Scale

            gap_distance_1 = extension_distance_1/3 * s_factor/100
            gap_distance_2 = extension_distance_2/3 * s_factor/100
            gap_distance_3 = extension_distance_3/3 * s_factor/100
            gap_distance_4 = extension_distance_4/3 * s_factor/100

            bbox = view.CropBox

            corner1 = XYZ(bbox.Min.X - gap_distance_1, bbox.Min.Y - gap_distance_4, bbox.Min.Z)
            corner2 = XYZ(bbox.Max.X + gap_distance_2, bbox.Min.Y - gap_distance_4, bbox.Min.Z)
            corner3 = XYZ(bbox.Max.X + gap_distance_2, bbox.Max.Y + gap_distance_3, bbox.Min.Z)
            corner4 = XYZ(bbox.Min.X - gap_distance_1, bbox.Max.Y + gap_distance_3, bbox.Min.Z)

            # Create lines representing the bounding box edges
            line1 = Line.CreateBound(corner1, corner2)
            line2 = Line.CreateBound(corner2, corner3)
            line3 = Line.CreateBound(corner3, corner4)
            line4 = Line.CreateBound(corner4, corner1)

            # Create model curves in the active view
            bbox_curves = [line1, line2, line3, line4]

            # for line in bbox_curves:
            #     doc.Create.NewDetailCurve(view, line)

            floor_plan_views = ["FloorPlan", "CeilingPlan", "EngineeringPlan", "AreaPlan"]
            front_views = ["Elevation", "Section"]

            if str(view.ViewType) in floor_plan_views:

                # Number of Grids
                grid_list_length = 0

                # Convert all Grids to ViewSpecific Grids
                for grid in grids_collector:
                    grid.SetDatumExtentType(DatumEnds.End0, view, DatumExtentType.ViewSpecific)
                    grid.SetDatumExtentType(DatumEnds.End1, view, DatumExtentType.ViewSpecific)

                    # Get the curves of the grids
                    curves = grid.GetCurvesInView(DatumExtentType.ViewSpecific, view)
                    for curve in curves:
                        grids_view_curve = curve
                        # point = curve.GetEndPoint(0)
                        # plane = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, point)
                        # sketch_plane = SketchPlane.Create(doc, plane)
                        # model_line = doc.Create.NewModelCurve(Line.CreateBound(point, curve.GetEndPoint(1)), sketch_plane)
                    
                    start_point = grids_view_curve.GetEndPoint(0)
                    end_point = grids_view_curve.GetEndPoint(1)
                    direction = (end_point - start_point).Normalize()

                    
                    
                    new_start_point = new_point(start_point, direction, bbox_curves)
                    new_end_point = new_point(end_point, direction, bbox_curves, new_start_point)

                    new_start_point = XYZ(new_start_point.X, new_start_point.Y, start_point.Z)
                    new_end_point = XYZ(new_end_point.X, new_end_point.Y, end_point.Z)

                    new_grid_line = Line.CreateBound(new_start_point, new_end_point)

                    if not int(new_start_point.X) == int(corner2.X):
                        new_grid_line = new_grid_line.CreateReversed()
                    
                    if not int(new_start_point.Y) == int(corner3.Y):
                        new_grid_line = new_grid_line.CreateReversed()


                    grid.SetCurveInView(DatumExtentType.ViewSpecific, view, new_grid_line)
                    grid.HideBubbleInView(DatumEnds.End0, view)
                    # grid.HideBubbleInView(DatumEnds.End1, view)
                    grid.ShowBubbleInView(DatumEnds.End1, view)

                    grid_list_length += 1

                total_grid_count += grid_list_length

                    # plane = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, new_start_point)
                    # sketch_plane = SketchPlane.Create(doc, plane)
                    # model_line = doc.Create.NewModelCurve(new_grid_line, sketch_plane)

            elif str(view.ViewType) in front_views:

                # Initialize an empty list to store Z-values from crop region curves
                end_point_z = []

                # Retrieve the crop region 
                crop_manager = view.GetCropRegionShapeManager()
                crop_region = crop_manager.GetCropShape()
                
                # Explode curve loop into individual lines
                for curve_loop in crop_region:
                    #print(curve_loop)
                    for curve in curve_loop:
                        print(curve)
                        # Get Z value of all end points
                        end_point_z.append(curve.GetEndPoint(0).Z)

                #Sort Z value of end points
                end_point_z = sorted(end_point_z)
                #print(end_point_z)
            
                # Number of Grids
                grid_list_length = 0

                # Convert all Grids to ViewSpecific Grids
                for grid in grids_collector:
                    grid.SetDatumExtentType(DatumEnds.End0, view, DatumExtentType.ViewSpecific)
                    grid.SetDatumExtentType(DatumEnds.End1, view, DatumExtentType.ViewSpecific)
            
                    # Get the curves of the grids
                    curves = grid.GetCurvesInView(DatumExtentType.ViewSpecific, view)
                    for curve in curves:
                        grids_view_curve = curve

                    # Get start and end points of the grid curve 
                    start_point   = curve.GetEndPoint(0)
                    end_point     = curve.GetEndPoint(1)

                    # Modify the Z-values of the start and end points based on the crop region
                    start_point   = XYZ(start_point.X, start_point.Y, end_point_z[0] - gap_distance_4)
                    end_point     = XYZ(end_point.X, end_point.Y, end_point_z[-1] + gap_distance_3)

                    # Create a new grid line with the updated start and end points
                    new_grid_line = Line.CreateBound(start_point, end_point)

                    # Apply the new grid line to the grid in the view
                    grid.SetCurveInView(DatumExtentType.ViewSpecific, view, new_grid_line)

                    # Hide the bubble at one end of the grid in this view
                    grid.HideBubbleInView(DatumEnds.End0, view)

                    # Show bubble at the other end of the grid
                    grid.ShowBubbleInView(DatumEnds.End1, view)

                    grid_list_length += 1
                total_grid_count += grid_list_length

            ensure_view_is_cropped(view)
            view_list_length+= 1
        total_view_count += view_list_length

        #print("Successfully aligned {} grids in {} views".format(total_grid_count, total_view_count))

        t.Commit()

        end_time = time.time()
        runtime = end_time - start_time
                
        run_result = "Tool ran successfully"
        if total_grid_count:
            element_count = total_grid_count
        else:
            element_count = 0

        error_occured ="Nil"

        get_run_data('Align Grids link in Dimesnion Grids', runtime, element_count, manual_time, run_result, error_occured)
        
    except Exception as e:
    
        #t.RollBack()
        print("Error occurred: {}".format(str(e)))
        
        end_time = time.time()
        runtime = end_time - start_time

        error_occured = ("Error occurred: %s", str(e))    
        run_result = "Error"
        element_count = 0
        
        get_run_data('Align Grids link in Dimesnion Grids', runtime, element_count, manual_time, run_result, error_occured)

# def align_levels(doc, selected_views):
#     yty

def get_levels_in_view(doc, view):

    level_collector = FilteredElementCollector(doc, view.Id) \
                    .OfCategory(BuiltInCategory.OST_Levels) \
                    .WhereElementIsNotElementType().ToElements()

    collected_elements = level_collector

    if doc.IsWorkshared:
        owned_grids = filter_element_ownership(doc, collected_elements)
        return owned_grids
    else: 
        return collected_elements

def align_levels(doc, final_selected_views, header_data):
    
    gaps = DoubleSlidersForm()

    # Retrieve slider values
    gap_distance_1 = gaps.window.Sl_left.Value
    gap_distance_2 = gaps.window.Sl_right.Value

    try:
        # Start transaction to ensure all Revit modifications happen inside it
        t = Transaction(doc, "Align Levels")
        t.Start()

        start_time = time.time()

        manual_time = 108.4 

        skipped_views = []  # List to store names of skipped views
        total_level_count = 0
        total_view_count = 0
        view_list_length =0


        for view in final_selected_views:
            view_direction = view.ViewDirection.Normalize()
            right_direction = view.RightDirection

            # Determine if the view is a section or elevation
            if view.ViewType in [ViewType.Elevation, ViewType.Section]:
                # Initialize lists to store points
                crop_box_pts_x = []
                crop_box_pts_y = []
                crop_box_pts_z = []

                # Retrieve the crop region
                crop_manager = view.GetCropRegionShapeManager()
                crop_region = crop_manager.GetCropShape()

                # Explode curve loop into individual lines
                for curve_loop in crop_region:
                    for curve in curve_loop:
                        # Get XYZ coordinates of all end points
                        crop_box_pts_x.append(curve.GetEndPoint(0).X)
                        crop_box_pts_y.append(curve.GetEndPoint(0).Y)
                        crop_box_pts_z.append(curve.GetEndPoint(0).Z)

                # Sort crop box coordinates
                crop_box_x = sorted(crop_box_pts_x)
                crop_box_y = sorted(crop_box_pts_y)
                crop_box_z = sorted(crop_box_pts_z)

                min_pt = XYZ(crop_box_x[0], crop_box_y[0], crop_box_z[0])
                max_pt = XYZ(crop_box_x[-1], crop_box_y[-1], crop_box_z[-1])

                # Determine the depth direction based on the view direction

                # Case 1: (0.000000000, -1.000000000, 0.000000000) - Y- (down)
                if view_direction.IsAlmostEqualTo(XYZ(0.0, -1.0, 0.0)):
                    line_start = XYZ(min_pt.X, max_pt.Y, min_pt.Z)
                    line_end = XYZ(max_pt.X, min_pt.Y, min_pt.Z)

                # Case 2: (0.000000000, 1.000000000, 0.000000000) - Y+ (up)
                elif view_direction.IsAlmostEqualTo(XYZ(0.0, 1.0, 0.0)):
                    line_start = XYZ(min_pt.X, max_pt.Y, min_pt.Z)
                    line_end = XYZ(max_pt.X, min_pt.Y, min_pt.Z)

                # Case 3: (1.000000000, 0.000000000, 0.000000000) - X+ (right)
                elif view_direction.IsAlmostEqualTo(XYZ(1.0, 0.0, 0.0)):
                    line_start = XYZ(min_pt.X, min_pt.Y, min_pt.Z)
                    line_end = XYZ(max_pt.X, max_pt.Y, min_pt.Z)

                # Case 4: (-1.000000000, 0.000000000, 0.000000000) - X- (left)
                elif view_direction.IsAlmostEqualTo(XYZ(-1.0, 0.0, 0.0)):
                    line_start = XYZ(min_pt.X, min_pt.Y, min_pt.Z)
                    line_end = XYZ(max_pt.X, max_pt.Y, min_pt.Z)

                else:
                    skipped_views.append((view.Name, output.linkify(view.Id)))
                    continue
                
                if line_start and line_end:    
                    selected_levels = get_levels_in_view(doc, view)
                
                #print(selected_levels)

                # Inside your level processing loop
                for level in selected_levels:
                    curves = level.GetCurvesInView(DatumExtentType.ViewSpecific, view)
                    for level_curve in curves:
                        # Get the Z value from the curve's end points
                        line_point = level_curve.GetEndPoint(0)
                        z_value = line_point.Z
                        s_factor = view.Scale
                        extension_distance_1 = gap_distance_1/3 * s_factor / 100
                        extension_distance_2 = gap_distance_2/3 * s_factor / 100

                        level.HideBubbleInView(DatumEnds.End0, view)
                        level.HideBubbleInView(DatumEnds.End1, view)

                        if view_direction.IsAlmostEqualTo(XYZ(0.0, -1.0, 0.0)): 
                            start_point_adjusted = XYZ(line_start.X - right_direction.X * extension_distance_1, line_start.Y, z_value)
                            end_point_adjusted = XYZ(line_end.X + right_direction.X * extension_distance_2, line_end.Y, z_value)
                            new_level_line = Line.CreateBound(start_point_adjusted, end_point_adjusted)
                            level.SetCurveInView(DatumExtentType.ViewSpecific, view, new_level_line)
                            level.ShowBubbleInView(DatumEnds.End1, view)

                        elif view_direction.IsAlmostEqualTo(XYZ(0.0, 1.0, 0.0)): 
                            start_point_adjusted = XYZ(line_start.X + right_direction.X * extension_distance_2, line_start.Y, z_value)
                            end_point_adjusted = XYZ(line_end.X - right_direction.X * extension_distance_1, line_end.Y, z_value)
                            new_level_line = Line.CreateBound(start_point_adjusted, end_point_adjusted)
                            level.SetCurveInView(DatumExtentType.ViewSpecific, view, new_level_line)
                            level.ShowBubbleInView(DatumEnds.End0, view)

                        elif view_direction.IsAlmostEqualTo(XYZ(1.0, 0.0, 0.0)): 
                            start_point_adjusted = XYZ(line_start.X, line_start.Y - right_direction.Y * extension_distance_1, z_value)
                            end_point_adjusted = XYZ(line_end.X, line_end.Y + right_direction.Y * extension_distance_2, z_value)
                            new_level_line = Line.CreateBound(start_point_adjusted, end_point_adjusted)
                            level.SetCurveInView(DatumExtentType.ViewSpecific, view, new_level_line)
                            level.ShowBubbleInView(DatumEnds.End1, view)

                        elif view_direction.IsAlmostEqualTo(XYZ(-1.0, 0.0, 0.0)):
                            start_point_adjusted = XYZ(line_start.X, line_start.Y + right_direction.Y * extension_distance_2, z_value)
                            end_point_adjusted = XYZ(line_end.X, line_end.Y - right_direction.Y * extension_distance_1, z_value)
                            new_level_line = Line.CreateBound(start_point_adjusted, end_point_adjusted)
                            level.SetCurveInView(DatumExtentType.ViewSpecific, view, new_level_line)
                            level.ShowBubbleInView(DatumEnds.End0, view)

                total_level_count += 1
            view_list_length+= 1
        total_view_count += view_list_length

        processed_views = total_view_count - len(skipped_views)

        t.Commit()

        forms.alert("Successfully aligned {} grids in {} views".format(total_level_count, processed_views))

        # Record the end time
        end_time = time.time()
        runtime = end_time - start_time
        

        run_result = "Tool ran successfully"
        element_count = total_level_count if total_level_count else 0
        error_occured = "Nil"
        get_run_data('Align Levels link in Dimesnion Levels', runtime, element_count, manual_time, run_result, error_occured)

    except Exception as e:
    # Print error message
        print("Error occurred: {}".format(str(e)))

        # Record the end time and runtime
        end_time = time.time()
        runtime = end_time - start_time

        # Log the error details
        error_occured = "Error occurred: {}".format(str(e))
        run_result = "Error"
        element_count = 10

        # Function to log run data in case of error
        get_run_data('Align Levels link in Dimesnion Levels', runtime, element_count, manual_time, run_result, error_occured)

        t.RollBack()

    finally:
        t.Dispose()

    # Print skipped views message at the end
    if skipped_views:
        output.print_md(header_data)
        # Print the header for skipped views
        output.print_md("## ⚠️ Views Skipped ☹️")  # Markdown Heading 2 
        output.print_md("---")  # Markdown Line Break
        output.print_md("❌ Views skipped due to being inclined or not cardinally aligned. Refer to the **Table Report** below for reference.")  # Print a Line
        
        # Create a table to display the skipped views
        output.print_table(table_data=skipped_views, columns=["VIEW NAME", "ELEMENT ID"])  # Print a Table
        
        print("\n\n")
        output.print_md("---")  # Markdown Line Break

    print("Script runtime: {:.2f} seconds".format(runtime))