import os
import slicer
import qt, ctk, vtk
from slicer.util import VTKObservationMixin
import MyEditorLib
from MyEditorLib.EditUtil import EditUtil
from MyEditorLib.LabelSummaryWidget import LabelSummaryWidget



#
# Editor
#

class Editor:
  def __init__(self, parent):
    import string
    parent.title = "Editor"
    parent.categories = ["", "Segmentation"]
    parent.contributors = ["Steve Pieper (Isomics)"]
    parent.helpText = string.Template("""
The Editor allows label maps to be created and edited. The active label map will be modified by the Editor.

See <a href=\"$a/Documentation/$b.$c/Modules/Editor\">the documentation</a> for more information.

The Master Volume refers to the background grayscale volume to be edited (used, for example, when thresholding).  The Merge Volume refers to a volume that contains several different label values corresponding to different structures.\n\nBasic usage: selecting the Master and Merge Volume give access to the editor tools.  Each tool has a help icon to bring up a dialog with additional information.  Hover your mouse pointer over buttons and options to view Balloon Help (tool tips).  Use these to define the Label Map.\n\nAdvanced usage: open the Per-Structure Volumes tab to create independent Label Maps for each color you wish to edit.  Since many editor tools (such as threshold) will operate on the entire volume, you can use the Per-Structure Volumes feature to isolate these operations on a structure-by-structure basis.  Use the Split Merge Volume button to create a set of volumes with independent labels.  Use the Add Structure button to add a new volume.  Delete Structures will remove all the independent structure volumes.  Merge All will assemble the current structures into the Merge Volume.  Merge And Build will invoke the Model Maker module on the Merge Volume.
    """).substitute({ 'a':parent.slicerWikiUrl, 'b':slicer.app.majorVersion, 'c':slicer.app.minorVersion })
    parent.acknowledgementText = """
This work is supported by NA-MIC, NAC, BIRN, NCIGT, and the Slicer Community. See <a>http://www.slicer.org</a> for details.  Module implemented by Steve Pieper.
This work is partially supported by PAR-07-249: R01CA131718 NA-MIC Virtual Colonoscopy (See <a href=http://www.slicer.org>http://www.na-mic.org/Wiki/index.php/NA-MIC_NCBC_Collaboration:NA-MIC_virtual_colonoscopy</a>).
    """
    self.parent = parent

    if slicer.mrmlScene.GetTagByClassName( "vtkMRMLScriptedModuleNode" ) != 'ScriptedModule':
      node = vtkMRMLScriptedModuleNode()
      slicer.mrmlScene.RegisterNodeClass(node)
      node.Delete()

    parent.icon = qt.QIcon("%s/ToolbarEditorToolbox.png" % EditorLib.ICON_DIR)


#
# qSlicerPythonModuleExampleWidget
#

class EditorWidget(VTKObservationMixin):

  # Lower priorities:
  #->> additional option for list of allowed labels - texts

  def __init__(self, parent=None, showVolumesFrame=True):
    VTKObservationMixin.__init__(self)
    self.shortcuts = []
    self.toolsBox = None

    # set attributes from ctor parameters
    self.showVolumesFrame = showVolumesFrame

    self.editUtil = EditUtil() # Kept for backward compatibility

    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
      self.layout = self.parent.layout()
      self.setup()
      self.parent.show()
    else:
      # Part of another module.
      self.parent = parent
      self.layout = parent.layout()
      self.setup()
      self.enterViaAnotherModule()

  def turnOffLightboxes(self):
    """Since the editor effects can't be used in lightbox mode,
    be sure to turn these off and warn the user about it"""
    warned = False
    layoutManager = slicer.app.layoutManager()
    if layoutManager != None:
      sliceLogics = layoutManager.mrmlSliceLogics()
      for i in xrange(sliceLogics.GetNumberOfItems()):
        sliceLogic = sliceLogics.GetItemAsObject(i)
        if sliceLogic:
          sliceNode = sliceLogic.GetSliceNode()
          if sliceNode.GetLayoutGridRows() != 1 or sliceNode.GetLayoutGridColumns() != 1:
            if not warned:
              qt.QMessageBox.warning(slicer.util.mainWindow(), 'Editor', 'The Editor Module is not compatible with slice viewers in light box mode.\nViews are being reset.')
              warned = True
            sliceNode.SetLayoutGrid(1,1)

  def installShortcutKeys(self):
    """Turn on editor-wide shortcuts.  These are active independent
    of the currently selected effect."""
    Key_Escape = 0x01000000 # not in PythonQt
    Key_Space = 0x20 # not in PythonQt
    self.shortcuts = []
    keysAndCallbacks = (
        ('e', EditUtil.toggleLabel),
        ('z', self.toolsBox.undoRedo.undo),
        ('y', self.toolsBox.undoRedo.redo),
        ('h', EditUtil.toggleCrosshair),
        ('o', EditUtil.toggleLabelOutline),
        ('t', EditUtil.toggleForegroundBackground),
        (Key_Escape, self.toolsBox.defaultEffect),
        ('p', lambda : self.toolsBox.selectEffect('PaintEffect')),
        ('d', lambda : self.toolsBox.selectEffect('DrawEffect')),
        ('r', lambda : self.toolsBox.selectEffect('RectangleEffect')),
        ('c', self.toolsColor.showColorBox),
        (Key_Space, self.toolsBox.toggleFloatingMode),
        )
    for key,callback in keysAndCallbacks:
      shortcut = qt.QShortcut(slicer.util.mainWindow())
      shortcut.setKey( qt.QKeySequence(key) )
      shortcut.connect( 'activated()', callback )
      self.shortcuts.append(shortcut)

  def removeShortcutKeys(self):
    for shortcut in self.shortcuts:
      shortcut.disconnect('activated()')
      shortcut.setParent(None)
    self.shortcuts = []

  def enter(self):
    """
    When entering the module, check that the lightbox modes are off
    and that we have the volumes loaded
    """
    self.turnOffLightboxes()
    self.installShortcutKeys()

    # get the master and merge nodes from the composite node associated
    # with the red slice, but only if showing volumes and we don't already
    # have an active set of volumes that we are using
    if self.showVolumesFrame:
      if not self.helper.master or not self.helper.merge:
        # get the slice composite node for the Red slice view (we'll assume it exists
        # since we are in the editor) to get the current background and label
        # - set the foreground layer as the active ID
        # in the selection node for later calls to PropagateVolumeSelection
        compositeNode = EditUtil.getCompositeNode()
        selectionNode = slicer.app.applicationLogic().GetSelectionNode()
        selectionNode.SetReferenceSecondaryVolumeID( compositeNode.GetForegroundVolumeID() )
        bgID = lbID = ""
        if compositeNode.GetBackgroundVolumeID():
          bgID = compositeNode.GetBackgroundVolumeID()
        if compositeNode.GetLabelVolumeID():
          lbID = compositeNode.GetLabelVolumeID()
        masterNode = slicer.mrmlScene.GetNodeByID( bgID )
        mergeNode = slicer.mrmlScene.GetNodeByID( lbID )
        self.setMasterNode(masterNode)
        self.setMergeNode(mergeNode)
    # if not showing volumes, the caller is responsible for setting the master and
    # merge nodes, most likely according to a widget within the caller

    # Observe the parameter node in order to make changes to
    # button states as needed
    self.parameterNode = EditUtil.getParameterNode()
    self.addObserver(self.parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromMRML)

    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.resetInterface)

    if self.helper:
      self.helper.onEnter()

    if self.toolsColor:
      self.toolsColor.updateGUIFromMRML(self.parameterNode, vtk.vtkCommand.ModifiedEvent)

  def enterViaAnotherModule(self):
    """
    Widget is created by another module, not the main Slicer app. Volumes
    are loaded by the other module, so skip the lightbox and input node
    stuff.
    """
    self.installShortcutKeys()

    # get the master and merge nodes from the composite node associated
    # with the red slice, but only if showing volumes and we don't already
    # have an active set of volumes that we are using
    if self.showVolumesFrame:
      if not self.helper.master or not self.helper.merge:
        # get the slice composite node for the Red slice view (we'll assume it exists
        # since we are in the editor) to get the current background and label
        # - set the foreground layer as the active ID
        # in the selection node for later calls to PropagateVolumeSelection
        compositeNode = EditUtil.getCompositeNode()
        selectionNode = slicer.app.applicationLogic().GetSelectionNode()
        selectionNode.SetReferenceSecondaryVolumeID( compositeNode.GetForegroundVolumeID() )
        bgID = lbID = ""
        if compositeNode.GetBackgroundVolumeID():
          bgID = compositeNode.GetBackgroundVolumeID()
        if compositeNode.GetLabelVolumeID():
          lbID = compositeNode.GetLabelVolumeID()
        masterNode = slicer.mrmlScene.GetNodeByID( bgID )
        mergeNode = slicer.mrmlScene.GetNodeByID( lbID )
        self.setMasterNode(masterNode)
        self.setMergeNode(mergeNode)
    # if not showing volumes, the caller is responsible for setting the master and
    # merge nodes, most likely according to a widget within the caller

    # Observe the parameter node in order to make changes to
    # button states as needed
    self.parameterNode = EditUtil.getParameterNode()
    self.addObserver(self.parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromMRML)

    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.resetInterface)

    if self.helper:
      self.helper.onEnter()

    if self.toolsColor:
      self.toolsColor.updateGUIFromMRML(self.parameterNode, vtk.vtkCommand.ModifiedEvent)
      
  def exit(self):
    self.removeObservers()
    self.resetInterface()
    self.removeShortcutKeys()

  def resetInterface(self, caller=None, event=None):
    if self.helper:
      self.helper.onExit()
    if self.toolsBox:
      self.toolsBox.defaultEffect()
      self.toolsBox.cancelFloatingMode()

  def updateGUIFromMRML(self, caller, event):
    if self.toolsBox:
      self.toolsBox.updateUndoRedoButtons()

  # sets the node for the volume to be segmented
  def setMasterNode(self, newMasterNode):
    if newMasterNode and newMasterNode.GetClassName() == "vtkMRMLScalarVolumeNode":
      if self.helper:
        self.helper.setMasterVolume(newMasterNode)

  # sets the node for the label map
  def setMergeNode(self, newMergeNode):
    if newMergeNode:
      if self.helper:
        self.helper.setMergeVolume(newMergeNode)
      if self.labelSummaryWidget:
        self.labelSummaryWidget.setMerge(newMergeNode)
        
  # sets the label map nodes
  def setLabelNodes(self, labelNodes):
    if self.labelSummaryWidget:
      self.labelSummaryWidget.addLabelNodes(labelNodes)

  # sets up the widget
  def setup(self):


    #
    # Editor Volumes
    #
    # only if showing volumes
    if self.showVolumesFrame:
      self.volumes = ctk.ctkCollapsibleButton(self.parent)
      self.volumes.objectName = 'VolumeCollapsibleButton'
      self.volumes.setLayout(qt.QVBoxLayout())
      self.volumes.setText("Create and Select Label Maps")
      self.layout.addWidget(self.volumes)
    else:
      self.volumes = None

    # create the helper box - note this isn't a Qt widget
    #  but a helper class that creates Qt widgets in the given parent
    if self.showVolumesFrame:
      self.helper = MyEditorLib.HelperBox(self.volumes)
    else:
      self.helper = None

    #
    # Tool Frame
    #

    # (we already have self.parent for the parent widget, and self.layout for the layout)
    # create the frames for the EditColor, toolsOptionsFrame and EditBox

    #
    # Label section
    #
    # Label color selector 
    colorNode = slicer.util.getNode('GenericColors')
    labelOptionsFrame = qt.QGroupBox("Labels", self.parent)
    labelOptionsFrame.setLayout(qt.QVBoxLayout())
    self.toolsColor = MyEditorLib.EditColor(labelOptionsFrame, colorNode=colorNode)
    self.parent.layout().addWidget(labelOptionsFrame)
    
    # Label opacity slicer
    defaultOpacity = 0.5
    EditUtil.setLabelOpacity(defaultOpacity)
    opacityFrame = qt.QFrame(labelOptionsFrame)
    opacityFrame.setLayout(qt.QHBoxLayout())
    labelOptionsFrame.layout().addWidget(opacityFrame)
    label = qt.QLabel("Opacity: ", opacityFrame)
    opacityFrame.layout().addWidget(label)
    self.opacityValue = qt.QLabel(str(defaultOpacity), opacityFrame)
    opacityFrame.layout().addWidget(self.opacityValue)
    self.opacitySlider = ctk.ctkDoubleSlider()
    self.opacitySlider.minimum = 0.0
    self.opacitySlider.maximum = 1.0
    self.opacitySlider.orientation = 1
    self.opacitySlider.singleStep = 0.05
    self.opacitySlider.setValue(defaultOpacity)
    self.opacitySlider.connect('valueChanged(double)', self.onOpacityChanged)
    opacityFrame.layout().addWidget(self.opacitySlider)
    
    # Label outline button
    self.labelOutlineCheckBox = qt.QCheckBox(opacityFrame)
    self.labelOutlineCheckBox.setText("Outlines")
    self.labelOutlineCheckBox.checked = False
    self.labelOutlineCheckBox.setToolTip("Show label regions as outlines.")
    self.labelOutlineCheckBox.connect('stateChanged(int)', self.onLabelOutlineChecked)
    opacityFrame.layout().addWidget(self.labelOutlineCheckBox)

    # create frame for effect options
    self.createEffectOptionsFrame()

    # create and add frame for EditBox
    self.createEditBox()

    # put the tool options below the color selector
    self.parent.layout().addWidget(self.editBoxFrame)
    self.parent.layout().addWidget(self.effectOptionsFrame)

    # Create and add widget for listing labels.
    self.createLabelSummaryWidget()
    self.parent.layout().addWidget(self.labelSummaryWidget)
    
    if self.helper:
      # add a callback to collapse/open the frame based on the validity of the label volume
      self.helper.mergeValidCommand = self.updateLabelFrame
      # add a callback to reset the tool when a new volume is selected
      self.helper.selectCommand = self.toolsBox.defaultEffect

    # Add spacer to layout
    self.layout.addStretch(1)

  # creates the frame for the effect options
  # assumes self.effectsToolsFrame and its layout has already been created
  def createEffectOptionsFrame(self):
    self.effectOptionsFrame = qt.QGroupBox("Tools", self.parent)
    self.effectOptionsFrame.objectName = 'EffectOptionsFrame'
    self.effectOptionsFrame.setLayout(qt.QVBoxLayout())

  # Creates the EditBox and its frame
  # Assumes effectOptionsFrame has already been created
  def createEditBox(self):
    if not self.effectOptionsFrame:
      self.effectOptionsFrame = self.createEffectOptionsFrame()
    #self.editBoxFrame = qt.QFrame(self.parent)
    self.editBoxFrame = qt.QGroupBox("Toolbox", self.parent)
    self.editBoxFrame.objectName = 'EditBoxFrame'
    self.editBoxFrame.setLayout(qt.QVBoxLayout())
    self.toolsBox = MyEditorLib.EditBox(self.editBoxFrame, optionsFrame=self.effectOptionsFrame)

  # Creates the label summary widget.
  def createLabelSummaryWidget(self):
    self.labelSummaryFrame = qt.QGroupBox("Current contours")
    self.labelSummaryFrame.objectName = "LabelSummaryFrame"
    self.labelSummaryFrame.setLayout(qt.QVBoxLayout())
    self.labelSummaryWidget = LabelSummaryWidget(self.labelSummaryFrame)

  def updateLabelFrame(self, mergeVolume):
    pass
    #self.editLabelMapsFrame.collapsed = not mergeVolume
      
  def onLabelOutlineChecked(self):
    EditUtil.setLabelOutline(self.labelOutlineCheckBox.isChecked())
    
  def onOpacityChanged(self, opacity):
    self.opacityValue.text = "{0:.1f}".format(opacity)
    EditUtil.setLabelOpacity(opacity)
  

  #->> TODO: check to make sure editor module smoothly handles interactive changes to the master and merge nodes
