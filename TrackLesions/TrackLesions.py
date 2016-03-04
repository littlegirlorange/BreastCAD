import os
import unittest
import vtk, qt, ctk, slicer, numpy
import vtkITK
from fnmatch import fnmatch
from slicer.ScriptedLoadableModule import *
import logging
import MyEditor
from MyEditorLib.EditUtil import EditUtil
import TrackLesionsParams_LongitudinalStudy as params
import LabelStatsLogic


customLayout = (
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
  
customLayoutId = 501

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
    
    layout = self.layout

    # Instantiate and connect widgets ...
    # Set custom 2 sag view layout.
    
    self.timePoints = ["Current", "Past1", "Past2"]
    self.sliceWidgets = ["Sub1", "Sub2", "Sub3", "Sub4"]
    self.viewLogicNames = ["ViewCurrent_VR", "ViewPast1_VR", "ViewPast2_VR"]
    self.currentLabelNode = None
    self.past1LabelNode = None
    self.past2LabelNode = None
    self.currentDiffNodes = None
    self.past1DiffNodes = None
    self.past2DiffNodes = None    
    self.studies = []

    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(customLayoutId, customLayout)
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(currentFourUpViewId, currentFourUpView)
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(past1FourUpViewId, past1FourUpView)
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(past2FourUpViewId, past2FourUpView)    
    layoutManager.setLayout(currentFourUpViewId)
    layoutManager.setLayout(past1FourUpViewId)
    layoutManager.setLayout(past2FourUpViewId)
    layoutManager.setLayout(customLayoutId)
    self.currentView = 'CompareView'

    self.resetUI()
           
    #
    # Patient area
    #
    patientCollapsibleButton = ctk.ctkCollapsibleButton()
    patientCollapsibleButton.text = "Patient"
    self.layout.addWidget(patientCollapsibleButton)
    patientFormLayout = qt.QFormLayout(patientCollapsibleButton)
    
    # Patient selector
    self.openPatientButton = qt.QPushButton("Select Patient Folder")
    patientFormLayout.addRow(self.openPatientButton)
    
    """
    # Patient info
    self.patientLayoutBox = qt.QGroupBox("Patient info")
    self.patientLayoutBox.setLayout(qt.QFormLayout())    
    self.patientIdLabel = qt.QLabel()
    self.patientIdLabel.setText("<Select patient>")
    #self.patientIdLabel.setAlignment(qt.Qt.AlignLeft | qt.Qt.AlignVCenter)
    self.patientLayoutBox.layout().addRow("Patient ID:", self.patientIdLabel)
    self.currentLabel = qt.QLabel()
    self.currentLabel.setText("")
    self.patientLayoutBox.layout().addRow("Current accession (date):", self.currentLabel)
    self.past1Label = qt.QLabel()
    self.past1Label.setText("")
    self.patientLayoutBox.layout().addRow("Past1 accession (date):", self.past1Label)
    self.past2Label = qt.QLabel()
    self.past2Label.setText("")
    self.patientLayoutBox.layout().addRow("Past2 accession (date):", self.past2Label)
    patientFormLayout.addRow(self.patientLayoutBox)
    """
    
    # Patient info
    self.patientLayoutBox = qt.QGroupBox("Patient info")
    self.patientLayoutBox.setLayout(qt.QFormLayout())    
    self.patientIdLabel = qt.QLabel()
    self.patientIdLabel.setText("<Select patient>")
    #self.patientIdLabel.setAlignment(qt.Qt.AlignLeft | qt.Qt.AlignVCenter)
    self.patientLayoutBox.layout().addRow("Patient ID:", self.patientIdLabel)    
    self.patientInfoView = qt.QTreeView()
    self.patientInfoView.sortingEnabled = False
    self.patientLayoutBox.layout().addRow(self.patientInfoView)
    self.setPatientInfo(reset=True)
#     self.patientInfoModel = qt.QStandardItemModel()
#     for iRow, timePoint in enumerate(self.timePoints):
#       item = qt.QStandardItem()
#       item.setText(timePoint)
#       self.patientInfoModel.setItem(iRow, 0, item)
#     self.patientInfoModel.setHeaderData(0, 1, "Study")
#     self.patientInfoModel.setHeaderData(1, 1, "Accession No.")
#     self.patientInfoModel.setHeaderData(2, 1, "Date")      
#     self.patientInfoView.setModel(self.patientInfoModel)
#     for i in range(3):
#       self.patientInfoView.resizeColumnToContents(i)   
    patientFormLayout.addRow(self.patientLayoutBox)
    
    #
    # View area
    #
    viewCollapsibleButton = ctk.ctkCollapsibleButton()
    viewCollapsibleButton.text = "View"
    self.layout.addWidget(viewCollapsibleButton)
    viewFormLayout = qt.QFormLayout(viewCollapsibleButton)
    
    # View group box
    self.viewRadioBox = qt.QGroupBox("View")
    self.viewRadioBox.setLayout(qt.QHBoxLayout())
    self.compareViewRadioButton = qt.QRadioButton()
    self.viewRadioBox.layout().addWidget(self.compareViewRadioButton)    
    self.compareViewRadioButton.text = "Compare"
    self.currentViewRadioButton = qt.QRadioButton()
    self.viewRadioBox.layout().addWidget(self.currentViewRadioButton)
    self.currentViewRadioButton.text = "Current"
    self.past1ViewRadioButton = qt.QRadioButton()
    self.viewRadioBox.layout().addWidget(self.past1ViewRadioButton)
    self.past1ViewRadioButton.text = "Past1"
    self.past2ViewRadioButton = qt.QRadioButton()
    self.viewRadioBox.layout().addWidget(self.past2ViewRadioButton)
    self.past2ViewRadioButton.text = "Past2"     
    self.compareViewRadioButton.checked = True
    viewFormLayout.addRow(self.viewRadioBox)
        
    # Slice selector
    self.inputSliceLabel = qt.QLabel("Jump to slice:")
    self.inputSliceLabel.setToolTip("Navigate sagittal views to the selected slice.")
    self.inputSliceSelector = qt.QSpinBox()
    self.inputSliceSelector.singleStep = (1)
    self.inputSliceSelector.minimum = (1)
    self.inputSliceSelector.maximum = (1)
    self.inputSliceSelector.value = (1)
    self.inputSliceSelector.setToolTip("Navigate sagittal views to the selected slice.")
    viewFormLayout.addRow(self.inputSliceLabel, self.inputSliceSelector)
    
    # Reset windowing button
    self.resetWindowingButton = qt.QPushButton("Reset Windowing")
    self.resetWindowingButton.toolTip = "Reset windowing of subtraction images to default values."
    self.resetWindowingButton.enabled = True
    viewFormLayout.addRow(self.resetWindowingButton)
         
    # Reset views button
    self.resetViewsButton = qt.QPushButton("Reset Data in Views")
    self.resetViewsButton.toolTip = "Load default volumes in views."
    self.resetViewsButton.enabled = True
    viewFormLayout.addRow(self.resetViewsButton)
             
    #
    # Contour area
    #
    contourCollapsibleButton = ctk.ctkCollapsibleButton()
    contourCollapsibleButton.text = "Contour"
    self.layout.addWidget(contourCollapsibleButton)
    contourFormLayout = qt.QFormLayout(contourCollapsibleButton)
    
    # Edit tools
    self.editBoxFrame = qt.QGroupBox("Contouring tools")
    self.editBoxFrame.objectName = 'EditBoxFrame'
    self.editBoxFrame.setLayout(qt.QVBoxLayout())
    contourFormLayout.addRow(self.editBoxFrame)
    self.editor = MyEditor.EditorWidget(self.editBoxFrame, False)
     
    #
    # Analysis Area
    #
    analysisCollapsibleButton = ctk.ctkCollapsibleButton()
    analysisCollapsibleButton.text = "Analysis"
    analysisCollapsibleButton.collapsed = True
    self.layout.addWidget(analysisCollapsibleButton)

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
    self.layout.addStretch(1)
    
    # connections
    self.openPatientButton.connect("clicked()", self.onOpenPatientButton)
    self.inputSliceSelector.connect("valueChanged(int)", self.onInputSliceSelect)
    self.compareViewRadioButton.connect('clicked()', self.onViewSelected)
    self.currentViewRadioButton.connect('clicked()', self.onViewSelected)
    self.past1ViewRadioButton.connect('clicked()', self.onViewSelected)
    self.past2ViewRadioButton.connect('clicked()', self.onViewSelected) 
    self.resetWindowingButton.connect('clicked()', self.onResetWindowing)  
    self.resetViewsButton.connect('clicked()', self.onResetViews)      
    self.findIslandsButton.connect('clicked(bool)', self.onConvertMapToLabelButton)
    self.saveIslandsButton.connect('toggled(bool)', self.onSaveIslandsButtonToggled)
    self.queryIslandsButton.connect('toggled(bool)', self.onQueryIslandsButtonToggled)    
    self.Button.connect('clicked(bool)', self.onButton)
      
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
    
  
  def resetUI(self):
    # Link views.
    layoutManager = slicer.app.layoutManager()    
    sliceLogics = layoutManager.mrmlSliceLogics()
    for i in xrange(sliceLogics.GetNumberOfItems()):
      sliceLogic = sliceLogics.GetItemAsObject(i)
      sliceCompositeNode = sliceLogic.GetSliceCompositeNode()
      sliceCompositeNode.SetLinkedControl(1)
      sliceLogic.FitSliceToAll()

    # Turn on navigation.
    crosshairNode = slicer.util.getNode("vtkMRMLCrosshairNode*")
    if crosshairNode:
      crosshairNode.SetCrosshairMode(5)
      crosshairNode.SetNavigation(1)
      

  def resetParameterNode(self):
    # Reset current patient.
    self.setPatientInfo(reset=True)
#     self.patientIdLabel.setText("<Select patient>")
#     self.currentLabel.setText("")
#     self.past1Label.setText("")
#     self.past2Label.setText("")

    # Set view to current.
    self.compareViewRadioButton.checked = True
    self.setSliceSelector(minVal=1, maxVal=1, value=1)    
    
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
    logic = TrackLesionsLogic()
    layoutManager = slicer.app.layoutManager()
    if newView == 'CompareView':
      layoutManager.setLayout(customLayoutId)
    elif newView == 'CurrentView':
      layoutManager.setLayout(currentFourUpViewId)
    elif newView == 'Past1View':
      layoutManager.setLayout(past1FourUpViewId)
    else:
      layoutManager.setLayout(past2FourUpViewId)
    self.currentView = newView
    #self.setLayoutNodes()
    

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
      

  def onOpenPatientButton(self):
    # Prompt to close current scene if data is currently loaded.
    if len(self.studies) > 0:
      qResult = qt.QMessageBox.question(slicer.util.mainWindow(), "Close patient", 
                                        "Close the current patient? \nUnsaved changes will be lost.", 
                                        qt.QMessageBox.Ok, qt.QMessageBox.Cancel)
      if qResult == qt.QMessageBox.Cancel:
        return
      else:
        slicer.mrmlScene.Clear(0)
        self.resetUI()
        self.resetParameterNode(
                                )
    # Pop up open data dialog.
    slicer.util.openAddDataDialog()
    
    # Sort input data into separate studies.
    self.logic = TrackLesionsLogic()
    self.studies = self.logic.sortVolumeNodes()
    if len(self.studies) == 0:
      qt.QMessageBox.warning(slicer.util.mainWindow(), "Load patient",
                             "Incomplete patient folder. \nUnable to process.")
      # TODO: Disable processing buttons
      return
    
    # Set current patient in parameter node.
#     self.patientIdLabel.setText(self.studies[0].patientId)
#     self.currentLabel.setText(self.studies[0].accessionNo +
#                               " ("+self.studies[0].studyDate + ")")
#     self.past1Label.setText(self.studies[1].accessionNo +
#                             " (" + self.studies[1].studyDate + ")")
#     self.past2Label.setText(self.studies[2].accessionNo +
#                             " (" + self.studies[2].studyDate + ")")
    self.setPatientInfo()
    
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
      labelNodeName = volumeNode.GetName() + "_label"
      labelNode = slicer.modules.volumes.logic().CreateAndAddLabelVolume(slicer.mrmlScene, volumeNode, labelNodeName)
      colorNode = slicer.util.getNode('GenericColors')
      labelNode.GetDisplayNode().SetAndObserveColorNodeID(colorNode.GetID())
      study.labelNode = labelNode
      
      # Attach to slice and volume displays.
      self.attachStudyToSliceWidgets(study, self.timePoints[iStudy])
      self.logic.maskFirstDiffNodeForVR(study)
      self.attachStudyToVolumeWidget(study, self.timePoints[iStudy])
    
    self.resetUI()
      
    # Set slice selector.
    dims = self.studies[0].diffNodes[0].GetImageData().GetDimensions()
    maxSliceNo = dims[2]+1
    curSliceNo = round(maxSliceNo/2)
    self.setSliceSelector(minVal=1, maxVal=maxSliceNo, value=curSliceNo)
    
    # Enable lesion contouring.
    EditUtil.setActiveVolumes(self.studies[0].diffNodes[0], self.studies[0].labelNode)
    EditUtil.setLabel(1)
    self.editor.setMergeNode(self.studies[0].labelNode)


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


  def onInputSliceSelect(self):
    slice = self.inputSliceSelector.value
    self.setSlice(slice)
    
    
  def onResetWindowing(self):
    for study in self.studies:
      for volumeNode in study.diffNodes:
        self.setWindowing(volumeNode, 0)
#           imageData = vtk.vtkImageData()
#           imageData = volumeNode.GetImageData()      
#           scalarRange = imageData.GetScalarRange()
#           displayNode = volumeNode.GetDisplayNode()
#           displayNode.SetAutoWindowLevel(0)
#           displayNode.SetWindowLevelMinMax(0, scalarRange[1])
        
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
      self.logic = TrackLesionsLogic()
      self.studies = self.logic.sortVolumeNodes()
      if len(self.studies) == 0:
        qt.QMessageBox.warning(slicer.util.mainWindow(), "Reset views",
                               "Incomplete patient folder. \nPlease try reloading data.")
        # TODO: Disable processing buttons
        return
      
      # Set current patient in parameter node.
#       self.patientIdLabel.setText(self.studies[0].patientId)
#       self.currentLabel.setText(self.studies[0].accessionNo +
#                                 " ("+self.studies[0].studyDate + ")")
#       self.past1Label.setText(self.studies[1].accessionNo +
#                               " (" + self.studies[1].studyDate + ")")
#       self.past2Label.setText(self.studies[2].accessionNo +
#                               " (" + self.studies[2].studyDate + ")")

    self.setPatientInfo()
      
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
        study.labelNode = labelNode
      
      # Attach to slice and volume displays.
      self.attachStudyToSliceWidgets(study, self.timePoints[iStudy])
      if not study.maskedDiffNode:
        self.logic.maskFirstDiffNodeForVR(study)
      self.attachStudyToVolumeWidget(study, self.timePoints[iStudy])
    
    self.resetUI()
      
    # Set slice selector.
    dims = self.studies[0].diffNodes[0].GetImageData().GetDimensions()
    maxSliceNo = dims[2]+1
    curSliceNo = round(maxSliceNo/2)
    self.setSliceSelector(minVal=1, maxVal=maxSliceNo, value=curSliceNo)
    
    # Enable lesion contouring.
    EditUtil.setActiveVolumes(self.studies[0].diffNodes[0], self.studies[0].labelNode)
    EditUtil.setLabel(1)
    self.editor.setMergeNode(self.studies[0].labelNode)    
    
        
  #
  # Contouring methods
  #
  def editLabelNode(self, labelNode, volumeNode):
    EditUtil.setActiveVolumes(volumeNode, labelNode)
    EditUtil.setLabel(1)
    EditUtil.setCurrentEffect("DrawEffect")    
    
  def onSelect(self):
    pass

    
  def attachStudyToSliceWidgets(self, study, timePoint):
    if timePoint in self.timePoints:
      for iDiffNode in range(len(study.diffNodes)):
        widget = timePoint + "_" + self.sliceWidgets[iDiffNode]
        self.updateSliceWidget(widget, "Background", study.diffNodes[iDiffNode].GetID(), True)
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


  def sortVolumeNodes(self):
    """Sorts the volume nodes in the scene into study objects.
    Each study contains multiple series.
    """
    
    studies = []
    if LONG_STUDY_FLAG:
      # Get all w/o fat sat nodes (should be one per study).
      woFSNodeDict = slicer.util.getNodes(pattern="*"+params.woFatSatSeriesNameTag)
      nSeries = len(woFSNodeDict)
      if nSeries == 0:
        return studies
      woFSNodeNames = sorted(woFSNodeDict.keys(), reverse=True)
      
      # Get all volume nodes associated with this pre-contrast volume. 
      for name in woFSNodeNames:
        parts = name.split("_")
        accession_no = parts[params.imageFilenameParts.AccessionNumber]
        study = self.getStudyVolumeNodesLongStudy(accession_no)
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


  def createNumpyArray (self, node):
    # Generate Numpy Array from vtkMRMLScalarVolumeNode
    imageData = vtk.vtkImageData()
    imageData = node.GetImageData()
    shapeData = list(imageData.GetDimensions())
    return (vtk.util.numpy_support.vtk_to_numpy(imageData.GetPointData().GetScalars()).reshape(shapeData))

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
      outputNode = self.createOutputLabelNode(newName, 'GenericColors')    
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
      

