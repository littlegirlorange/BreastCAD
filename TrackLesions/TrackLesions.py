import os
import unittest
import vtk, qt, ctk, slicer, numpy
import vtkITK
from slicer.ScriptedLoadableModule import *
import logging
from SimpleITK.SimpleITK import LabelMapToRGBImageFilter_swigregister
import TrackLesionsParams as params

customLayout = ("<layout type=\"horizontal\" split=\"true\" >"
    " <item>"
    "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Current\">"
    "   <property name=\"orientation\" action=\"default\">Sagittal</property>"
    "   <property name=\"viewlabel\" action=\"default\">C</property>"
    "   <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
    "  </view>"
    " </item>"
    " <item>"
    "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Past\">"
    "   <property name=\"orientation\" action=\"default\">Sagittal</property>"
    "   <property name=\"viewlabel\" action=\"default\">P</property>"
    "   <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
    "  </view>"
    " </item>"
    " </layout>")
  
customLayoutId = 501    

#
# TrackLesions
#

class TrackLesions(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "TrackLesions" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Custom"]
    self.parent.dependencies = []
    self.parent.contributors = ["Maggie Kusano (Martel Group)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# TrackLesionsWidget
#

class TrackLesionsWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    
    layout = self.layout

    # Instantiate and connect widgets ...
    # Set custom 2 sag view layout.
    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(customLayoutId, customLayout)
    layoutManager.setLayout(customLayoutId)
    
    sliceLogics = layoutManager.mrmlSliceLogics()
    for i in xrange(sliceLogics.GetNumberOfItems()):
      sliceLogic = sliceLogics.GetItemAsObject(i)
      if sliceLogic.GetName() in ["Current", "Past"]:
        sliceNode = sliceLogic.GetSliceNode()
        if sliceNode.GetLayoutGridRows() != 1 or sliceNode.GetLayoutGridColumns() != 1:
          sliceNode.SetLayoutGrid(1,1)
        sliceCompositeNode = sliceLogic.GetSliceCompositeNode()
        sliceCompositeNode.SetLinkedControl(1)
          
    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Current image selector
    #
    self.currentImgSelector = slicer.qMRMLNodeComboBox()
    self.currentImgSelector.nodeTypes = (("vtkMRMLScalarVolumeNode"), ("Name", "*Ph1*")) 
    self.currentImgSelector.selectNodeUponCreation = True
    self.currentImgSelector.addEnabled = False
    self.currentImgSelector.removeEnabled = False
    self.currentImgSelector.noneEnabled = False
    self.currentImgSelector.showHidden = False
    self.currentImgSelector.showChildNodeTypes = False
    self.currentImgSelector.setMRMLScene( slicer.mrmlScene )
    self.currentImgSelector.setToolTip( "Select the current first post-contrast image." )
    parametersFormLayout.addRow("Current Ph1 image: ", self.currentImgSelector)

    #
    # Past image selector
    #
    self.pastImgSelector = slicer.qMRMLNodeComboBox()
    self.pastImgSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.pastImgSelector.selectNodeUponCreation = True
    self.pastImgSelector.addEnabled = False
    self.pastImgSelector.removeEnabled = False
    self.pastImgSelector.noneEnabled = False
    self.pastImgSelector.showHidden = False
    self.pastImgSelector.showChildNodeTypes = False
    self.pastImgSelector.setMRMLScene( slicer.mrmlScene )
    self.pastImgSelector.setToolTip( "Select the past first post-contrast image." )
    parametersFormLayout.addRow("Past Ph1 image: ", self.pastImgSelector)

    #
    # Current lesion map selector
    #
    self.currentMapSelector = slicer.qMRMLNodeComboBox()
    self.currentMapSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.currentMapSelector.selectNodeUponCreation = True
    self.currentMapSelector.addEnabled = False
    self.currentMapSelector.removeEnabled = False
    self.currentMapSelector.noneEnabled = False
    self.currentMapSelector.showHidden = False
    self.currentMapSelector.showChildNodeTypes = False
    self.currentMapSelector.setMRMLScene( slicer.mrmlScene )
    self.currentMapSelector.setToolTip( "Select the current lesion map." )
    parametersFormLayout.addRow("Current lesion map: ", self.currentMapSelector)
    
    #
    # Past lesion map selector
    #
    self.pastMapSelector = slicer.qMRMLNodeComboBox()
    self.pastMapSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.pastMapSelector.selectNodeUponCreation = True
    self.pastMapSelector.addEnabled = False
    self.pastMapSelector.removeEnabled = False
    self.pastMapSelector.noneEnabled = False
    self.pastMapSelector.showHidden = False
    self.pastMapSelector.showChildNodeTypes = False
    self.pastMapSelector.setMRMLScene( slicer.mrmlScene )
    self.pastMapSelector.setToolTip( "Select the past lesion map." )
    parametersFormLayout.addRow("Past lesion map: ", self.pastMapSelector)
    
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.outputSelector.baseName = "Label Map"
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.renameEnabled = True
    self.outputSelector.noneEnabled = False
    self.outputSelector.addEnabled = True
    self.outputSelector.setMRMLScene(slicer.mrmlScene)
    self.outputSelector.setToolTip('Select or create a label map volume node as the SegmentCAD segmentation output.')
    parametersFormLayout.addRow("Output label map: ", self.outputSelector)
    
    #
    # Calculate subtraction images button
    #
    self.subtractImagesButton = qt.QPushButton("Calculate subtraction images")
    self.subtractImagesButton.toolTip = "Subtract pre-contrast image from post-contrast images."
    self.subtractImagesButton.enabled = True
    parametersFormLayout.addRow(self.subtractImagesButton)
        
    #
    # Find islands button
    #
    self.findIslandsButton = qt.QPushButton("Convert probability map to label map")
    self.findIslandsButton.toolTip = "Convert lesion probability map to label map."
    self.findIslandsButton.enabled = True
    parametersFormLayout.addRow(self.findIslandsButton)
        
    #
    # Save islands button
    #
    self.saveIslandsButton = qt.QPushButton("Save islands")
    self.saveIslandsButton.toolTip = "Save selected islands."
    self.saveIslandsButton.setCheckable(True)
    self.saveIslandsButton.enabled = True
    parametersFormLayout.addRow(self.saveIslandsButton)
    
    # Add vertical spacer
    self.layout.addStretch(1)
    
    # connections
    self.currentImgSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onCurrentImgSelect)
    self.pastImgSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onPastImgSelect)
    self.findIslandsButton.connect('clicked(bool)', self.onConvertMapToLabelButton)
    self.saveIslandsButton.connect('toggled(bool)', self.onSaveIslandsButtonToggled)
    self.subtractImagesButton.connect('clicked(bool)', self.onSubtractImagesButton)
    
    self.styleObserverTags = []
    self.sliceWidgetsPerStyle = {}    

  def removeObservers(self):
    # Remove observers and reset
    for observee, tag in self.styleObserverTags:
      observee.RemoveObserver(tag)
    self.styleObserverTags = []
    self.sliceWidgetsPerStyle = {}

  def addObservers(self):
    # Get new slice nodes
    layoutManager = slicer.app.layoutManager()
    sliceNodeCount = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceNode')
    for nodeIndex in xrange(sliceNodeCount):
      # Find the widget for each node in scene
      sliceNode = slicer.mrmlScene.GetNthNodeByClass(nodeIndex, 'vtkMRMLSliceNode')
      sliceWidget = layoutManager.sliceWidget(sliceNode.GetLayoutName())
      if sliceWidget:
        # Add observers and keep track of tags
        style = sliceWidget.sliceView().interactorStyle()
        self.sliceWidgetsPerStyle[style] = sliceWidget
        tag = style.AddObserver("LeftButtonReleaseEvent", self.processEvent)
        self.styleObserverTags.append([style, tag])


    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    self.removeObservers()

  def updateSliceWidget(self, widget, layer, nodeID):
    sliceLogic = slicer.app.layoutManager().sliceWidget(widget).sliceLogic()
    if layer == "Foreground":
      sliceLogic.GetSliceCompositeNode().SetForegroundVolumeID(nodeID)
    elif layer == "Background":
      sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(nodeID)
    elif layer == "Label":
      sliceLogic.GetSliceCompositeNode().SetLabelVolumeID(nodeID)
    else:
      logging.debug("updateSliceWidget failed: invalid layer: " + layer) 

  def onCurrentImgSelect(self):
    logic = TrackLesionsLogic()
    lesionMapNode = logic.getLesionMap(self.currentImgSelector.currentNode())
    self.currentMapSelector.setCurrentNode(lesionMapNode)

  def onPastImgSelect(self):
    logic = TrackLesionsLogic()
    lesionMapNode = logic.getLesionMap(self.pastImgSelector.currentNode())
    self.pastMapSelector.setCurrentNode(lesionMapNode)

  def onSelect(self):
    pass
    #self.applyButton.enabled = self.currentImgSelector.currentNode() and self.pastImgSelector.currentNode() and self.currentMapSelector.currentNode() and self.pastMapSelector.currentNode() and self.outputSelector.currentNode()
    #self.subtractImagesButton.enabled = self.currentImgSelector.currentNode() and self.pastImgSelector.currentNode() and self.currentMapSelector.currentNode() and self.pastMapSelector.currentNode() and self.outputSelector.currentNode()
    
  def onSubtractImagesButton(self):
    logic = TrackLesionsLogic()
    currentNode = self.currentImgSelector.currentNode()
    pastNode = self.pastImgSelector.currentNode()
    if logic.isValidSubtractImageInput(currentNode):
      diffNodes = logic.generateSubtractionImages(currentNode)
      self.updateSliceWidget("Current", "Background", diffNodes[0].GetID())
      self.updateSliceWidget("Current", "Foreground", None)
    if logic.isValidSubtractImageInput(pastNode):
      diffNodes = logic.generateSubtractionImages(pastNode)
      self.updateSliceWidget("Past", "Background", diffNodes[0].GetID())
      self.updateSliceWidget("Past", "Foreground", None)
      
  def onConvertMapToLabelButton(self):
    logic = TrackLesionsLogic()
    currentLabelNode = logic.convertMapToLabel(self.currentMapSelector.currentNode())
    if currentLabelNode:
      currentIslandNode = logic.identifyIslands(currentLabelNode)
    if currentIslandNode:
        self.updateSliceWidget("Current", "Label", currentIslandNode.GetID())
    pastLabelNode = logic.convertMapToLabel(self.pastMapSelector.currentNode())
    if pastLabelNode:
      pastIslandNode = logic.identifyIslands(pastLabelNode)
    if pastIslandNode:
        self.updateSliceWidget("Past", "Label", pastIslandNode.GetID())
        
  def onSaveIslandsButtonToggled(self, checked):
    if checked:
      self.removeObservers()
      self.addObservers()
    else:
      self.removeObservers()
            

  def processEvent(self, caller=None, event=None):
    """
    handle events from the render window interactor
    """
    logging.info("Left mouse click detected")
    if not self.sliceWidgetsPerStyle.has_key(caller):
      return
    if event == "LeftButtonReleaseEvent":
      # FIX INTERACTION so not all left button releases save islands #####
      sliceWidget = self.sliceWidgetsPerStyle[caller]
      sliceLogic = sliceWidget.sliceLogic()
      interactor = caller.GetInteractor()
      xy = interactor.GetEventPosition()
      logic = TrackLesionsLogic()
      outputNode = logic.saveIsland(xy, sliceLogic)
      if outputNode:
        self.updateSliceWidget(sliceLogic.GetName(), "Label", outputNode.GetID()) 

#
# TrackLesionsLogic
#

class TrackLesionsLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  
  def __init__(self):
    self.lesionMapMinThresh = 0.71
    self.lesionMapMaxThresh = 1.0

  def hasImageData(self, volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() == None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidSubtractImageInput(self, inputNode):
    if not inputNode:
      logging.debug('isValidSubtractImageInput failed: input node not defined')
      return False
    inputName = inputNode.GetName()
    if inputName.find("Ph") == -1:
      logging.debug('isValidSubtractImageInput failed: current volume is not a post-contrast series')
      return False
    return True
  
  def isValidInputOutputData(self, currentImgNode, pastImgNode, currentMapNode, pastMapNode):
    """Validates input data
    """
    if not currentImgNode:
      logging.debug('isValidInputOutputData failed: no current volume node defined')
      return False
    if not pastImgNode:
      logging.debug('isValidInputOutputData failed: no past volume node defined')
      return False
    if not currentMapNode:
      logging.debug('isValidInputOutputData failed: no current lesion map node defined')
      return False
    if not pastMapNode:
      logging.debug('isValidInputOutputData failed: no past lesion map node defined')
      return False      
    return True

  def createNumpyArray (self, node):
    # Generate Numpy Array from vtkMRMLScalarVolumeNode
    imageData = vtk.vtkImageData()
    imageData = node.GetImageData()
    shapeData = list(imageData.GetDimensions())
    return (vtk.util.numpy_support.vtk_to_numpy(imageData.GetPointData().GetScalars()).reshape(shapeData))

  def getSeriesIndex(self, volumeNode):
    # Returns the index of the volume series number in the volume node name
    volumeName = volumeNode.GetName()
    parts = volumeName.split("_")
    if params.pastImageTag in parts:
      # Past series.
      seriesIndex = params.pastImageFilenameParts.SeriesNumber
    else:
      # Current series.
      seriesIndex = params.currentImageFilenameParts.SeriesNumber
    return seriesIndex

  def getLesionMap(self, inputNode):
    nodeName = inputNode.GetName()
    parts = nodeName.split("_")
    if parts[-1] == "elastix":
      # Past series.
      if parts[-3] == "mc":
        seriesIndex = -5
      else:
        seriesIndex = -4
      postfix = "_?_Sag.VIBRANT.wo.FS_LesionProbMap_warped_elastix_thresh_vr"
    else:
      # Current series.
      seriesIndex = 4
      postfix = "_?_Sag.VIBRANT.wo.FS_LesionProbMap_thresh_vr"
    lesionMapName = ('_').join(parts[0:seriesIndex]) + postfix
    print lesionMapName
    lesionMapNode = slicer.util.getNode(lesionMapName)
    
    return lesionMapNode
    

  def generateSubtractionImages(self, inputNode):
    nodeName = inputNode.GetName()
    parts = nodeName.split("_")
    if parts[-1] == "elastix":
      # Past series.
      if parts[-3] == "mc":
        # Motion corrected.
        seriesIndex = -5
        prePostfix = "_Sag.VIBRANT.MPH_warped_elastix"
        postPostfix = "Sag.VIBRANT.MPH_mc_warped_elastix"
      else:
        seriesIndex = -4
        prePostfix = "_Sag.VIBRANT.MPH_warped_elastix"
        postPostfix = "Sag.VIBRANT.MPH_warped_elastix"
    else:
      # Current series.
      seriesIndex = 4
      prePostfix = "_Sag.VIBRANT.MPH"
      postPostfix = "Sag.VIBRANT.MPH"    
    
    print len(parts[seriesIndex])
    if len(parts[seriesIndex]) != 3:
      # Series number is < 3 characters long -> not a pre- or post-contrast image series.
      logging.info("Error in generateSubtractionImages: series number is not 3 digits long")
      return
  
    # Get pre-contrast image by series number. 
    # Expecting 3 digits ending with 0 (e.g., 600).
    # Also expecting node name to end in "_Sag.VIBRANT.MPH"
    parts[seriesIndex] = parts[seriesIndex][0:2]+'0'
    series0 = parts[seriesIndex]
    img0Name = ('_').join(parts[0:seriesIndex+1]) + prePostfix
    print img0Name
    img0Data = slicer.util.getNode(img0Name).GetImageData()
    
    # Set up VTK subtraction filter.
    diffFilter = vtk.vtkImageMathematics()
    diffFilter.SetOperationToSubtract()
    diffFilter.SetInputData(1, img0Data)
    
    diffNodes = []
    for i in range(4):  # Assume 4 post-contrast images.
      # Get series number. Expecting 3 digits (e.g., 601).
      # Also expecting node name to end in "_Ph[N]Sag.VIBRANT.MPH"
      # where [N] is between 1-4.
      parts[seriesIndex] = parts[seriesIndex][0:2]+str(i+1)
      seriesN = parts[seriesIndex]
      imgName = ('_').join(parts[0:seriesIndex+1]) + "_Ph" + str(i+1) + postPostfix
      print imgName
      
      # Subtract the pre-contrast image from this image.
      imgData = slicer.util.getNode(imgName).GetImageData()
      diffFilter.SetInputData(0, imgData)
      diffFilter.Update()
      
      # Check to see if there's already an output node.
      newName = ('_').join(parts[0:seriesIndex])+"_"+seriesN+"-"+series0
      outputNode = slicer.util.getNode(newName)
      if not outputNode:
        # Create new nodes to hold, display and store the subtraction image.
        outputNode = slicer.vtkMRMLScalarVolumeNode()
        outputNode.SetName(newName)
        slicer.mrmlScene.AddNode(outputNode)
        colorNode = slicer.util.getNode('Grey')
        displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
        slicer.mrmlScene.AddNode(displayNode)
        displayNode.SetAndObserveColorNodeID(colorNode.GetID())
        outputNode.SetAndObserveDisplayNodeID(displayNode.GetID())
        outputNode.CreateDefaultStorageNode()
                
      # Connect data and update display.
      ras2ijk = vtk.vtkMatrix4x4()
      ijk2ras = vtk.vtkMatrix4x4()
      inputNode.GetRASToIJKMatrix(ras2ijk)
      inputNode.GetIJKToRASMatrix(ijk2ras)
      outputNode.SetRASToIJKMatrix(ras2ijk)
      outputNode.SetIJKToRASMatrix(ijk2ras)
      outputNode.SetAndObserveImageData(diffFilter.GetOutput())
      outputNode.GetImageData().Modified()
      outputNode.Modified()
      
      diffNodes.append(outputNode)
      
    return diffNodes   

  def convertMapToLabel(self, lesionMapNode):
      
    if not lesionMapNode:
      slicer.util.errorDisplay('Lesion map missing.')
      return
  
    thresh = vtk.vtkImageThreshold()
    thresh.SetInputData(lesionMapNode.GetImageData())
    thresh.ThresholdBetween(self.lesionMapMinThresh, self.lesionMapMaxThresh)
    thresh.SetInValue(1)
    thresh.SetOutValue(0)
    thresh.SetOutputScalarTypeToShort()
    thresh.Update()

    # Check to see if there's already an output node.
    lesionMapName = lesionMapNode.GetName()
    parts = lesionMapName.split("_")
    seriesIndex = self.getSeriesIndex(lesionMapNode)
    newName = ('_').join(parts[0:seriesIndex])+"_label"
    outputNode = slicer.util.getNode(newName)
    if not outputNode:
      outputNode = self.createOutputLabelNode(newName, 'GenericAnatomyColors')    
    self.connectImageDataToOutputNode(lesionMapNode, outputNode, thresh.GetOutput())
      
    return outputNode

  def identifyIslands(self, labelNode):
    #
    # change the label values based on the parameter node
    #
    minimumSize = 0
    fullyConnected = True

    # note that island operation happens in unsigned long space
    # but the slicer editor works in Short
    castIn = vtk.vtkImageCast()
    castIn.SetInputData( labelNode.GetImageData() )
    castIn.SetOutputScalarTypeToUnsignedLong()

    # now identify the islands in the inverted volume
    # and find the pixel that corresponds to the background
    islandMath = vtkITK.vtkITKIslandMath()
    islandMath.SetInputConnection( castIn.GetOutputPort() )
    islandMath.SetFullyConnected( fullyConnected )
    islandMath.SetMinimumSize( minimumSize )
    # TODO: $this setProgressFilter $islandMath "Calculating Islands..."

    # note that island operation happens in unsigned long space
    # but the slicer editor works in Short
    outputImageData = vtk.vtkImageData()
    castOut = vtk.vtkImageCast()
    castOut.SetInputConnection( islandMath.GetOutputPort() )
    castOut.SetOutputScalarTypeToShort()
    castOut.SetOutput(outputImageData)

    castOut.Update()
    islandCount = islandMath.GetNumberOfIslands()
    islandOrigCount = islandMath.GetOriginalNumberOfIslands()
    ignoredIslands = islandOrigCount - islandCount
    print( "%d islands created (%d ignored)" % (islandCount, ignoredIslands) )

    # Check to see if there's already an output node.
    labelName = labelNode.GetName()
    newName = labelName + "_islands"
    outputNode = slicer.util.getNode(newName)
    if not outputNode:            
      outputNode = self.createOutputLabelNode(newName, 'GenericAnatomyColors')    
    self.connectImageDataToOutputNode(labelNode, outputNode, outputImageData)
    
    castOut.SetOutput( None )
    
    return outputNode


  def createOutputLabelNode(self, name, colorTable='GenericAnatomyColors'):
    # Create new nodes to hold, display and store the output image.
    outputNode = slicer.vtkMRMLLabelMapVolumeNode()
    outputNode.SetName(name)
    slicer.mrmlScene.AddNode(outputNode)
    colorNode = slicer.util.getNode(colorTable)
    displayNode = slicer.vtkMRMLLabelMapVolumeDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    displayNode.SetAndObserveColorNodeID(colorNode.GetID())
    outputNode.SetAndObserveDisplayNodeID(displayNode.GetID())
    outputNode.CreateDefaultStorageNode()
    return outputNode

  def connectImageDataToOutputNode(self, inputNode, outputNode, outputImageData):
    # Connect data and update display.
    ras2ijk = vtk.vtkMatrix4x4()
    ijk2ras = vtk.vtkMatrix4x4()
    inputNode.GetRASToIJKMatrix(ras2ijk)
    inputNode.GetIJKToRASMatrix(ijk2ras)
    outputNode.SetRASToIJKMatrix(ras2ijk)
    outputNode.SetIJKToRASMatrix(ijk2ras)
    outputNode.SetAndObserveImageData(outputImageData)
    if outputNode.GetImageDataConnection():
      outputNode.GetImageDataConnection().GetProducer().Update()
    outputNode.GetImageData().Modified()
    outputNode.Modified()       
    
  '''
  Set up mouse interaction on viewports
  Encode point as fiducial
  Find the label at the selected point
  Find the centroid of the labelled voxels
  Convert centroid from xyz coords to RAS
  Display table of fiducials:
  Current                              Past                                 Difference
  FName  Volume  Dimensions  Centroid  FName  Volume  Dimensions  Centroid  Overlap  Union  Dice  Distance
  '''
 
  def saveIsland(self, xy, sliceLogic):
    # Save the currently selected island as a new label node.
    labelLogic = sliceLogic.GetLabelLayer()
    multiLabelNode = labelLogic.GetVolumeNode()
    if not multiLabelNode:
      return
    multiLabelImageData = multiLabelNode.GetImageData()
    if not multiLabelImageData:
      return
    xyToIJK = labelLogic.GetXYToIJKTransform()
    ijk = xyToIJK.TransformDoublePoint( xy + (0,) )
    ijk = map(lambda v: int(round(v)), ijk)
    dims = multiLabelImageData.GetDimensions()
    for idx in xrange(3):
      if ijk[idx] < 0 or ijk[idx] >= dims[idx]:
        return
    
    # Call vtk filter.
    outputImageData = vtk.vtkImageData()
    connectivity = slicer.vtkImageConnectivity()
    connectivity.SetFunctionToSaveIsland()
    connectivity.SetInputData(multiLabelImageData)
    connectivity.SetOutput(outputImageData)
    connectivity.SetSeed(ijk)
    connectivity.Update()
    
    # Get island label.
    labelValue = int(multiLabelImageData.GetScalarComponentAsDouble(ijk[0], ijk[1], ijk[2], 0))
    
    # Check to see if there's already an output node.
    multiLabelNodeName = multiLabelNode.GetName()
    newName = multiLabelNodeName + "_" + str(labelValue)
    outputNode = slicer.util.getNode(newName)
    if not outputNode:            
      outputNode = self.createOutputLabelNode(newName, 'GenericAnatomyColors')    
    self.connectImageDataToOutputNode(multiLabelNode, outputNode, outputImageData)

    connectivity.SetOutput( None )
    
    return outputNode
    
  def pickLabel(self, xy):
    ''' Return the label at the selected point in image coordinates.
    '''
    pass
    

  def run(self, currentVolume, pastVolume, currentMap, pastMap):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(currentVolume, pastVolume, currentMap, pastMap):
      slicer.util.errorDisplay('Input data missing.')
      return False

    logging.info('Processing started')

    self.showOverlays()

    logging.info('Processing completed')

    return True


class TrackLesionsTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_TrackLesions1()

  def test_TrackLesions1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = TrackLesionsLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
