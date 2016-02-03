import vtk, qt, ctk, slicer
import string
import SimpleITK as sitk
import sitkUtils


class LabelStatsLogic:
  """This Logic is copied from the Label Statistics Module -Steve Pieper (Isomics)"""
  """Implement the logic to calculate label statistics.
  Nodes are passed in as arguments.
  Results are stored as 'statistics' instance variable.
  """
  
  HEADER_KEYS = ("Index", "Count", "Volume mm^3", "DimX mm", "DimY mm", "DimZ mm", "COMX mm", "COMY mm", "COMZ mm", "Min", "Max", "Mean", "StdDev", "LabelNode", "ImageNode")
  
  def __init__(self, labelNode, label=None, grayscaleNode=None):
    
    #self.keys = ("Index", "Count", "Volume mm^3", "DimX mm", "DimY mm", "DimZ mm", "COMX mm", "COMY mm", "COMZ mm", "Min", "Max", "Mean", "StdDev", "LabelNode", "ImageNode")
    cubicMMPerVoxel = reduce(lambda x,y: x*y, labelNode.GetSpacing())
    self.labelStats = {}
    self.labelStats['Labels'] = []
    
    # Set up VTK histogram statistics filter.
    stataccum = vtk.vtkImageAccumulate()
    stataccum.SetInputConnection(labelNode.GetImageDataConnection())
    stataccum.Update()

    if not grayscaleNode:
      grayscaleNode = labelNode
      
    if label:
      lo = label
      hi = label
    else:
      lo = int(stataccum.GetMin()[0])
      hi = int(stataccum.GetMax()[0])
      if lo == 0:
        # Don't calculate statistics for the background.
        if hi == 0:
          # No label.
          return
        lo = 1
    
    # Set up SimpleITK shape statistics filter for label node.
    voxDims = labelNode.GetSpacing()
    labelName = labelNode.GetName()
    labelImage = sitkUtils.PullFromSlicer(labelName)
    labelShapeStatisticsFilter = sitk.LabelShapeStatisticsImageFilter()
    outputImage = labelShapeStatisticsFilter.Execute(labelImage, 0, False, False)    

    for i in xrange(lo, hi + 1):
      thresholder = vtk.vtkImageThreshold()
      thresholder.SetInputConnection(labelNode.GetImageDataConnection())
      thresholder.SetInValue(1)
      thresholder.SetOutValue(0)
      thresholder.ReplaceOutOn()
      thresholder.ThresholdBetween(i, i)
      thresholder.SetOutputScalarType(grayscaleNode.GetImageData().GetScalarType())
      thresholder.Update()

      stencil = vtk.vtkImageToImageStencil()
      stencil.SetInputConnection(thresholder.GetOutputPort())
      stencil.ThresholdBetween(1, 1)
      
      stat1 = vtk.vtkImageAccumulate()
      stat1.SetInputConnection(grayscaleNode.GetImageDataConnection())
      stencil.Update()
      stat1.SetStencilData(stencil.GetOutput())
      stat1.Update()

      if stat1.GetVoxelCount() > 0:
        
        vol = labelShapeStatisticsFilter.GetPhysicalSize(i)
        dims = labelShapeStatisticsFilter.GetBoundingBox(i)  # [x0, y0, z0, dx, dy, dz]
        com = labelShapeStatisticsFilter.GetCentroid(i)
                
        # add an entry to the LabelStats list
        self.labelStats["Labels"].append(i)
        self.labelStats[i,"Index"] = i
        self.labelStats[i,"Count"] = stat1.GetVoxelCount()
        self.labelStats[i,"Volume mm^3"] = "{0:.1f}".format(vol)
        self.labelStats[i,"DimX mm"] = "{0:.1f}".format(dims[3]*voxDims[0])
        self.labelStats[i,"DimY mm"] = "{0:.1f}".format(dims[4]*voxDims[1])
        self.labelStats[i,"DimZ mm"] = "{0:.1f}".format(dims[5]*voxDims[2])
        self.labelStats[i,"COMX mm"] = "{0:.1f}".format(-com[0])  # Convert from LPS to RAS
        self.labelStats[i,"COMY mm"] = "{0:.1f}".format(-com[1])  # Convert from LPS to RAS
        self.labelStats[i,"COMZ mm"] = "{0:.1f}".format(com[2])
        self.labelStats[i,"Min"] = stat1.GetMin()[0]
        self.labelStats[i,"Max"] = stat1.GetMax()[0]
        self.labelStats[i,"Mean"] = "{0:.1f}".format(stat1.GetMean()[0])
        self.labelStats[i,"StdDev"] = "{0:.1f}".format(stat1.GetStandardDeviation()[0])
        self.labelStats[i,"LabelNode"] = labelName
        self.labelStats[i,"ImageNode"] = grayscaleNode.GetName()


