import os
import unittest
import vtk, qt, ctk, slicer, numpy
import vtkITK
from fnmatch import fnmatch
from slicer.ScriptedLoadableModule import *
import logging
import TrackLesionsParams as params
import LabelStatsLogic


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

currentFourUpView = (
  "<layout type=\"vertical\">"
  " <item>"
  "  <layout type=\"horizontal\">"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"CurrentRed\">"
  "     <property name=\"orientation\" action=\"default\">Axial</property>"
  "     <property name=\"viewlabel\" action=\"default\">CurR</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
  "   <item>"
  "    <view class=\"vtkMRMLViewNode\" singletontag=\"Current1\">"
  "     <property name=\"viewlabel\" action=\"default\">Cur1</property>"
  "    </view>"
  "   </item>"
  "  </layout>"
  " </item>"
  " <item>"
  "  <layout type=\"horizontal\">"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"CurrentYellow\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">CurY</property>"
  "     <property name=\"viewcolor\" action=\"default\">#EDD54C</property>"
  "    </view>"
  "   </item>"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"CurrentGreen\">"
  "     <property name=\"orientation\" action=\"default\">Coronal</property>"
  "     <property name=\"viewlabel\" action=\"default\">CurG</property>"
  "     <property name=\"viewcolor\" action=\"default\">#6EB04B</property>"
  "    </view>"
  "   </item>"
  "  </layout>"
  " </item>"
  "</layout>")
currentFourUpViewId = 502

pastFourUpView = (
  "<layout type=\"vertical\">"
  " <item>"
  "  <layout type=\"horizontal\">"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"PastRed\">"
  "     <property name=\"orientation\" action=\"default\">Axial</property>"
  "     <property name=\"viewlabel\" action=\"default\">PastR</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
  "   <item>"
  "    <view class=\"vtkMRMLViewNode\" singletontag=\"Past1\">"
  "     <property name=\"viewlabel\" action=\"default\">Past1</property>"
  "    </view>"
  "   </item>"
  "  </layout>"
  " </item>"
  " <item>"
  "  <layout type=\"horizontal\">"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"PastYellow\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">PastY</property>"
  "     <property name=\"viewcolor\" action=\"default\">#EDD54C</property>"
  "    </view>"
  "   </item>"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"PastGreen\">"
  "     <property name=\"orientation\" action=\"default\">Coronal</property>"
  "     <property name=\"viewlabel\" action=\"default\">PastG</property>"
  "     <property name=\"viewcolor\" action=\"default\">#6EB04B</property>"
  "    </view>"
  "   </item>"
  "  </layout>"
  " </item>"
  "</layout>")
pastFourUpViewId = 503

#
# TrackLesions
#

class TrackLesions(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "TrackLesions"
    self.parent.categories = ["Custom"]
    self.parent.dependencies = ["Data"]
    self.parent.contributors = ["Maggie Kusano (Martel Group)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is a scripted loadable module bundled in an extension.
    It calculates subtraction images and segments lesion probabiliy maps from
    registered DCE-MRI data.
    """
    self.parent.acknowledgementText = """
    Thanks for being patient while using this work-in-progress :).
    """

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
    self.sliceLogicNames = ["Current", "Past"]
    self.viewLogicNames = ["ViewCurrent1", "ViewPast1"]
    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(customLayoutId, customLayout)
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(currentFourUpViewId, currentFourUpView)
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(pastFourUpViewId, pastFourUpView)
    layoutManager.setLayout(currentFourUpViewId)
    layoutManager.setLayout(pastFourUpViewId)
    layoutManager.setLayout(customLayoutId)
    for iView in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(iView).threeDView()
      viewNode = threeDView.mrmlViewNode()
      if viewNode.GetName() in self.viewLogicNames:
        viewNode.SetBackgroundColor([0,0,0])
        viewNode.SetBackgroundColor2([0,0,0])
        viewNode.SetBoxVisible(0)
        viewNode.SetAxisLabelsVisible(0)
    self.currentView = 'CompareView'
    
    sliceLogics = layoutManager.mrmlSliceLogics()
    for i in xrange(sliceLogics.GetNumberOfItems()):
      sliceLogic = sliceLogics.GetItemAsObject(i)
      # if sliceLogic.GetName() in self.sliceLogicNames:
      sliceNode = sliceLogic.GetSliceNode()
      if sliceNode.GetLayoutGridRows() != 1 or sliceNode.GetLayoutGridColumns() != 1:
        sliceNode.SetLayoutGrid(1,1)
      sliceCompositeNode = sliceLogic.GetSliceCompositeNode()
      sliceCompositeNode.SetLinkedControl(1)
      
    # Turn on navigation.
    crosshairNode = slicer.util.getNode("vtkMRMLCrosshairNode*")
    if crosshairNode:
      crosshairNode.SetCrosshairMode(5)
      crosshairNode.SetNavigation(1)
          
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
    self.currentImgSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"] 
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
    
    #
    # View selector
    #
    """
    loader = qt.QUiLoader()
    path = os.path.join(os.path.dirname(__file__), 'Resources', 'UI', 'viewRadioButtons.ui')
    qfile = qt.QFile(path)
    qfile.open(qt.QFile.ReadOnly)
    self.window = loader.load(qfile)
    window = self.window
    find = slicer.util.findChildren
    self.viewSelectorWidget = find(window, 'horizontalLayoutWidget')[0]
    self.compareViewRadioButton = find(window, 'compareViewRadioButton')[0]
    self.currentViewRadioButton = find(window, 'currentViewRadioButton')[0]
    self.pastViewRadioButton = find(window, 'pastViewRadioButton')[0]
    self.compareViewRadioButton.checked = True
    parametersFormLayout.addRow("View: ", self.viewSelectorWidget)
"""
    self.viewLayoutBox = qt.QGroupBox()
    self.viewLayoutBox.setLayout(qt.QFormLayout())
    self.compareViewRadioButton = qt.QRadioButton()
    self.viewLayoutBox.layout().addWidget(self.compareViewRadioButton)    
    self.compareViewRadioButton.text = "Compare (sagittal side-by-side)"
    self.currentViewRadioButton = qt.QRadioButton()
    self.viewLayoutBox.layout().addWidget(self.currentViewRadioButton)
    self.currentViewRadioButton.text = "Current only (4-up)"
    self.pastViewRadioButton = qt.QRadioButton()
    self.viewLayoutBox.layout().addWidget(self.pastViewRadioButton)
    self.pastViewRadioButton.text = "Past only (4-up)"   
    self.compareViewRadioButton.checked = True
    parametersFormLayout.addRow("View:", self.viewLayoutBox)
        
    #
    # Slice selector
    #
    self.inputSliceLabel = qt.QLabel("Show sagittal slice:")
    self.inputSliceLabel.setToolTip("Navigate sagittal views to the selected slice.")
    self.inputSliceSelector = qt.QSpinBox()
    self.inputSliceSelector.singleStep = (1)
    self.inputSliceSelector.minimum = (1)
    if self.currentImgSelector.currentNode():
      dims = self.currentImgSelector.currentNode().GetImageData().GetDimensions()
      maxSliceNo = dims[2]+1
      value = round(maxSliceNo/2)
    else:
      maxSliceNo = 1
      value = 1
    self.inputSliceSelector.maximum = (maxSliceNo)
    self.inputSliceSelector.value = (value)
    self.inputSliceSelector.setToolTip("Navigate sagittal views to the selected slice.")
    parametersFormLayout.addRow(self.inputSliceLabel, self.inputSliceSelector)
    
          
    #
    # Analysis Area
    #
    analysisCollapsibleButton = ctk.ctkCollapsibleButton()
    analysisCollapsibleButton.text = "Analysis"
    self.layout.addWidget(analysisCollapsibleButton)

    # Layout within the dummy collapsible button
    analysisFormLayout = qt.QFormLayout(analysisCollapsibleButton)
    
    #
    # Calculate subtraction images button
    #
    self.subtractImagesButton = qt.QPushButton("Calculate subtraction images")
    self.subtractImagesButton.toolTip = "Subtract pre-contrast image from post-contrast images."
    self.subtractImagesButton.enabled = True
    analysisFormLayout.addRow(self.subtractImagesButton)
        
    #
    # Find islands button
    #
    self.findIslandsButton = qt.QPushButton("Convert probability map to label map")
    self.findIslandsButton.toolTip = "Convert lesion probability map to label map."
    self.findIslandsButton.enabled = True
    analysisFormLayout.addRow(self.findIslandsButton)
        
    #
    # Save islands button
    #
    self.saveIslandsButton = qt.QPushButton("Save islands")
    self.saveIslandsButton.toolTip = "Save selected islands."
    self.saveIslandsButton.setCheckable(True)
    self.saveIslandsButton.enabled = False  # Turned off for now.
    analysisFormLayout.addRow(self.saveIslandsButton)
 
    #
    # Query islands button
    #
    self.queryIslandsButton = qt.QPushButton("Query island statistics")
    self.queryIslandsButton.toolTip = "Save selected islands."
    self.queryIslandsButton.setCheckable(True)
    self.queryIslandsButton.enabled = True
    analysisFormLayout.addRow(self.queryIslandsButton)
    
    # LabelStatistics Table Collapsible Button
    self.labelstatisticsCollapsibleButton = ctk.ctkCollapsibleButton()
    self.labelstatisticsCollapsibleButton.text = "Lesion Label Statistics"
    analysisFormLayout.addWidget(self.labelstatisticsCollapsibleButton)
    self.labelstatisticsCollapsibleButton.collapsed = False
    # Layout within the collapsible button
    self.labelstatisticsLayout = qt.QFormLayout(self.labelstatisticsCollapsibleButton)
    # Table View to display Label statistics
    self.labelStatisticsTableView = qt.QTableView()
    self.labelStatisticsTableView.sortingEnabled = True
    self.labelstatisticsLayout.addWidget(self.labelStatisticsTableView)
    self.labelStatisticsTableView.minimumHeight = 200
    self.initializeStats()    
    
    # Add vertical spacer
    self.layout.addStretch(1)
    
    # connections
    self.currentImgSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onCurrentImgSelect)
    self.pastImgSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onPastImgSelect)
    self.inputSliceSelector.connect("valueChanged(int)", self.onInputSliceSelect)
    self.compareViewRadioButton.connect('clicked()', self.onViewSelected)
    self.currentViewRadioButton.connect('clicked()', self.onViewSelected)
    self.pastViewRadioButton.connect('clicked()', self.onViewSelected)        
    self.findIslandsButton.connect('clicked(bool)', self.onConvertMapToLabelButton)
    self.saveIslandsButton.connect('toggled(bool)', self.onSaveIslandsButtonToggled)
    self.queryIslandsButton.connect('toggled(bool)', self.onQueryIslandsButtonToggled)    
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

  def cleanup(self):
    self.removeObservers()

  def onViewSelected(self):
    if self.compareViewRadioButton.checked:
      newView = 'CompareView'
    elif self.currentViewRadioButton.checked:
      newView = 'CurrentView'
    else:
      newView = 'PastView'
    if self.currentView != newView:
      self.setView(newView)
      
  def setView(self, newView):
    logic = TrackLesionsLogic()
    layoutManager = slicer.app.layoutManager()
    if newView == 'CompareView':
      layoutManager.setLayout(customLayoutId)
    elif newView == 'CurrentView':
      layoutManager.setLayout(currentFourUpViewId)     
    else:
      layoutManager.setLayout(pastFourUpViewId)
    self.currentView = newView

  def updateSliceWidget(self, widget, layer, nodeID, fitToBackground=False):
    sliceWidget = slicer.app.layoutManager().sliceWidget(widget)
    sliceLogic = sliceWidget.sliceLogic()
    if layer == "Foreground":
      sliceLogic.GetSliceCompositeNode().SetForegroundVolumeID(nodeID)
    elif layer == "Background":
      sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(nodeID)
    elif layer == "Label":
      sliceLogic.GetSliceCompositeNode().SetLabelVolumeID(nodeID)
    else:
      logging.debug("updateSliceWidget failed: invalid layer: " + layer)
    if fitToBackground:
      sliceWidget.fitSliceToBackground()
    print(("Updated widget: {0}, layer: {1}, nodeId: {2}").format(widget, layer, nodeID))
    
  def getSliceWidgets(self, name="*", orientation="*"):
    if name != "*":
      name = name + "*"
    nSliceNodes = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceNode')
    layoutManager = slicer.app.layoutManager()
    sliceWidgets = []
    for iSliceNode in xrange(nSliceNodes):
      sliceNode = slicer.mrmlScene.GetNthNodeByClass(iSliceNode, 'vtkMRMLSliceNode')
      sliceWidgetName = sliceNode.GetLayoutName()
      sliceWidgetOrientation = sliceNode.GetOrientationString() 
      if fnmatch(sliceWidgetName, name) and fnmatch(sliceWidgetOrientation, orientation):
        sliceWidgets.append(sliceWidgetName)
    return sliceWidgets

  def onCurrentImgSelect(self):
    logic = TrackLesionsLogic()
    lesionMapNode = logic.getLesionMap(self.currentImgSelector.currentNode())
    self.currentMapSelector.setCurrentNode(lesionMapNode)
    widgets = self.getSliceWidgets("Current")
    for widget in widgets:
      self.updateSliceWidget(widget, "Background", self.currentImgSelector.currentNode().GetID(), True)
      if lesionMapNode:
        self.updateSliceWidget(widget, "Foreground", lesionMapNode.GetID())
    # Update slice selector widget according to current image dimensions.
    dims = self.currentImgSelector.currentNode().GetImageData().GetDimensions()
    maxSliceNo = dims[2]+1
    self.inputSliceSelector.maximum = (maxSliceNo)
    if self.inputSliceSelector.value > maxSliceNo:
      value = round(maxSliceNo/2)
      self.inputSliceSelector.value = (value)

  def onPastImgSelect(self):
    logic = TrackLesionsLogic()
    lesionMapNode = logic.getLesionMap(self.pastImgSelector.currentNode())
    self.pastMapSelector.setCurrentNode(lesionMapNode)
    widgets = self.getSliceWidgets("Past")
    for widget in widgets:
      self.updateSliceWidget(widget, "Background", self.pastImgSelector.currentNode().GetID(), True)
      if lesionMapNode:
        self.updateSliceWidget(widget, "Foreground", lesionMapNode.GetID())    

  def onInputSliceSelect(self):
    slice = self.inputSliceSelector.value
    self.setSlice(slice)
    
  def onSelect(self):
    pass
    #self.applyButton.enabled = self.currentImgSelector.currentNode() and self.pastImgSelector.currentNode() and self.currentMapSelector.currentNode() and self.pastMapSelector.currentNode() and self.outputSelector.currentNode()
    #self.subtractImagesButton.enabled = self.currentImgSelector.currentNode() and self.pastImgSelector.currentNode() and self.currentMapSelector.currentNode() and self.pastMapSelector.currentNode() and self.outputSelector.currentNode()
    
  def onSubtractImagesButton(self):
    logic = TrackLesionsLogic()
    currentNode = self.currentImgSelector.currentNode()
    pastNode = self.pastImgSelector.currentNode()
    if logic.isValidSubtractImageInput(currentNode) and logic.isValidSubtractImageInput(pastNode):
      # Update slice nodes.
      currentDiffNodes = logic.generateSubtractionImages(currentNode)
      pastDiffNodes = logic.generateSubtractionImages(pastNode)
      curWidgets = self.getSliceWidgets("Current")
      for widget in curWidgets:
        self.updateSliceWidget(widget, "Background", currentDiffNodes[0].GetID())
        self.updateSliceWidget(widget, "Foreground", None)
      pastWidgets = self.getSliceWidgets("Past")
      for widget in pastWidgets:
        self.updateSliceWidget(widget, "Background", pastDiffNodes[0].GetID())
        self.updateSliceWidget(widget, "Foreground", None)
        
      # Update volume nodes.
      curVolumeNode = currentDiffNodes[0]
      pastVolumeNode = pastDiffNodes[0]
      breastMaskNode = logic.getBreastMask(curVolumeNode)
      if breastMaskNode:
        curMaskedNode = logic.generateMaskedNode(curVolumeNode, breastMaskNode)
        if curMaskedNode:
          curVolumeNode = curMaskedNode
        pastMaskedNode = logic.generateMaskedNode(pastVolumeNode, breastMaskNode)
        if pastMaskedNode:
          pastVolumeNode = pastMaskedNode
      logic.renderVolume(curVolumeNode, "ViewCurrent1")
      logic.renderVolume(pastVolumeNode, "ViewPast1")
      
  def onConvertMapToLabelButton(self):
    logic = TrackLesionsLogic()
    currentLabelNode = logic.convertMapToLabel(self.currentMapSelector.currentNode())
    if currentLabelNode:
      currentIslandNode = logic.identifyIslands(currentLabelNode)
    if currentIslandNode:
      widgets = self.getSliceWidgets("Current")
      for widget in widgets:
        self.updateSliceWidget(widget, "Label", currentIslandNode.GetID())
    pastLabelNode = logic.convertMapToLabel(self.pastMapSelector.currentNode())
    if pastLabelNode:
      pastIslandNode = logic.identifyIslands(pastLabelNode)
    if pastIslandNode:
      widgets = self.getSliceWidgets("Past")
      for widget in widgets:
        self.updateSliceWidget(widget, "Label", pastIslandNode.GetID())
        
  def onSaveIslandsButtonToggled(self, checked):
    if checked:
      self.removeObservers()
      self.addObservers()
      self.queryIslandsButton.checked = False
    else:
      self.removeObservers()

  def onQueryIslandsButtonToggled(self, checked):
    if checked:
      self.removeObservers()
      self.addObservers()
      self.saveIslandsButton.checked = False
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
      if self.saveIslandsButton.isChecked():
        outputNode = logic.saveIsland(xy, sliceLogic)
        if outputNode:
          self.updateSliceWidget(sliceLogic.GetName(), "Label", outputNode.GetID())
      elif self.queryIslandsButton.isChecked():
        statsLogic = logic.queryIsland(xy, sliceLogic)
        if statsLogic:
          labelNode = sliceLogic.GetLabelLayer().GetVolumeNode()
          self.populateStats(statsLogic, labelNode)
          
  
  def setSlice(self, iSlice):
    # Set the slice displayed in the Current and Past volume nodes.
    orientations = {'Sagittal':0, 'Coronal':1, 'Axial':2}
    sliceNodeNames = self.getSliceWidgets("*", "Sagittal")
    for name in sliceNodeNames:
      ijkToRas = vtk.vtkMatrix4x4()
      sliceLogic = slicer.app.layoutManager().sliceWidget(name).sliceLogic()
      sliceNode = sliceLogic.GetSliceNode()
      orientationString = sliceNode.GetOrientationString()
      rasIndex = orientations[orientationString]
      volNode = sliceLogic.GetBackgroundLayer().GetVolumeNode()
      volNode.GetIJKToRASMatrix(ijkToRas)
      posIjk = [0, 0, 0, 1]
      posIjk[2-rasIndex] = iSlice
      posRas = ijkToRas.MultiplyPoint(posIjk)
      sliceLogic.SetSliceOffset(posRas[rasIndex])
      
  def initializeStats(self):
    # Create table.
    self.model = qt.QStandardItemModel()
    self.labelStatisticsTableView.setModel(self.model)
    self.labelStatisticsTableView.verticalHeader().visible = False
    
  def populateStats(self, statsLogic, labelNode):
    """
    Most based on Slicer's LabelStatistics Module
    """
    # Get label/image info for table.
    labelName = labelNode.GetName()
    parts = labelName.split("_")
    if len(parts) > params.currentImageFilenameParts.AccessionNumber+3:
      # Past label.
      accessionNo = parts[params.pastLesionMapFilenameParts.AccessionNumber]
    else:
      accessionNo = parts[params.currentLesionMapFilenameParts.AccessionNumber]
      
    # Populate table.
    displayNode = labelNode.GetDisplayNode()
    colorNode = displayNode.GetColorNode()
    lut = colorNode.GetLookupTable()
    self.items = []
    row = self.model.rowCount()
    
    for i in statsLogic.labelStats["Labels"]:
      # Label color box.
      col = 0
      color = qt.QColor()
      rgb = lut.GetTableValue(i)
      color.setRgb(rgb[0]*255,rgb[1]*255,rgb[2]*255)
      item = qt.QStandardItem()
      item.setData(color,qt.Qt.DecorationRole)
      item.setToolTip(colorNode.GetColorName(i))
      item.setEditable(False)
      self.model.setItem(row,col,item)
      self.items.append(item)
      col += 1
      
      # Label color name (editable).
      item = qt.QStandardItem()
      item.setData(colorNode.GetColorName(i),qt.Qt.DisplayRole)
      item.setEditable(True)
      self.model.setItem(row,col,item)
      self.items.append(item)
      col += 1
      
      # Accession number.
      item = qt.QStandardItem()
      item.setData(accessionNo, qt.Qt.DisplayRole)
      item.setEditable(False)
      self.model.setItem(row,col,item)
      self.items.append(item)
      col += 1
      
      # Stats from statsLogic.
      for k in LabelStatsLogic.HEADER_KEYS:
        item = qt.QStandardItem()
        # set data as float with Qt::DisplayRole
        item.setData(statsLogic.labelStats[i,k],qt.Qt.DisplayRole)
        item.setToolTip(colorNode.GetColorName(i))
        item.setEditable(False)
        self.model.setItem(row,col,item)
        self.items.append(item)
        col += 1
      row += 1

    # Set column headers and widths.
    self.labelStatisticsTableView.setColumnWidth(0,30)
    self.model.setHeaderData(0,1,"")
    self.model.setHeaderData(1,1,"LabelName")
    self.model.setHeaderData(2,1,"AccessionNo")
    col = 3
    for k in LabelStatsLogic.HEADER_KEYS:
      self.labelStatisticsTableView.setColumnWidth(col,10*len(k))
      self.model.setHeaderData(col,1,k)
      col += 1

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
    if params.pastImageTag in parts:
      # Past series.
      seriesIndex = params.pastLesionMapFilenameParts.SeriesNumber
      postfix = params.lesionMapSeriesNameTag + "_" + params.annStepTag + "_" + params.registrationStepTag + "_" + params.thresholdStepTag + "_" + params.vesselRemovalStepTag
      # postfix = "_?_Sag.VIBRANT.wo.FS_LesionProbMap_reg_thresh_vr"
    else:
      # Current series.
      seriesIndex = params.currentLesionMapFilenameParts.SeriesNumber
      postfix = params.lesionMapSeriesNameTag + "_" + params.annStepTag + "_" + params.thresholdStepTag + "_" + params.vesselRemovalStepTag
      # postfix = "_?_Sag.VIBRANT.wo.FS_LesionProbMap_thresh_vr"
    lesionMapName = ('_').join(parts[0:seriesIndex]) + postfix
    print lesionMapName
    lesionMapNode = slicer.util.getNode(lesionMapName)
    return lesionMapNode
  
  def getBreastMask(self, inputNode):
    nodeName = inputNode.GetName()
    parts = nodeName.split("_")
    if params.pastImageTag in parts:
      # Past series.
      # The pipeline doesn't generate a registered breast mask return empty node.
      breastMaskName = "None"
    else:
      # Current series.
      seriesIndex = params.currentLesionMapFilenameParts.SeriesNumber
      postfix = params.breastSegmentationSeriesNameTag + "_" + params.breastSegmentationStepTag      
      breastMaskName = ('_').join(parts[0:seriesIndex]) + postfix
    print breastMaskName
    breastMaskNode = slicer.util.getNode(breastMaskName)
    return breastMaskNode
  
  
  def generateMaskedNode(self, imageNode, maskNode, dilate=0):
    # Apply mask to image data.
    imageData = vtk.vtkImageData()
    imageData = imageNode.GetImageData()
    maskData = vtk.vtkImageData()
    maskData = maskNode.GetImageData()
    maskCast = vtk.vtkImageCast()
    maskCast.SetInputData(maskData)
    maskCast.SetOutputScalarTypeToUnsignedChar()
    maskCast.Update()
    newMaskData = maskCast.GetOutput()
    
    mask = vtk.vtkImageMask()
    mask.SetImageInputData(imageData)
    mask.SetMaskInputData(maskCast.GetOutput())
    mask.SetMaskedOutputValue(100)
    mask.Update()
    
    imageNodeName = imageNode.GetName()
    newName = imageNodeName + "_masked"
    outputNode = slicer.util.getNode(newName)
    if not outputNode:
      outputNode = self.createOutputVolumeNode(newName, 'Grey')
    self.connectImageDataToOutputNode(imageNode, outputNode, mask.GetOutput())
    
    return outputNode 
    

  def generateSubtractionImages(self, inputNode):
    nodeName = inputNode.GetName()
    parts = nodeName.split("_")
    if params.pastImageTag in parts:
      # Past series.
      seriesIndex = params.pastImageFilenameParts.SeriesNumber
      prePostfix = params.preContrastSeriesNameTag + "_" + params.registrationStepTag
      # prePostfix = "_Sag.VIBRANT.MPH_reg"      
      if params.motionCorrectionStepTag in parts:
        # Motion corrected.
        postPostfix = params.postContrastSeriesNameTag + "_" + params.motionCorrectionStepTag + "_" + params.registrationStepTag
        # postPostfix = "Sag.VIBRANT.MPH_mc_reg"
      else:
        postPostfix = params.postContrastSeriesNameTag + "_" + params.registrationStepTag
        # postPostfix = "Sag.VIBRANT.MPH_reg"
    else:
      # Current series.
      seriesIndex = params.currentImageFilenameParts.SeriesNumber
      prePostfix = params.preContrastSeriesNameTag
      # prePostfix = "_Sag.VIBRANT.MPH"
      if params.motionCorrectionStepTag in parts:
        postPostfix = params.postContrastSeriesNameTag + "_" + params.motionCorrectionStepTag
        # postPostfix = "Sag.VIBRANT.MPH_mc"
      else:
        postPostfix = postContrastSeriesNameTag
        # postPostfix = "Sag.VIBRANT.MPH"    
    
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
      
      # Set up VTK subtraction filter.
      img0Cast = vtk.vtkImageCast()
      img0Cast.SetInputData(img0Data)
      img0Cast.SetOutputScalarType(imgData.GetScalarType())
      img0Cast.ClampOverflowOn()        
      diffFilter = vtk.vtkImageMathematics()
      diffFilter.SetOperationToSubtract()
      diffFilter.SetInputConnection(1, img0Cast.GetOutputPort())  
      #diffFilter.SetInputData(1, img0Data)
      diffFilter.SetInputData(0, imgData)
      diffFilter.Update()
      
      # Check to see if there's already an output node.
      newName = ('_').join(parts[0:seriesIndex])+"_"+seriesN+"-"+series0
      outputNode = slicer.util.getNode(newName)
      if not outputNode:
        outputNode = self.createOutputVolumeNode(newName, 'Grey')
      self.connectImageDataToOutputNode(inputNode, outputNode, diffFilter.GetOutput())
      
      # Change display properties (don't show negative values).
      scalarRange = diffFilter.GetOutput().GetScalarRange()
      displayNode = outputNode.GetDisplayNode()
      displayNode.SetAutoWindowLevel(0)
      displayNode.SetThreshold(0, scalarRange[1])
      displayNode.SetWindowLevelMinMax(0, scalarRange[1])
      
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
  
  def createOutputVolumeNode(self, name, colorTable='Grey'):
    # Create new nodes to hold, display and store the subtraction image.
    outputNode = slicer.vtkMRMLScalarVolumeNode()
    outputNode.SetName(name)
    slicer.mrmlScene.AddNode(outputNode)
    colorNode = slicer.util.getNode(colorTable)
    displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
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

  def queryIsland(self, xy, sliceLogic):
    '''  
    Calculate statistics for the currently selected label.
    '''
    labelLogic = sliceLogic.GetLabelLayer()
    backgroundLogic = sliceLogic.GetBackgroundLayer()
    labelNode = labelLogic.GetVolumeNode()
    if not labelNode:
      return
    backgroundNode = backgroundLogic.GetVolumeNode()
    if not backgroundNode:
      qt.QMessageBox.warning(slicer.util.mainWindow(), 'TrackLesions', 'Background volume not selected. \nAll stats will be for the selected label.')
      backgroundNode = labelNode
    labelImageData = labelNode.GetImageData()
    xyToIJK = labelLogic.GetXYToIJKTransform()
    ijk = xyToIJK.TransformDoublePoint( xy + (0,) )
    ijk = map(lambda v: int(round(v)), ijk)
    dims = labelImageData.GetDimensions()
    for idx in xrange(3):
      if ijk[idx] < 0 or ijk[idx] >= dims[idx]:
        return
    
    labelValue = int(labelImageData.GetScalarComponentAsDouble(ijk[0], ijk[1], ijk[2], 0))    
    statsLogic = LabelStatsLogic(labelNode, labelValue, backgroundNode)
    
    return statsLogic
    
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
  
  def renderVolume(self, volumeNode, widget):
    volumeRenderingLogic = slicer.modules.volumerendering.logic()
    volumeRenderingDisplayNodeName = "VolumeRendering"+widget
    volumeRenderingDisplay = slicer.util.getNode(volumeRenderingDisplayNodeName)
    if not volumeRenderingDisplay:
      volumeRenderingDisplay = volumeRenderingLogic.CreateVolumeRenderingDisplayNode("vtkMRMLGPURayCastVolumeRenderingDisplayNode")
      volumeRenderingDisplay.SetName(volumeRenderingDisplayNodeName)
      slicer.mrmlScene.AddNode(volumeRenderingDisplay)
      volumeRenderingDisplay.RemoveAllViewNodeIDs()
      volumeRenderingDisplay.AddViewNodeID(slicer.util.getNode(widget).GetID())
    volumeRenderingDisplay.UnRegister(volumeRenderingLogic)
    volumeRenderingDisplay.SetRaycastTechnique(2)
    volumeRenderingLogic.UpdateDisplayNodeFromVolumeNode(volumeRenderingDisplay, volumeNode)
    volumeNode.AddAndObserveDisplayNodeID(volumeRenderingDisplay.GetID())
    
    viewNode = slicer.util.getNode(widget)
    viewNodeId = viewNode.GetID()
    cameraNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLCameraNode')
    for iCamera in range(slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLCameraNode')):
      cameraNode = cameraNodes.GetItemAsObject(iCamera)
      activeTag = cameraNode.GetActiveTag()
      if activeTag == viewNodeId:
        print(("rendering 3d view Widget: {0}, ViewNodeId: {1}, CameraNodeActiveTag: {2}").format(widget, viewNodeId, cameraNode.GetActiveTag))
        camera = cameraNode.GetCamera()
        camera.SetPosition(0, 600, 0)
        camera.SetViewUp(0, 0, 1)


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
    
#import vtk, qt, ctk, slicer
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
    
    volumeName = grayscaleNode.GetName()
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

