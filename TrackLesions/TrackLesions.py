﻿import os
import vtk, qt, ctk, slicer
import vtkITK
from fnmatch import fnmatch
from slicer.ScriptedLoadableModule import *
import logging
#import ConfigParser
from MyEditorLib import MyEditor
from MyEditorLib.EditUtil import EditUtil
#from MyEditorLib.EditOptions import HelpButton
from TrackLesionsLib import TrackLesionsParams_LongitudinalStudy as params
from MyEditorLib import LabelStatsLogic


compareLayout = (
    "<layout type=\"horizontal\">"
    " <item>"
    "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Current_Sub1\">"
    "   <property name=\"orientation\" action=\"default\">Sagittal</property>"
    "   <property name=\"viewlabel\" action=\"default\">C_1</property>"
    "   <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
    "  </view>"
    " </item>"
    " <item>"
    "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Past1_Sub1\">"
    "   <property name=\"orientation\" action=\"default\">Sagittal</property>"
    "   <property name=\"viewlabel\" action=\"default\">P1_1</property>"
    "   <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
    "  </view>"
    " </item>"
    " <item>"
    "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Past2_Sub1\">"
    "   <property name=\"orientation\" action=\"default\">Sagittal</property>"
    "   <property name=\"viewlabel\" action=\"default\">P2_1</property>"
    "   <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
    "  </view>"
    " </item>"    
    "</layout>")
  
compareLayoutId = 501

currentFourUpView = (
  "<layout type=\"vertical\">"
  " <item>"
  "  <layout type=\"horizontal\">"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Current_Sub1\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">C_1</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Current_Sub2\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">C_2</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
    "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Current_Sub3\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">C_3</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
    "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Current_Sub4\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">C_4</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
  "  </layout>"
  " </item>"
  " <item>"
  "  <view class=\"vtkMRMLViewNode\" singletontag=\"Current_VR\">"
  "   <property name=\"viewlabel\" action=\"default\">C_VR</property>"
  "  </view>"
  " </item>"  
  "</layout>")
currentFourUpViewId = 502

past1FourUpView = (
  "<layout type=\"vertical\">"
  " <item>"
  "  <layout type=\"horizontal\">"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Past1_Sub1\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">P1_1</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Past1_Sub2\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">P1_2</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
    "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Past1_Sub3\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">P1_3</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
    "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Past1_Sub4\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">P1_4</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
  "  </layout>"
  " </item>"
  " <item>"
  "  <view class=\"vtkMRMLViewNode\" singletontag=\"Past1_VR\">"
  "   <property name=\"viewlabel\" action=\"default\">P1_VR</property>"
  "  </view>"
  " </item>"  
  "</layout>")
past1FourUpViewId = 503

past2FourUpView = (
  "<layout type=\"vertical\">"
  " <item>"
  "  <layout type=\"horizontal\">"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Past2_Sub1\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">P2_1</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
  "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Past2_Sub2\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">P2_2</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
    "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Past2_Sub3\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">P2_3</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
    "   <item>"
  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Past2_Sub4\">"
  "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
  "     <property name=\"viewlabel\" action=\"default\">P2_4</property>"
  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
  "    </view>"
  "   </item>"
  "  </layout>"
  " </item>"
  " <item>"
  "  <view class=\"vtkMRMLViewNode\" singletontag=\"Past2_VR\">"
  "   <property name=\"viewlabel\" action=\"default\">P2_VR</property>"
  "  </view>"
  " </item>"  
  "</layout>")
past2FourUpViewId = 504


#
# TrackLesions
#

LONG_STUDY_FLAG = True
VOLUME_RENDER = False

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
    This is a scripted loadable module bundled in an extension that has been
    customized for longitudinal DCE-MRI breast studies. 
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

    self.timePoints = ["Current", "Past1", "Past2"]
    self.sliceWidgetNames = ["Sub1", "Sub2", "Sub3", "Sub4"]
    self.viewLogicNames = ["ViewCurrent_VR", "ViewPast1_VR", "ViewPast2_VR"]  
    self.styleObserverTags = []
    self.sliceWidgetsPerStyle = {}   
    self.studies = []
    self.currentDirectory = ""
    self.logic = TrackLesionsLogic()
    self.bIgnoreSliceNodeEvents = False
        
    # Instantiate and connect widgets ...
    
    # Set custom layouts.
    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(compareLayoutId, compareLayout)
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(currentFourUpViewId, currentFourUpView)
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(past1FourUpViewId, past1FourUpView)
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(past2FourUpViewId, past2FourUpView)
    # Have to call setLayout for all layouts to force creation of slice widgets    
    layoutManager.setLayout(currentFourUpViewId)
    layoutManager.setLayout(past1FourUpViewId)
    layoutManager.setLayout(past2FourUpViewId)
    layoutManager.setLayout(compareLayoutId)
    self.currentView = 'CompareView'
    self.setLinkedControl()

    #
    # Main panel
    #
    mainCollapsibleButton = ctk.ctkCollapsibleButton()
    mainCollapsibleButton.text = "TrackLesions"
    self.layout.addWidget(mainCollapsibleButton)
    mainLayout = qt.QFormLayout(mainCollapsibleButton)
    self.tabWidget = qt.QTabWidget()
    mainLayout.addWidget(self.tabWidget)
           
    #
    # Patient area
    #
    self.patientFormWidget = qt.QWidget()
    patientFormLayout = qt.QFormLayout()
    self.patientFormWidget.setLayout(patientFormLayout)
    self.tabWidget.addTab(self.patientFormWidget, "Load")
    
    # Patient selector
    self.openPatientButton = qt.QPushButton("Select Patient Folder")
    patientFormLayout.addRow(self.openPatientButton)
    
    # Patient info
    self.patientLayoutBox = qt.QGroupBox("Patient Info")
    self.patientLayoutBox.setLayout(qt.QFormLayout())    
    self.patientIdLabel = qt.QLabel()
    self.patientIdLabel.setText("<Select patient>")
    self.patientLayoutBox.layout().addRow("Patient ID:", self.patientIdLabel)    
    self.patientInfoView = qt.QTreeView()
    self.patientInfoView.sortingEnabled = False
    self.patientLayoutBox.layout().addRow(self.patientInfoView)
    self.setPatientInfo(reset=True)  
    patientFormLayout.addRow(self.patientLayoutBox)
    
    #
    # View area
    #
    self.viewFormWidget = qt.QWidget()
    viewFormLayout = qt.QFormLayout()
    self.viewFormWidget.setLayout(viewFormLayout)
    self.viewFormWidget.setEnabled(False)
    self.tabWidget.addTab(self.viewFormWidget, "View")
    
    # View group box
    self.viewRadioBox = qt.QGroupBox("View")
    self.viewRadioBox.setLayout(qt.QHBoxLayout())
    self.compareViewRadioButton = qt.QRadioButton()
    self.viewRadioBox.layout().addWidget(self.compareViewRadioButton)    
    self.compareViewRadioButton.text = "Compare"
    self.compareViewRadioButton.setToolTip("Display the first subtraction series for each study.")
    self.currentViewRadioButton = qt.QRadioButton()
    self.viewRadioBox.layout().addWidget(self.currentViewRadioButton)
    self.currentViewRadioButton.text = "Current"
    self.currentViewRadioButton.setToolTip("Display dynamic subtraction images for the most recent study.")
    self.past1ViewRadioButton = qt.QRadioButton()
    self.viewRadioBox.layout().addWidget(self.past1ViewRadioButton)
    self.past1ViewRadioButton.text = "Past1"
    self.past1ViewRadioButton.setToolTip("Display dynamic subtraction images for the first prior study.")
    self.past2ViewRadioButton = qt.QRadioButton()
    self.viewRadioBox.layout().addWidget(self.past2ViewRadioButton)
    self.past2ViewRadioButton.text = "Past2"
    self.past2ViewRadioButton.setToolTip("Display dynamic subtraction images for the second prior study.")
    self.compareViewRadioButton.checked = True
    viewFormLayout.addRow(self.viewRadioBox)

    # Navigate group box
    self.navigateFrame = qt.QGroupBox("Navigate")
    self.navigateFrame.setLayout(qt.QFormLayout())
    viewFormLayout.addRow(self.navigateFrame)
    instructions = qt.QLabel("Middle Scroll: scroll slices\n"
                             "Right Drag Up/Down: zoom out/in")
    self.navigateFrame.layout().addRow(instructions)

    # Slice selector
    self.inputSliceLabel = qt.QLabel("Jump to slice:")
    self.inputSliceLabel.setToolTip("Navigate sagittal views to the selected slice.")
    self.inputSliceSelector = qt.QSpinBox()
    self.inputSliceSelector.singleStep = (1)
    self.inputSliceSelector.minimum = (0)
    self.inputSliceSelector.maximum = (0)
    self.inputSliceSelector.value = (0)
    self.inputSliceSelector.setToolTip("Navigate sagittal views to the selected slice.")
    self.navigateFrame.layout().addRow(self.inputSliceLabel, self.inputSliceSelector)

    # Reset FOV (slice) button
    self.resetSliceFovButton = qt.QPushButton("Reset Slice Field of View")
    self.resetSliceFovButton.toolTip = "Re-center current slice and fit to field of view."
    self.resetSliceFovButton.enabled = True
    self.navigateFrame.layout().addRow(self.resetSliceFovButton)

    # Reset FOV button
    self.resetFovButton = qt.QPushButton("Reset Volume Field of View")
    self.resetFovButton.toolTip = "Re-center volume and fit to field of view."
    self.resetFovButton.enabled = True
    self.navigateFrame.layout().addRow(self.resetFovButton)

    #HelpButton(self.navigateFrame, "Middle Scroll: scroll slices\nRight Drag Up/Down: zoom out/in")

    # Window/Level group box
    self.windowingFrame = qt.QGroupBox("Window/Level")
    self.windowingFrame.setLayout(qt.QFormLayout())
    viewFormLayout.addRow(self.windowingFrame)
    instructions = qt.QLabel("Left Drag Left/Right: window\n"
                             "Left Drag Up/Down: level")
    self.windowingFrame.layout().addRow(instructions)

    # Reset windowing button
    self.resetWindowingButton = qt.QPushButton("Reset Windowing")
    self.resetWindowingButton.toolTip = "Reset windowing of subtraction images to default values."
    self.resetWindowingButton.enabled = True
    self.windowingFrame.layout().addRow(self.resetWindowingButton)

    #HelpButton(self.windowingFrame, "Left Drag Left/Right: window\nLeft Drag Up/Down: level")

    # Uh Oh group box
    self.uhohFrame = qt.QGroupBox("Uh Oh")
    self.uhohFrame.setLayout(qt.QFormLayout())
    viewFormLayout.addRow(self.uhohFrame)

    # Reset views button
    self.resetViewsButton = qt.QPushButton("Reset Data in Views")
    self.resetViewsButton.toolTip = "Load default images and labels in views. " \
                                    "Recenters and resynchronizes views. " \
                                    "Use this if your volumes/studies are" \
                                    "loaded in the wrong windows."
    self.resetViewsButton.enabled = True
    self.uhohFrame.layout().addRow(self.resetViewsButton)
             
    #
    # Contour area
    #
    self.contourFormWidget = qt.QWidget()
    contourFormLayout = qt.QVBoxLayout()
    self.contourFormWidget.setLayout(contourFormLayout)
    self.contourFormWidget.setEnabled(False)
    self.tabWidget.addTab(self.contourFormWidget, "Contour")

    # Current label
    self.currentLabelFrame = qt.QGroupBox("Label Volume(s)")
    self.currentLabelFrame.setLayout(qt.QHBoxLayout())
    self.currentLabelLabel = qt.QLabel("Current label volume:")
    self.currentLabelFrame.layout().addWidget(self.currentLabelLabel)
    self.currentLabelSelector = qt.QComboBox()
    self.currentLabelFrame.layout().addWidget(self.currentLabelSelector)
    contourFormLayout.addWidget(self.currentLabelFrame)
    
    # Edit tools
    self.editBoxFrame = qt.QFrame()
    self.editBoxFrame.objectName = 'EditBoxFrame'
    self.editBoxFrame.setLayout(qt.QVBoxLayout())
    self.editor = MyEditor.EditorWidget(self.contourFormWidget, False)

    #
    # Save area
    #
    self.saveFormWidget = qt.QWidget()
    saveFormLayout = qt.QVBoxLayout()
    self.saveFormWidget.setLayout(saveFormLayout)
    self.saveFormWidget.setEnabled(False)
    self.tabWidget.addTab(self.saveFormWidget, "Save")

    # Current label
    self.saveLabelFrame = qt.QGroupBox("Label Volume(s)")
    self.saveLabelFrame.setLayout(qt.QVBoxLayout())
    # model and view for stats table
    self.labelTableView = qt.QTableView()
    self.labelTableView.sortingEnabled = True
    self.saveLabelFrame.layout().addWidget(self.labelTableView)
    self.labelTableModel = qt.QStandardItemModel()
    self.labelTableView.setModel(self.labelTableModel)
    self.labelTableColHeaders = ["Label Volume", "Modified", "Save", "Overwrite", "Save as"]
    self.labelTableModel.setHorizontalHeaderLabels(self.labelTableColHeaders)
    self.labelTableView.verticalHeader().visible = False
    self.labelTableView.setMaximumHeight(200)
    saveFormLayout.addWidget(self.saveLabelFrame)

    # Save contours button
    self.saveContoursButton = qt.QPushButton("Save Contours")
    self.saveContoursButton.toolTip = "Save contours as .mha label maps."
    self.saveContoursButton.enabled = True
    saveFormLayout.addWidget(self.saveContoursButton)
    saveFormLayout.addStretch(1)

    #
    # Analysis Area - Disabled for longitudinal study.
    #
    analysisCollapsibleButton = ctk.ctkCollapsibleButton()
    analysisCollapsibleButton.text = "Analysis"
    analysisCollapsibleButton.collapsed = True

    # Layout within the dummy collapsible button
    analysisFormLayout = qt.QFormLayout(analysisCollapsibleButton)
    
    #
    # Calculate subtraction images button
    #
    self.Button = qt.QPushButton("Calculate subtraction images")
    self.Button.toolTip = "Subtract pre-contrast image from post-contrast images."
    self.Button.enabled = True
    analysisFormLayout.addRow(self.Button)
        
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
    self.labelstatisticsCollapsibleButton.collapsed = True
    # Layout within the collapsible button
    self.labelstatisticsLayout = qt.QFormLayout(self.labelstatisticsCollapsibleButton)
    # Table View to display Label statistics
    self.labelStatisticsTableView = qt.QTableView()
    self.labelStatisticsTableView.sortingEnabled = True
    self.labelstatisticsLayout.addWidget(self.labelStatisticsTableView)
    self.labelStatisticsTableView.minimumHeight = 200
    self.initializeStats()    
    
    # Add vertical spacer
    #self.layout.addStretch(1)
  
    # Connections
    self.openPatientButton.connect("clicked()", self.onOpenPatient)
    self.inputSliceSelector.connect("valueChanged(int)", self.onInputSliceSelect)
    self.compareViewRadioButton.connect('clicked()', self.onViewSelected)
    self.currentViewRadioButton.connect('clicked()', self.onViewSelected)
    self.past1ViewRadioButton.connect('clicked()', self.onViewSelected)
    self.past2ViewRadioButton.connect('clicked()', self.onViewSelected) 
    self.resetWindowingButton.connect('clicked()', self.onResetWindowing)
    self.resetSliceFovButton.connect('clicked()', self.resetSliceFieldOfView)
    self.resetFovButton.connect('clicked()', self.resetFieldOfView)
    self.resetViewsButton.connect('clicked()', self.onResetViews)
    self.tabWidget.connect('currentChanged(int)', self.onTabChanged)
    self.currentLabelSelector.connect('currentIndexChanged(QString)', self.onLabelSelect)
    self.labelTableView.connect("clicked(QModelIndex)", self.onLabelTableSelect)
    self.saveContoursButton.connect('clicked()', self.onSaveContours)     
    self.findIslandsButton.connect('clicked(bool)', self.onConvertMapToLabelButton)
    self.saveIslandsButton.connect('toggled(bool)', self.onSaveIslandsButtonToggled)
    self.queryIslandsButton.connect('toggled(bool)', self.onQueryIslandsButtonToggled)    
    self.Button.connect('clicked(bool)', self.onButton)

    self.sliceNodeTags = []
    sliceNodeNames = self.getSliceWidgets("*", "Sagittal")
    for name in sliceNodeNames:
      sliceLogic = slicer.app.layoutManager().sliceWidget(name).sliceLogic()
      sliceNode = sliceLogic.GetSliceNode()
      tag = sliceNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.sliceNodeEvent, 1.0)
      self.sliceNodeTags.append([sliceNode, tag])
      
  def removeLeftButtonObservers(self):
    # Remove observers and reset
    for observee, tag in self.styleObserverTags:
      observee.RemoveObserver(tag)
    self.styleObserverTags = []
    self.sliceWidgetsPerStyle = {}

  def addLeftButtonObservers(self):
    # Observe left button releases in all TrackLesions slice widgets.
    for timePoint in self.timePoints:
      for name in self.sliceWidgetNames:
        sliceWidgetName = timePoint + "_" + name
        sliceWidget = slicer.app.layoutManager().sliceWidget(sliceWidgetName)
        if sliceWidget:
          style = sliceWidget.sliceView().interactorStyle()
          self.sliceWidgetsPerStyle[style] = sliceWidget
          tag = style.AddObserver("LeftButtonReleaseEvent", self.processEvent)
          self.styleObserverTags.append([style, tag])

  def clearParams(self):
    self.studies = []
    self.currentDirectory = ""


  def cleanup(self):
    for sliceNode, tag in self.sliceNodeTags:
      sliceNode.RemoveObserver(tag)
    self.removeLeftButtonObservers()
    self.clearParams()

  def resetSliceFieldOfView(self):
    self.setLinkedControl()
    layoutManager = slicer.app.layoutManager()
    sliceLogic = layoutManager.sliceWidget("Current_Sub1").sliceLogic()
    sliceNode = sliceLogic.GetSliceNode()
    winDims = sliceNode.GetDimensions()
    whRatio = float(winDims[0])/winDims[1]
    imgDims = [0, 0, 0]
    imgCenter = [0, 0, 0]
    sliceLogic.GetBackgroundSliceDimensions(imgDims, imgCenter)
    currentFov = sliceNode.GetFieldOfView()
    sliceLogic.StartSliceNodeInteraction(34)  # vtkMRMLSliceNode::FieldOfViewFlag=2 and XYZOriginFlag=32
    if whRatio < 1.0:
      # width < height --> fit img width to slice node width
      sliceNode.SetFieldOfView(imgDims[0], imgDims[1]/whRatio, currentFov[2])
    else:
      # width > height --> fit img height to slice node height
      sliceNode.SetFieldOfView(imgDims[0]*whRatio, imgDims[1], currentFov[2])
    offset = sliceNode.GetSliceOffset()
    sliceNode.SetXYZOrigin(0.0, 0.0, offset)
    sliceNode.UpdateMatrices()
    sliceLogic.EndSliceNodeInteraction()

  def resetFieldOfViewForTheFirstTime(self):
    # Have to display each layout using processEvents() in order for each
    # slice node to be created and know its true size. This flickers and is slow,
    # but it's the only way to make all slice nodes have the same FOV.
    layoutIds = [currentFourUpViewId, past1FourUpViewId, past2FourUpViewId, compareLayoutId]
    viewNames = ["CompareView", "CurrentView", "Past1View", "Past2View"]
    widgetNames = ["Current_Sub1", "Past1_Sub1", "Past2_Sub2", "Current_Sub1"]
    layoutManager = slicer.app.layoutManager()
    for i, id in enumerate(layoutIds):
      layoutManager.setLayout(id)
      slicer.app.processEvents()
      sliceLogic = layoutManager.sliceWidget(widgetNames[i]).sliceLogic()    
      sliceLogic.StartSliceNodeInteraction(8)  # vtkMRMLSliceNode::ResetFieldOfViewFlag
      sliceLogic.FitSliceToAll()
      sliceLogic.GetSliceNode().UpdateMatrices()
      sliceLogic.EndSliceNodeInteraction()
    self.setView(self.currentView)
    
  
  def resetFieldOfView(self):
    self.setLinkedControl()
    layoutManager = slicer.app.layoutManager()
    sliceLogic = layoutManager.sliceWidget("Current_Sub1").sliceLogic()
    sliceLogic.StartSliceNodeInteraction(8)  # vtkMRMLSliceNode::ResetFieldOfViewFlag
    sliceLogic.FitSliceToAll()
    sliceLogic.GetSliceNode().UpdateMatrices()
    sliceLogic.EndSliceNodeInteraction()
      
        
  def setNavigation(self, bool):
    # Turn on navigation.
    crosshairNode = slicer.util.getNode("vtkMRMLCrosshairNode*")
    if crosshairNode:
      if bool:
        crosshairNode.SetCrosshairMode(5)
        crosshairNode.SetNavigation(1)
      else:
        crosshairNode.SetCrosshairMode(1)
        crosshairNode.SetNavigation(0)
      

  def resetGuiPanel(self):
    # Reset current patient.
    self.setPatientInfo(reset=True)

    # Set view to current.
    self.compareViewRadioButton.checked = True
    self.setSliceSelector(minVal=0, maxVal=0, value=0)
    
    # Set patient tab to current and disable view and contour.
    self.tabWidget.setCurrentWidget(self.patientFormWidget)
    self.viewFormWidget.setEnabled(False)
    self.contourFormWidget.setEnabled(False)
    self.currentLabelSelector.clear()
    
    # Reset editor.
    self.editor.resetInterface()
    
    
  def setPatientInfo(self, reset=False):
    if len(self.studies) == 0:
      reset = True
    if reset:
      patientId = "<Select patient>"
    else:
      patientId = self.studies[0].patientId
    self.patientIdLabel.setText(patientId)
    self.patientInfoModel = qt.QStandardItemModel()
    for iRow, timePoint in enumerate(self.timePoints):
      item = qt.QStandardItem()
      item.setText(timePoint)
      self.patientInfoModel.setItem(iRow, 0, item)
      if not reset and len(self.studies) > 0:
        if self.studies[iRow]:
          item = qt.QStandardItem()
          item.setText(self.studies[iRow].accessionNo)
          self.patientInfoModel.setItem(iRow, 1, item)
          item = qt.QStandardItem()
          item.setText(self.studies[iRow].studyDate)
          self.patientInfoModel.setItem(iRow, 2, item)
    self.patientInfoModel.setHeaderData(0, 1, "Study")
    self.patientInfoModel.setHeaderData(1, 1, "Accession No.")
    self.patientInfoModel.setHeaderData(2, 1, "Date")      
    self.patientInfoView.setModel(self.patientInfoModel)
    for i in range(self.patientInfoModel.columnCount()):
      self.patientInfoView.resizeColumnToContents(i) 
    

  def onViewSelected(self):
    if self.compareViewRadioButton.checked:
      newView = 'CompareView'
    elif self.currentViewRadioButton.checked:
      newView = 'CurrentView'
    elif self.past1ViewRadioButton.checked:
      newView = 'Past1View'
    else:
      newView = 'Past2View'
    if self.currentView != newView:
      self.setView(newView)
      
  def setView(self, newView):
    layoutManager = slicer.app.layoutManager()
    if newView == 'CompareView':
      layoutManager.setLayout(compareLayoutId)
    elif newView == 'CurrentView':
      layoutManager.setLayout(currentFourUpViewId)
    elif newView == 'Past1View':
      layoutManager.setLayout(past1FourUpViewId)
    else:
      layoutManager.setLayout(past2FourUpViewId)
    self.currentView = newView  
    

  def updateSliceWidget(self, widget, layer, nodeID):
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

  
  def getLinkedControl(self):
    layoutManager = slicer.app.layoutManager()    
    sliceLogics = layoutManager.mrmlSliceLogics()
    for i in xrange(sliceLogics.GetNumberOfItems()):
      sliceLogic = sliceLogics.GetItemAsObject(i)
      sliceCompositeNode = sliceLogic.GetSliceCompositeNode()
      isLinked = sliceCompositeNode.GetLinkedControl()
      print sliceCompositeNode.GetID() + " is linked = " + str(isLinked) 

  
  def setLinkedControl(self):
    layoutManager = slicer.app.layoutManager()    
    sliceLogics = layoutManager.mrmlSliceLogics()
    for i in xrange(sliceLogics.GetNumberOfItems()):
      sliceLogic = sliceLogics.GetItemAsObject(i)
      sliceCompositeNode = sliceLogic.GetSliceCompositeNode()
      sliceCompositeNode.SetLinkedControl(1)

  def getModifiedLabelNodes(self):
    labelNodeDict = slicer.util.getNodes(pattern="*label*")
    for name, node in labelNodeDict.iteritems():
      if not node.GetModifiedSinceRead():
        del labelNodeDict[name]
    return labelNodeDict.values()


  def onOpenPatient(self):
    # Prompt to close current scene if data is currently loaded.
    if len(self.studies) > 0:
      qResult = qt.QMessageBox.question(slicer.util.mainWindow(), "Close patient", 
                                        "Close the current patient?\nPress Cancel to continue working with this patient.",
                                        qt.QMessageBox.Ok | qt.QMessageBox.Cancel,
                                        qt.QMessageBox.Cancel)
      if qResult == qt.QMessageBox.Cancel:
        return

      modifiedLabelNodes = self.getModifiedLabelNodes()
      if len(modifiedLabelNodes) > 0:
        qResult = qt.QMessageBox.question(slicer.util.mainWindow(), "Close patient",
                                          "Discard changes to label volumes?\nPress Cancel to continue working with this patient.",
                                          qt.QMessageBox.Ok | qt.QMessageBox.Cancel,
                                          qt.QMessageBox.Cancel)
        if qResult == qt.QMessageBox.Cancel:
          return

      slicer.mrmlScene.Clear(0)
      self.resetGuiPanel()
      self.clearParams()
      self.removeLeftButtonObservers()
       
    # Create custom Qt dialog here instead of using slicer.util.openadddatadialog() to avoid
    # loaded scenes and other non-.mha data.
    dir = qt.QFileDialog.getExistingDirectory(slicer.util.mainWindow(), 
                                              "Select Patient Folder", "", 
                                              qt.QFileDialog.DontUseNativeDialog)
    if not dir:
      return

    retNodes = []
    labelNodes = []
    for root, dirs, files in os.walk(dir):
      for file in files:
        if file.endswith(".mha"):
          if file.lower().find("label") > 0:
            # Label volume.
            retNode = slicer.util.loadLabelVolume(os.path.join(root, file), returnNode=True)[1]
            labelNodes.append(retNode)
          else:
            # Image volume.
            retNode = slicer.util.loadVolume(os.path.join(root, file), returnNode=True)[1]
            retNodes.append(retNode)

    # Sort input data into separate studies.
    self.studies = self.logic.sortVolumeNodes(retNodes)
    if len(self.studies) == 0:
      qt.QMessageBox.warning(slicer.util.mainWindow(), "Load patient",
                             "Incomplete patient folder. \nUnable to process.")
      # TODO: Disable processing buttons
      return

    # Set current directory for saving label volumes.
    diffNodeFilename = self.studies[0].diffNodes[0].GetStorageNode().GetFileName()
    self.currentDirectory = os.path.dirname(diffNodeFilename)    
    slicer.mrmlScene.SetRootDirectory(self.currentDirectory)
    
    # Display patient info in main GUI panel.
    self.setPatientInfo()
    
    # Check to see if existing label nodes were loaded.
    labelNodeDict = slicer.util.getNodes(pattern="*_label*")
    nNodes = len(labelNodeDict)
    if nNodes > 0:
      intVals = []
      for node in labelNodeDict.values():
        name = node.GetName()
        parts = name.split("_label_")
        if len(parts) == 1:
          # The basename is *_label
          intVal = 0
        else:
          try:
            # The basename is *_label_<int>
            intVal = int(parts[-1])
          except ValueError:
            # The basename is *_label_<string>
            intVal = 0
        intVals.append(intVal)
      overallMax = max(intVals)
      postfix = str(overallMax + 1)
    else:
      postfix = ""
    
    labelNodes = []
    for iStudy, study in enumerate(self.studies):
      if not LONG_STUDY_FLAG:
        # Calculate subtraction images.
        self.logic.calculateSubtractionImages(study)
      else:       
        # Set windowing of subtraction images (don't show negative values).
        for volumeNode in study.diffNodes:
          imageData = vtk.vtkImageData()
          imageData = volumeNode.GetImageData()      
          scalarRange = imageData.GetScalarRange()
          displayNode = volumeNode.GetDisplayNode()
          displayNode.SetAutoWindowLevel(0)
          #displayNode.SetThreshold(0, scalarRange[1])
          displayNode.SetWindowLevelMinMax(0, scalarRange[1])
        
      # Set up label nodes for lesion contouring.
      volumeNode = study.diffNodes[0]
      labelNodeName = volumeNode.GetName() + "_label" + (postfix if not postfix else ("_"+postfix))
      labelNode = slicer.modules.volumes.logic().CreateAndAddLabelVolume(slicer.mrmlScene, volumeNode, labelNodeName)
      colorNode = slicer.util.getNode('GenericColors')
      labelNode.GetDisplayNode().SetAndObserveColorNodeID(colorNode.GetID())
      storageNode = labelNode.CreateDefaultStorageNode()
      slicer.mrmlScene.AddNode(storageNode)
      labelNode.SetAndObserveStorageNodeID(storageNode.GetID())
      storageNode.SetFileName(self.currentDirectory+os.sep+labelNode.GetName()+".mha")
      study.labelNode = labelNode
      labelNodes.append(labelNode)      
      
      # Attach to slice and volume displays.
      self.attachStudyToSliceWidgets(study, self.timePoints[iStudy])
      
      if VOLUME_RENDER:
        self.logic.maskFirstDiffNodeForVR(study)
        self.attachStudyToVolumeWidget(study, self.timePoints[iStudy])
    
    self.editor.setLabelNodes(labelNodes)
    postfixes = self.getLabelNodePostfixes()
    index = postfixes.index(postfix)
    self.currentLabelSelector.clear()
    for postfix in postfixes:
      self.currentLabelSelector.addItem("label" + (postfix if not postfix else ("_"+postfix)))
    self.currentLabelSelector.setCurrentIndex(index)
    self.populateLabelTable()
    
    self.resetFieldOfViewForTheFirstTime()
    
    # Enable view and contour features.
    self.viewFormWidget.setEnabled(True)
    self.contourFormWidget.setEnabled(True)
    self.saveFormWidget.setEnabled(True)
      
    # Set slice selector.
    dims = self.studies[0].diffNodes[0].GetImageData().GetDimensions()
    maxSliceNo = dims[2]+1
    curSliceNo = round(maxSliceNo/2)
    self.setSliceSelector(minVal=0, maxVal=maxSliceNo, value=curSliceNo)
    
    # Enable lesion contouring.
    EditUtil.setLabel(1)

  def populateLabelTable(self):
    postfixes = self.getLabelNodePostfixes()
    self.items = []
    for iRow, postfix in enumerate(postfixes):
      # Label volume name.
      item = qt.QStandardItem()
      labelName = "label"+(postfix if not postfix else ("_"+postfix))
      item.setData(labelName, qt.Qt.DisplayRole)
      item.setEditable(False)
      self.labelTableModel.setItem(iRow, self.labelTableColHeaders.index("Label Volume"), item)
      self.items.append(item)
      labelNodeDict = slicer.util.getNodes(pattern="*_label"+(postfix if not postfix else ("_"+postfix)))
      bModified = False
      checkState = 0  # Qt::Unchecked
      node = labelNodeDict.values()[0]
      storageNode = node.GetStorageNode()
      for name, node in labelNodeDict.iteritems():
        if node.GetModifiedSinceRead() and self.logic.hasLabels(node):
          bModified = True
          checkState = 2  # Qt::Checked
          break
      # Modified state.
      item = qt.QStandardItem()
      item.setEditable(False)
      item.setCheckState(checkState)
      self.labelTableModel.setItem(iRow, self.labelTableColHeaders.index("Modified"), item)
      self.items.append(item)
      # Save (checked if modified by default).
      item = qt.QStandardItem()
      item.setEditable(False)
      item.setCheckable(bModified)
      item.setCheckState(checkState)
      self.labelTableModel.setItem(iRow, self.labelTableColHeaders.index("Save"), item)
      self.items.append(item)
      # Overwrite (checked if modified by default).
      item = qt.QStandardItem()
      item.setEditable(False)
      item.setCheckable(bModified)
      item.setCheckState(checkState)
      self.labelTableModel.setItem(iRow, self.labelTableColHeaders.index("Overwrite"), item)
      self.items.append(item)
      # Save as (set to label volume name and disabled by default).
      item = qt.QStandardItem()
      item.setData(labelName, qt.Qt.DisplayRole)
      item.setEnabled(False)
      self.labelTableModel.setItem(iRow, self.labelTableColHeaders.index("Save as"), item)
      self.items.append(item)
    self.labelTableView.setModel(self.labelTableModel)
    for iCol in range(len(self.labelTableColHeaders)):
      self.labelTableView.resizeColumnToContents(iCol)


  def getLabelNodePostfixes(self):
    ''' Returns a reverse sorted list of unique label node postfixes attached to the scene.
        A postfix is the version number following the "label" portion of the node name, e.g.:
          <patId>_<dateX>_<accessionNoX>_<subY>_label_<postfix>
    '''
    uniquePostfixes = []
    labelNodeDict = slicer.util.getNodes(pattern="*_label*")
    nNodes = len(labelNodeDict)
    if nNodes == 0:
      return uniquePostfixes

    # Get postfix and accession number for each label node.
    allPostfixes = []
    allAccessionNos = []
    for name, node in labelNodeDict.iteritems():
      parts = name.split("_")
      accessionNo = parts[params.imageFilenameParts.AccessionNumber]
      parts = name.split("_label_")
      if len(parts) == 1:
        # The basename is *_label
        postfix = ""
      else:
        # The basename is *_label_<postfix>
        postfix = str(parts[-1])
      allPostfixes.append(postfix)
      allAccessionNos.append(accessionNo)

    # Make sure each study has a label node with each unique postfix.
    uniquePostfixes = list(set(allPostfixes))
    for uniquePostfix in uniquePostfixes:
      # Get the accession nos. for each label node with the unique postfix.
      accessionNos = []
      for i, postfix in enumerate(allPostfixes):
        if postfix == uniquePostfix:
          accessionNos.append(allAccessionNos[i])

      # Make sure all studies are accounted for.
      for study in self.studies:
        if study.accessionNo not in accessionNos:
          uniquePostfixes.remove(uniquePostfix)
          continue

    return sorted(uniquePostfixes, reverse=True)

  def setSliceSelector(self, minVal=None, maxVal=None, value=None):
    # Update slice selector widget according to current image dimensions.
    if maxVal:
      self.inputSliceSelector.maximum = (maxVal)
    if minVal:
      self.inputSliceSelector.minimum = (minVal)
    if value:
      if value < self.inputSliceSelector.minimum:
        value = self.inputSliceSelector.minimum
      elif value > self.inputSliceSelector.maximum:
        value = self.inputSliceSelector.maximum
      self.inputSliceSelector.value = (value)


  def onInputSliceSelect(self, iSlice):
    self.bIgnoreSliceNodeEvents = True
    self.setSlice(iSlice)
    self.bIgnoreSliceNodeEvents = False
    
    
  def onResetWindowing(self):
    for study in self.studies:
      for volumeNode in study.diffNodes:
        self.setWindowing(volumeNode, 0)

        
  def setWindowing(self, volumeNode, winMin=None, winMax=None):  
    imageData = vtk.vtkImageData()
    imageData = volumeNode.GetImageData()
    displayNode = volumeNode.GetDisplayNode()
    if not imageData or not displayNode:
      return
    if winMin == None and winMax == None:
      displayNode.SetAutoWindowLevel(1)
    else:
      scalarRange = imageData.GetScalarRange()
      if winMin == None:
        winMin = scalarRange[0]
      if winMax == None:
        winMax = scalarRange[1]
      if winMin > winMax:
        return        
      displayNode.SetAutoWindowLevel(0)
      #displayNode.SetThreshold(winMin, winMax)
      displayNode.SetWindowLevelMinMax(winMin, winMax)
      

  def onResetViews(self):
    # Attach volume and label nodes to each compound view node.
    if len(self.studies) == 0:
      # Sort nodes into separate studies.
      self.studies = self.logic.sortVolumeNodes()
      if len(self.studies) == 0:
        qt.QMessageBox.warning(slicer.util.mainWindow(), "Reset views",
                               "Incomplete patient folder. \nPlease try reloading data.")
        # TODO: Disable processing buttons
        return

    self.setPatientInfo()

    labelNodes = []      
    for iStudy, study in enumerate(self.studies):
      if not LONG_STUDY_FLAG:
        # Calculate subtraction images.
        self.logic.calculateSubtractionImages(study)
      else:
        # Set windowing of subtraction images (don't show negative values).
        for volumeNode in study.diffNodes:
          self.setWindowing(volumeNode, 0)
      
      # Set up label nodes for lesion contouring.
      if not study.labelNode:
        volumeNode = study.diffNodes[0]
        labelNodeName = volumeNode.GetName() + "_label"
        labelNode = slicer.modules.volumes.logic().CreateAndAddLabelVolume(slicer.mrmlScene, volumeNode, labelNodeName)
        colorNode = slicer.util.getNode('GenericColors')
        labelNode.GetDisplayNode().SetAndObserveColorNodeID(colorNode.GetID())
        storageNode = labelNode.CreateDefaultStorageNode()
        slicer.mrmlScene.AddNode(storageNode)
        labelNode.SetAndObserveStorageNodeID(storageNode.GetID())
        storageNode.SetFileName(self.currentDirectory+os.sep+labelNode.GetName()+".mha")
        study.labelNode = labelNode
        labelNodes.append(labelNode)
      
      # Attach to slice and volume displays.
      self.attachStudyToSliceWidgets(study, self.timePoints[iStudy])
      if VOLUME_RENDER:
        if not study.maskedDiffNode:
          self.logic.maskFirstDiffNodeForVR(study)
        self.attachStudyToVolumeWidget(study, self.timePoints[iStudy])
    
    # Set label nodes in editor.
    self.editor.setLabelNodes(labelNodes)
    
    # Set slice selector.
    dims = self.studies[0].diffNodes[0].GetImageData().GetDimensions()
    maxSliceNo = dims[2]-1
    curSliceNo = round(dims[2]/2.0)
    self.setSliceSelector(minVal=0, maxVal=maxSliceNo, value=curSliceNo)
    
    # Enable lesion contouring.
    EditUtil.setLabel(1)
        
  #
  # Contouring methods
  #

  def onLabelSelect(self, nodeNameFilter):
    # Get currently selected label postfix.
    labelNodeDict = slicer.util.getNodes(pattern="*"+nodeNameFilter)
    if len(labelNodeDict) != len(self.studies):
      logging.debug('onLabelSelect failed: incorrect number of label nodes')
      return

    # Set study label nodes.
    accessionNos = []
    for study in self.studies:
      accessionNos.append(study.accessionNo)
    for name, node in labelNodeDict.items():
      parts = name.split("_")
      accessionNo = parts[params.imageFilenameParts.AccessionNumber]
      if accessionNo not in accessionNos:
        logging.debug('onLabelSelect failed: label node accession no. {0} does not match loaded accession nos. {1}.'.format(name, ", ".join(accessionNos)))
        return
      index = accessionNos.index(accessionNo)
      self.studies[index].labelNode = node

    # Attach label nodes to slice widgets.
    for i, study in enumerate(self.studies):
      timePoint = self.timePoints[i]
      for iDiffNode in range(len(study.diffNodes)):
        widget = timePoint + "_" + self.sliceWidgetNames[iDiffNode]
        self.updateSliceWidget(widget, "Label", study.labelNode.GetID())

    # Attach label nodes to editor.
    self.editor.setLabelNodes(labelNodeDict.values())

  #
  # Save methods
  #
  def onTabChanged(self, tabIndex):
    if self.tabWidget.tabText(tabIndex) != "Contour":
      # Stop contouring (set tool to Default) if we're switched out of the Contour tab.
      self.editor.resetInterface()
    if self.tabWidget.tabText(tabIndex) == "Save":
      # Recalculate which label volumes need saving and display.
      self.populateLabelTable()


  def onLabelTableSelect(self, modelIndex):
    ''' Change file overwrite settings based on whether or not the file is to be saved.
    '''
    if modelIndex.row() == -1:
      return
    if modelIndex.column() == self.labelTableColHeaders.index('Save'):
      # Save state changed for a label volume.
      saveItem = self.labelTableModel.itemFromIndex(modelIndex)
      if not saveItem.isCheckable():
        return
      saveCheckState = saveItem.checkState()
      overwriteItem = self.labelTableModel.item(modelIndex.row(), self.labelTableColHeaders.index('Overwrite'))
      saveAsItem = self.labelTableModel.item(modelIndex.row(), self.labelTableColHeaders.index('Save as'))
      # overwriteCheckState = overwriteItem.checkState()
      if saveCheckState == 0:
        overwriteItem.setEnabled(False)
        saveAsItem.setEnabled(False)
      else:
        overwriteItem.setEnabled(True)
        saveAsItem.setEnabled(False)
    elif modelIndex.column() == self.labelTableColHeaders.index('Overwrite'):
      # Can only check/uncheck this option if it is enabled (if save is checked).
      labelNameItem = self.labelTableModel.item(modelIndex.row(), self.labelTableColHeaders.index('Label Volume'))
      overwriteItem = self.labelTableModel.item(modelIndex.row(), self.labelTableColHeaders.index('Overwrite'))
      saveAsItem = self.labelTableModel.item(modelIndex.row(), self.labelTableColHeaders.index('Save as'))
      overwriteCheckState = overwriteItem.checkState()
      if overwriteCheckState == 0:  # Unchecked = do not overwrite
        # Enable Save as and set to a unique label name.
        saveAsItem.setEnabled(True)
        postfix = self.getUniqueLabelPostfix()
        newLabelName = "label" + (postfix if not postfix else ("_"+postfix))
        saveAsItem.setText(newLabelName)
      elif overwriteCheckState == 2:  # Checked = overwrite
        # Disable Save as and set to original name.
        saveAsItem.setEnabled(False)
        saveAsItem.setText(labelNameItem.text())


  def onSaveContours(self):
    # Prompt for folder to save to.
    # directory = qt.QFileDialog.getExistingDirectory(self.parent,
    #                                                 "Save contours to folder",
    #                                                 self.currentDirectory)
    # if not directory:
    #   qResult = qt.QMessageBox.warning(slicer.util.mainWindow(), "Save contours to folder",
    #                                    "Folder not selected. Contours not saved.",
    #                                    qt.QMessageBox.Ok, qt.QMessageBox.Ok)
    #   return

    # Find label nodes selected to save in label table.
    errorList = []
    savedList = []
    nModified = 0
    for iRow in range(self.labelTableModel.rowCount()):
      bModified = self.labelTableModel.item(iRow, self.labelTableColHeaders.index("Modified")).checkState()
      if bModified:
        nModified += 1
      bSave = self.labelTableModel.item(iRow, self.labelTableColHeaders.index("Save")).checkState()
      if bSave:
        # Get all label nodes with this postfix.
        postfix = self.labelTableModel.item(iRow, self.labelTableColHeaders.index("Label Volume")).text()
        labelNodeDict = slicer.util.getNodes(pattern="*"+postfix)
        bOverwrite = self.labelTableModel.item(iRow, self.labelTableColHeaders.index("Overwrite")).checkState()
        for name, node in labelNodeDict.iteritems():
          if bOverwrite:
            filename = node.GetStorageNode().GetFileName()
          else:
            newPostfix = self.labelTableModel.item(iRow, self.labelTableColHeaders.index("Save as")).text()
            origFilename = node.GetStorageNode().GetFileName()
            path = self.currentDirectory()
            filename = path + os.sep + filename.split("")
            node.GetStorageNode().SetFileName(filename)
          bOk = self.logic.saveVTKAsMHA(node, filename)
          if not bOk:
            errorList.append(filename)
          savedList.append(filename)

    if nModified == 0:
      qResult = qt.QMessageBox.information(slicer.util.mainWindow(), "Save contours",
                                           "Label volumes have not been modified.\nNothing saved.",
                                           qt.QMessageBox.Ok, qt.QMessageBox.Ok)
      return
    if len(savedList) == 0:
      qResult = qt.QMessageBox.information(slicer.util.mainWindow(), "Save contours",
                                           "No label volumes selected for save.\nMake sure 'Save' is checked for the label volume(s) you wish to save.",
                                           qt.QMessageBox.Ok, qt.QMessageBox.Ok)
      return
    if len(errorList) > 0:
      qResult = qt.QMessageBox.error(slicer.util.mainWindow(), "Save contours",
                                     "Error saving \n{0}\n".format("\n".join(errorList)),
                                     qt.QMessageBox.Ok, qt.QMessageBox.Ok)

    qResult = qt.QMessageBox.information(slicer.util.mainWindow(), "Save contours",
                                         "Labels saved to\n{0}".format("\n".join(savedList)),
                                         qt.QMessageBox.Ok, qt.QMessageBox.Ok)
    self.populateLabelTable()


  def getUniqueLabelPostfix(self):
    """ Returns a unique postfix for a label node.
        (Postfix only, no "label_").
    """
    postfixes = self.getLabelNodePostfixes()  # Postfixes only (no "label_")
    if len(postfixes) == 1 and postfixes[0] == "":
      newPostfix = str(1)
    else:
      intVals = [int(pf) for pf in postfixes if pf != ""]
      maxVal = max(intVals)
      newPostfix = str(maxVal + 1)
    return newPostfix


  def editLabelNode(self, labelNode, volumeNode):
    EditUtil.setLabel(1)
    EditUtil.setCurrentEffect("DrawEffect")
        
    
  def onSelect(self):
    pass

    
  def attachStudyToSliceWidgets(self, study, timePoint):
    if timePoint in self.timePoints:
      for iDiffNode in range(len(study.diffNodes)):
        widget = timePoint + "_" + self.sliceWidgetNames[iDiffNode]
        self.updateSliceWidget(widget, "Background", study.diffNodes[iDiffNode].GetID())
        self.updateSliceWidget(widget, "Foreground", None)
        if study.labelNode:
          self.updateSliceWidget(widget, "Label", study.labelNode.GetID())
        

  def attachStudyToVolumeWidget(self, study, timePoint):
    if study.maskedDiffNode and timePoint in self.timePoints:
      widget = "View" + timePoint + "_VR"
      self.logic.renderVolume(study.maskedDiffNode, widget)

    
  def onButton(self):
    for iStudy, study in enumerate(self.studies):
      self.logic.calculateSubtractionImages(study)
      self.logic.maskFirstDiffNodeForVR(study)
      self.attachStudyToSliceWidgets(study, self.timePoints[iStudy])
      self.attachStudyToVolumeWidget(study, self.timePoints[iStudy])
          
      
  def onConvertMapToLabelButton(self):
    currentLabelNode = self.logic.convertMapToLabel(self.currentMapSelector.currentNode())
    if currentLabelNode:
      currentIslandNode = self.logic.identifyIslands(currentLabelNode)
    if currentIslandNode:
      self.currentLabelNode = currentIslandNode
      widgets = self.getSliceWidgets("Current")
      for widget in widgets:
        self.updateSliceWidget(widget, "Label", currentIslandNode.GetID())
        
    past1LabelNode = self.logic.convertMapToLabel(self.past1MapSelector.currentNode())
    if past1LabelNode:
      past1IslandNode = self.logic.identifyIslands(past1LabelNode)
    if past1IslandNode:
      self.past1LabelNode = past1IslandNode
      widgets = self.getSliceWidgets("Past1")
      for widget in widgets:
        self.updateSliceWidget(widget, "Label", past1IslandNode.GetID())
        
    past2LabelNode = self.logic.convertMapToLabel(self.past2MapSelector.currentNode())
    if past2LabelNode:
      past2IslandNode = self.logic.identifyIslands(past2LabelNode)
    if past2IslandNode:
      self.past2LabelNode = past2IslandNode
      widgets = self.getSliceWidgets("Past2")
      for widget in widgets:
        self.updateSliceWidget(widget, "Label", past2IslandNode.GetID())
        
        
  def onSaveIslandsButtonToggled(self, checked):
    if checked:
      self.removeLeftButtonObservers()
      self.addLeftButtonObservers()
      self.queryIslandsButton.checked = False
    else:
      self.removeLeftButtonObservers()

  def onQueryIslandsButtonToggled(self, checked):
    if checked:
      self.removeLeftButtonObservers()
      self.addLeftButtonObservers()
      self.saveIslandsButton.checked = False
    else:
      self.removeLeftButtonObservers()

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
      if self.saveIslandsButton.isChecked():
        outputNode = self.logic.saveIsland(xy, sliceLogic)
        if outputNode:
          self.updateSliceWidget(sliceLogic.GetName(), "Label", outputNode.GetID())
      elif self.queryIslandsButton.isChecked():
        statsLogic = self.logic.queryIsland(xy, sliceLogic)
        if statsLogic:
          labelNode = sliceLogic.GetLabelLayer().GetVolumeNode()
          self.populateStats(statsLogic, labelNode)

  def sliceNodeEvent(self, caller=None, event=None):
    """ A slice node has changed.
        Update the TrackLesions slice selector if the current sagittal slice has changed.
    """
    if self.bIgnoreSliceNodeEvents:
      return
    nodeName = caller.GetName()
    sliceNodeNames = self.getSliceWidgets("*", "Sagittal")
    if nodeName in sliceNodeNames:
      sliceLogic = slicer.app.layoutManager().sliceWidget(nodeName).sliceLogic()
      layerLogic = sliceLogic.GetBackgroundLayer()
      volumeNode = layerLogic.GetVolumeNode()
      if volumeNode:
        xyz = [0.0, 0.0, 0.0]
        xyToIjk = layerLogic.GetXYToIJKTransform()
        ijkFloat = xyToIjk.TransformDoublePoint(xyz)
        z = int(round(ijkFloat[2]))
        #wasBlocking = self.inputSliceSelector.blockSignals(True)
        self.inputSliceSelector.value = (z)
        #self.inputSliceSelector.blockSignals(wasBlocking)
  
  def setSlice(self, iSlice):
    # Set the slice displayed in all sagittal slice nodes.
    orientations = {'Sagittal':0, 'Coronal':1, 'Axial':2}
    sliceNodeNames = self.getSliceWidgets("*", "Sagittal")
    for name in sliceNodeNames:
      ijkToRas = vtk.vtkMatrix4x4()
      sliceLogic = slicer.app.layoutManager().sliceWidget(name).sliceLogic()
      sliceNode = sliceLogic.GetSliceNode()
      orientationString = sliceNode.GetOrientationString()
      rasIndex = orientations[orientationString]
      volNode = sliceLogic.GetBackgroundLayer().GetVolumeNode()
      if volNode:
        volNode.GetIJKToRASMatrix(ijkToRas)
        posIjk = [0, 0, 0, 1]
        posIjk[2-rasIndex] = iSlice
        posRas = ijkToRas.MultiplyPoint(posIjk)
        sliceLogic.SetSliceOffset(posRas[rasIndex])
      
  def initializeLabelSummary(self):
    # Create table.
    self.model = qt.QStandardItemModel()
    self.labelSummaryTableView.setModel(self.model)
    self.labelSummaryTableView.verticalHeader().visible = False
      
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


  def sortVolumeNodes(self, retNodes=[]):
    """Sorts the volume nodes in the scene into study objects.
    Each study contains multiple series.
    """
    studies = []
    if LONG_STUDY_FLAG:
      accessionNos = []
      for retNode in retNodes:
        parts = retNode.GetName().split("_")
        accessionNos.append(parts[params.imageFilenameParts.AccessionNumber])
      # Get unique accession numbers.
      uniqueANos = sorted(list(set(accessionNos)), reverse=True)
      for accessionNo in uniqueANos:
        study = self.getStudyVolumeNodesLongStudy(accessionNo)
        if study:
          studies.append(study)
          
    else:
      # Get all pre-contrast nodes (should be one per study).
      preContrastNodeDict = slicer.util.getNodes(pattern="*"+params.preContrastSeriesNameTag+"*")
      nSeries = len(preContrastNodeDict)
      if nSeries == 0:
        return studies
      preContrastNodeNames = sorted(preContrastNodeDict.keys(), reverse=True)
      
      # Get all volume nodes associated with this pre-contrast volume. 
      for name in preContrastNodeNames:
        preContrastNode = preContrastNodeDict[name]
        study = self.getStudyVolumeNodes(preContrastNode)
        if study:
          studies.append(study)
        
    # Some previous studies don't have registered breast masks.  Use the
    # current study's breast mask if missing.
    for iStudy in range(1, len(studies)):
      if not studies[iStudy].maskNode:
        studies[iStudy].maskNode = studies[0].maskNode
        
    return studies
  
    
  def getStudyVolumeNodes(self, preContrastNode):
    """Extracts names of all required volume nodes for each study:
      pre-contrast
      post-contrast (4 nodes)
      lesion map (optional)
      breast mask (optional)
      Returns True if one or more studies are found consisting of 1 pre-contrast image and 4 post-contrast images
    """
    # Get all corresponding post-contrast, lesion map and mask nodes.
    nodeName = preContrastNode.GetName()
    parts = nodeName.split("_")
    if params.pastImageTag in parts:
      # Past series.
      seriesIndex = params.pastImageFilenameParts.SeriesNumber
      patientId = parts[params.pastImageFilenameParts.PatientID]
      studyDate = parts[params.pastImageFilenameParts.SeriesDate]    
      accessionNo = parts[params.pastImageFilenameParts.AccessionNumber]
    else:
      # Current series.
      seriesIndex = params.currentImageFilenameParts.SeriesNumber
      patientId = parts[params.currentImageFilenameParts.PatientID]
      studyDate = parts[params.currentImageFilenameParts.SeriesDate]
      accessionNo = parts[params.currentImageFilenameParts.AccessionNumber]
    prefix = ('_').join(parts[0:seriesIndex])
      
    study = CADStudy(patientId, studyDate, accessionNo)
    study.preContrastNode = preContrastNode
      
    # Find post-contrast nodes.
    pattern = prefix+"_???_Ph?"+params.postContrastSeriesNameTag+"*"
    postNodeDict = slicer.util.getNodes(pattern=pattern)
    nPostNodes = len(postNodeDict)
    if nPostNodes != 4:
      logging.info(("{0}: {1} post contrast nodes found").format(nodeName, str(nPostNodes)))
    nodeNames = sorted(postNodeDict.keys())
    study.postContrastNodes = []
    for name in nodeNames:
      study.postContrastNodes.append(postNodeDict[name])
      
    # Find lesion map.
    lesionMapNode = self.getLesionMap(preContrastNode)
    lesionMapNodeName = ""
    if lesionMapNode:
      study.lesionMapNode = lesionMapNode
      
    # Find breast mask.
    maskNode = self.getBreastMask(preContrastNode)
    maskNodeName = ""
    if maskNode:
      study.maskNode = maskNode

    return study

  def getStudyVolumeNodesLongStudy(self, accession_no):
    """
    Extracts names of all required volume nodes for each study based on
    accession number:
      wo fat sat series
      subtraction series (4 nodes)
      lesion map (optional)
      breast mask (optional)
    Returns True if wo fat sat and 4 subtraction nodes are found.
    """
    # Get all volume nodes with accession number in name.
    nodeDict = slicer.util.getNodes(pattern="*" + accession_no + "*")
    nNodes = len(nodeDict)
    if nNodes < 4:
      logging.info(("{0}: {1} nodes found").format(accession_no, str(nNodes)))
      return False
    nodeName = nodeDict.keys()[0]
    parts = nodeName.split("_")
    patientId = parts[params.imageFilenameParts.PatientID]
    studyDate = parts[params.imageFilenameParts.SeriesDate]
    accessionNo = parts[params.imageFilenameParts.AccessionNumber]
    prefix = ('_').join(parts[0:params.imageFilenameParts.SeriesID])
    study = CADStudy(patientId, studyDate, accessionNo)

    # Find subtraction nodes.
    pattern = prefix + params.subtractionSeriesNameTag
    subtractionNodeDict = slicer.util.getNodes(pattern=pattern)
    nNodes = len(subtractionNodeDict)
    if nNodes != 4:
      logging.info(("{0}: {1} subtraction nodes found").format(accession_no, str(nNodes)))
    nodeNames = sorted(subtractionNodeDict.keys())
    study.diffNodes = []
    for name in nodeNames:
      study.diffNodes.append(subtractionNodeDict[name])
      
    # Find breast mask.
    pattern = prefix + params.maskSeriesNameTag
    maskNodeDict = slicer.util.getNodes(pattern=pattern)
    nNodes = len(maskNodeDict)
    if nNodes != 1:
      logging.info(("{0}: {1} mask nodes found").format(accession_no, str(nNodes)))
    study.maskNode = maskNodeDict.values()[0]

    return study


  def getSeriesIndex(self, volumeNodeName):
    # Returns the index of the volume series number in the volume node name
    parts = volumeNodeName.split("_")
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
    
  def calculateSubtractionImages(self, study):

    diffNodes = []
    
    # Get pre-contrast series.
    series0Name = study.preContrastNode.GetName()
    series0Parts = series0Name.split("_")
    series0SeriesIndex = self.getSeriesIndex(series0Name)
    series0SeriesNumber = series0Parts[series0SeriesIndex]
    series0Data = study.preContrastNode.GetImageData()

    # Subtract each post-contrast series from the pre-contrast series.
    for iSeries in range(len(study.postContrastNodes)):
      # Set up VTK subtraction filter.
      # Need to cast pre-contrast image because post-contrast images
      # are converted to doubles during motion correction.
      seriesName = study.postContrastNodes[iSeries].GetName()
      seriesParts = seriesName.split("_")
      seriesSeriesNumber = seriesParts[self.getSeriesIndex(seriesName)]
      seriesData = study.postContrastNodes[iSeries].GetImageData()
      series0Cast = vtk.vtkImageCast()
      series0Cast.SetInputData(series0Data)
      series0Cast.SetOutputScalarType(seriesData.GetScalarType())
      series0Cast.ClampOverflowOn()
      diffFilter = vtk.vtkImageMathematics()
      diffFilter.SetOperationToSubtract()
      diffFilter.SetInputConnection(1, series0Cast.GetOutputPort())  
      diffFilter.SetInputData(0, seriesData)
      diffFilter.Update()
      
      # Check to see if there's already an output node.
      newName = ("_").join(series0Parts[0:series0SeriesIndex])+"_"+seriesSeriesNumber+"-"+series0SeriesNumber
      inputNode = study.preContrastNode
      outputNode = slicer.util.getNode(newName)
      if not outputNode:
        outputNode = self.createOutputVolumeNode(newName, 'Grey')
      self.connectImageDataToOutputNode(inputNode, outputNode, diffFilter.GetOutput())
      
      # Change display properties (don't show negative values).
      scalarRange = diffFilter.GetOutput().GetScalarRange()
      displayNode = outputNode.GetDisplayNode()
      displayNode.SetAutoWindowLevel(0)
      #displayNode.SetThreshold(0, scalarRange[1])
      displayNode.SetWindowLevelMinMax(0, scalarRange[1])
          
      diffNodes.append(outputNode)
        
    study.diffNodes = diffNodes
    
    
  def maskFirstDiffNodeForVR(self, study):
    if study.maskNode and study.diffNodes[0]:
      study.maskedDiffNode = self.generateMaskedNode(study.diffNodes[0], study.maskNode)
         

  def hasLabels(self, labelNode):
    accum = vtk.vtkImageAccumulate()
    accum.SetInputConnection(labelNode.GetImageDataConnection())
    accum.Update()
    lo = max(int(accum.GetMin()[0]), 1)
    hi = int(accum.GetMax()[0])
    return hi != 0 and lo != 0


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
    seriesIndex = self.getSeriesIndex(lesionMapName)
    newName = ('_').join(parts[0:seriesIndex])+"_label"
    outputNode = slicer.util.getNode(newName)
    if not outputNode:
      outputNode = self.createOutputLabelNode(newName, 'GenericColors')    
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
      outputNode = self.createOutputLabelNode(newName)
    self.connectImageDataToOutputNode(labelNode, outputNode, outputImageData)
    
    castOut.SetOutput( None )
    
    return outputNode


  def createOutputLabelNode(self, name, colorTable='GenericColors'):
    # Create new nodes to hold, display and store the output image.
    outputNode = slicer.vtkMRMLLabelMapVolumeNode()
    outputNode.SetName(name)
    slicer.mrmlScene.AddNode(outputNode)
    self.initializeOutputLabelNodeDisplayAndStorage(outputNode, colorTable)    
    return outputNode
  
  
  def initializeOutputLabelNodeDisplayAndStorage(self, outputNode, colorTable='GenericColors'):
    # Set colour table and add to display.
    colorNode = slicer.util.getNode(colorTable)
    displayNode = slicer.vtkMRMLLabelMapVolumeDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    displayNode.SetAndObserveColorNodeID(colorNode.GetID())
    outputNode.SetAndObserveDisplayNodeID(displayNode.GetID())
    outputNode.CreateDefaultStorageNode()
    
  def initializeOutputLabelNode(self, labelNode, volumeNode):
    ras2ijk = vtk.vtkMatrix4x4()
    ijk2ras = vtk.vtkMatrix4x4()
    volumeNode.GetRASToIJKMatrix(ras2ijk)
    volumeNode.GetIJKToRASMatrix(ijk2ras)
    labelNode.SetRASToIJKMatrix(ras2ijk)
    labelNode.SetIJKToRASMatrix(ijk2ras)
    imageData = vtk.vtkImageData()
  
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
      outputNode = self.createOutputLabelNode(newName, 'GenericColors')    
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
      volumeRenderingDisplay.UnRegister(volumeRenderingLogic)
      volumeRenderingDisplay.RemoveAllViewNodeIDs()
      volumeRenderingDisplay.AddViewNodeID(slicer.util.getNode(widget).GetID())
    volumeRenderingDisplay.SetRaycastTechnique(2)
    volumeRenderingLogic.UpdateDisplayNodeFromVolumeNode(volumeRenderingDisplay, volumeNode)
    volumeNode.AddAndObserveDisplayNodeID(volumeRenderingDisplay.GetID())
    
    viewNode = slicer.util.getNode(widget)
    viewNode.SetBackgroundColor([0,0,0])
    viewNode.SetBackgroundColor2([0,0,0])
    viewNode.SetBoxVisible(0)
    viewNode.SetAxisLabelsVisible(0)
        
    viewNodeId = viewNode.GetID()
    cameraNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLCameraNode')
    for iCamera in range(slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLCameraNode')):
      cameraNode = cameraNodes.GetItemAsObject(iCamera)
      activeTag = cameraNode.GetActiveTag()
      if activeTag == viewNodeId:
        print(("rendering 3d view Widget: {0}, ViewNodeId: {1}, CameraNodeActiveTag: {2}").format(widget, viewNodeId, cameraNode.GetActiveTag))
        camera = cameraNode.GetCamera()
        camera.SetPosition(-600, 0, 0)
        camera.SetViewUp(0, 0, 1)
    cameraNodes.UnRegister(slicer.mrmlScene)


  def saveVTKAsMHA(self, volumeNode, filename):
    return slicer.util.saveNode(volumeNode, filename)
    

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
    testFolder = "D:\\Work\\BreastCAD\\TestData\\TestPipeline\\Lara\Invasive\\7184_7420191_6975224_6791512"
    for root, dirs, files in os.walk(testFolder):
      for file in files:
        if file.endswith(".mha"):
          slicer.util.loadVolume(os.path.join(root, file))
    self.delayDisplay('Finished with download and loading')

#     volumeNode = slicer.util.getNode(pattern="FA")
#     logic = TrackLesionsLogic()
#     self.assertTrue( logic.hasImageData(volumeNode) )
#     self.delayDisplay('Test passed!')
    
        
class CADStudy:
  def __init__(self, patientId, studyDate, accessionNo):
    self.patientId = patientId
    self.studyDate = studyDate
    self.accessionNo = accessionNo
    self.preContrastNode = None
    self.postContrastNodes = None
    self.lesionMapNode = None
    self.maskNode = None
    self.diffNodes = None
    self.labelNode = None
    self.maskedDiffNode = None
      

