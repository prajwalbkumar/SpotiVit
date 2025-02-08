# -*- coding: utf-8 -*-
# __Title__ = " Curve Functions"
__author__ = "romaramnani"
__doc__ = 'Functions on curves to refer in main scripts.'

from Autodesk.Revit.DB import *
import Autodesk.Revit.DB as DB
import math
import itertools
from collections import defaultdict

def is_concentric(curves):
    c_curves = []
    for i, curve in curves:
        if isinstance(curve, Arc):
         c = curve.Center
        
         if c[i] == c[i+1]:
             c_curves.append(curve)
        else:
            print("curve no. {} in list is non-concentric".format(i+1))
             
def get_orientation(curve):
     if isinstance(curve, Line):
        start = curve.Curve.GetEndPoint(0)
        end = curve.Curve.GetEndPoint(1)
        
        dx = abs(start.X - end.X)
        dy = abs(start.Y - end.Y)
    
        if dx > dy:  # More horizontal
            return "horizontal"
        elif dx < dy:  # More vertical
            return "vertical"
        elif dx != 0 and dy != 0:  
            return "diagonal"
     else:  
         print("Curve is not a line")

def get_grid_radius(grids):
    for grid in grids:
        arc = grid.Curve
        c = arc.Center
        point = arc.GetEndPoint(0)
        radius = point.DistanceTo(c)
        return radius
    
# Convert type float to point
def convert_to_xyz(float_list):
    # Assuming the float_list contains coordinates in the order [X, Y, Z]
    if len(float_list) == 3:
        return DB.XYZ(float_list[0], float_list[1], float_list[2])
    else:
        raise ValueError("List must contain exactly 3 float values.")

# Check if point is XYZ element and print point coordinates
def print_xyz_point(point):
    """Prints the X, Y, Z coordinates of a Revit XYZ point."""
    if isinstance(point, XYZ):
        print("X: {}, Y: {}, Z: {}".format(point.X, point.Y, point.Z))
    else:
        print("Error: The {}} is not an XYZ object, but of type {}".format(point.Name, type(point)))

# Function to create circle model lines at given points
def create_circle(doc, view, point):
    radius = 3
    
    sketch_plane = view.SketchPlane
    print(point)
    print(type(point))

    point_on_plane = XYZ(point.X, point.Y, sketch_plane.GetPlane().Origin.Z)
    # Define the plane and arc for the circle
    circle_plane = DB.Plane.CreateByNormalAndOrigin(sketch_plane.GetPlane().Normal, point_on_plane)  # Normal to Z-axis
    circle_curve = Arc.Create(circle_plane, radius, 0, 2 * 3.14159)  # Full circle arc

    # Create a model line in the active view with the defined style
    model_line = doc.Create.NewModelCurve(circle_curve, sketch_plane)
    '''model_lines.append(model_line)'''
    return model_line

def isParallel(v1, v2):
    """
    Check if two vectors are parallel.
    """
    cross_product = v1.CrossProduct(v2)
    return cross_product.IsAlmostEqualTo(XYZ(0, 0, 0))

def are_parallel(vec1, vec2):
    return vec1.IsAlmostEqualTo(vec2) or vec1.IsAlmostEqualTo(vec2.Negate())

def isCollinear(l0, l1):
    """
    Check if two lines are collinear.
    """
    # Get endpoints of the lines
    a = l0.GetEndPoint(0)
    b = l0.GetEndPoint(1)
    c = l1.GetEndPoint(0)
    d = l1.GetEndPoint(1)
    
    # Define vectors
    v0 = b - a
    v1 = d - c
    v2 = c - a
    
    # Check if vectors are parallel
    if not isParallel(v0, v1):
        return False

    # Check if the lines lie on the same infinite line
    
# Create a normal line perpendicular to the curve of the segment.
def normal_line(s):
  
    l = s.GetCurve()
    d = l.Direction
    # Calculate the normal vector
    n = XYZ(-d.Y, d.X, 0)
    # Calculate the midpoint of the curve
    m = (l.GetEndPoint(0) + l.GetEndPoint(1)) / 2
    # Create a line from the midpoint in the direction of the normal vector
    nl = Line.CreateBound(m, m + n)
    return nl

def normalize_vector(vec):
    length = vec.GetLength()
    if length == 0:
        return vec
    return XYZ(vec.X / length, vec.Y / length, vec.Z / length)

# Function to offset a line in Revit
def offset_line(revit_line, offset_distance):
    start_point = revit_line.GetEndPoint(0)
    end_point = revit_line.GetEndPoint(1)
    direction = (end_point - start_point).Normalize()
    normal = DB.XYZ.BasisZ.CrossProduct(direction)

    offset_line = revit_line.CreateOffset(offset_distance, normal)
    return offset_line

def get_slope_intercept(lines):
   
    # List to store slope and intercept pairs
    line_equations = []

    for line in lines:
        # Get start and end points of the line
        start_point = line.GetEndPoint(0)
        end_point = line.GetEndPoint(1)
        
        # Calculate slope (m) and intercept (c)
        # Slope (m) = (y2 - y1) / (x2 - x1)
        slope = (end_point.Y - start_point.Y) / (end_point.X - start_point.X)
        
        # Intercept (c) = y - mx (using one of the points, e.g., start_point)
        intercept = start_point.Y - slope * start_point.X
        
        # Append (slope, intercept) to the list
        line_equations.append((slope, intercept))

    return line_equations

def distance_between_parallel_lines(line1, line2):
    # Get the direction vector of the lines
    dir1 = normalize_vector(line1.Direction)
    dir2 = normalize_vector(line2.Direction)
    
    if not are_parallel(dir1, dir2):
        raise ValueError("Lines are not parallel")
    
    # Get the start and end points of the lines
    pt1 = line1.GetEndPoint(0)
    pt2 = line2.GetEndPoint(0)
    
    # Calculate the perpendicular distance between the lines
    return abs((pt2 - pt1).DotProduct(dir1))

# Function to calculate the distance between two parallel lines
def distance_between_lines(c1, c2, slope):
    return abs(c2 - c1) / math.sqrt(1 + slope**2)

# Function to find the min and max distance between a list of parallel lines
def min_max_distance(lines, slope):
    # Extract the y-intercepts (c values) from the lines
    intercepts = [line[1] for line in lines]
    
    # Calculate all unique pair distances
    distances = []
    for (c1, c2) in itertools.combinations(intercepts, 2):
        distances.append(distance_between_lines(c1, c2, slope))
    
    # Find min and max distance
    return min(distances), max(distances)

def min_max_distance_pairs(lines, slope):
    # Extract the y-intercepts (c values) from the lines
    intercepts = [line[1] for line in lines]
    
    # Initialize variables to store min and max distances and the corresponding pairs
    min_dist = float('inf')
    max_dist = float('-inf')
    min_pair = None
    max_pair = None
    
    # Calculate all unique pair distances
    for (line1, line2) in itertools.combinations(lines, 2):
        c1, c2 = line1[1], line2[1]  # Extract intercepts
        dist = distance_between_lines(c1, c2, slope)
        
        # Check for minimum distance
        if dist < min_dist:
            min_dist = dist
            min_pair = (line1, line2)
        
        # Check for maximum distance
        if dist > max_dist:
            max_dist = dist
            max_pair = (line1, line2)
    
    # Return the minimum and maximum distances along with the line pairs
    return min_dist, min_pair, max_dist, max_pair

def group_parallel_lines(lines):
    parallel_groups = defaultdict(list)

    direction_vectors = []
    
    # Extract direction vectors and normalize them
    for line in lines:
        start_point = line.GetEndPoint(0)
        end_point = line.GetEndPoint(1)
        direction_vector = end_point - start_point
        normalized_vector = normalize_vector(direction_vector)
        direction_vectors.append(normalized_vector)

    # Group lines by parallel direction vectors
    for i, line in enumerate(lines):
        vector_i = direction_vectors[i]
        grouped = False
        for key in parallel_groups.keys():
            if are_parallel(vector_i, key):
                parallel_groups[key].append(line)
                grouped = True
                break
        if not grouped:
            parallel_groups[vector_i].append(line)

    return parallel_groups

def refArray(listConv):
    refArray = DB.ReferenceArray()
    for e in listConv:
        refArray.Append(DB.Reference(e))
    return refArray

def refLine(points):
    n = len(points) - 1
    start = points[0]
    end = points[n]
    dim_ref = DB.Line.CreateBound(start, end)
    return  dim_ref

# Function to check if an edge belongs to a door or window opening
def is_edge_in_opening(edge, doc):
    # Get the elements adjacent to the edge
    adjacent_faces = [edge.GetFace(0), edge.GetFace(1)]
    
    # Check if any adjacent face belongs to a door or window category
    for face in adjacent_faces:
        ref = face.Reference
        if ref:
            elem = doc.GetElement(ref.ElementId)
            if elem.Category:
                print(elem.Category.Id.IntegerValue)
                if elem.Category.Id.IntegerValue in [
                    BuiltInCategory.OST_Doors,
                    BuiltInCategory.OST_Windows,
                ]:
                    return True
                else:
                    return False
