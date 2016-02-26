import qt
import slicer
import vtk

import SimpleITK as sitk
import sitkUtils

from fnmatch import fnmatch

from EditUtil import EditUtil
from ColorBox import ColorBox


#=============================================================================
#
# LabelSummaryWidget
#
#=============================================================================
class LabelSummaryWidget(qt.QWidget):
  #---------------------------------------------------------------------------
  def __init__(self, *args, **kwargs):
    qt.QWidget.__init__(self, *args, **kwargs)
    
    self.create()

    # mrml volume node instances
    self._master = None
    self._merge = None
    
    self.structureLabelNames = []

    # pseudo signals
    # - python callable that gets True or False
    self.mergeValidCommand = None

    # instance of a ColorBox
    self.colorBox = None

    # qt model/view classes to track per-structure volumes
    self.structures = qt.QStandardItemModel()

    # mrml node for invoking command line modules
    self.CLINode = None

    # slicer helper class
    self.volumesLogic = slicer.modules.volumes.logic()

    # buttons pressed
#     self.addStructureButton.connect("clicked()", self.addStructure)
    self.deleteStructuresButton.connect("clicked()", self.deleteStructures)
    self.deleteSelectedStructureButton.connect("clicked()", self.deleteSelectedStructure)


  #---------------------------------------------------------------------------
  @property
  def master(self):
    return self._master

  #---------------------------------------------------------------------------
  @master.setter
  def master(self, node):
    self._master = node

  #---------------------------------------------------------------------------
  @property
  def merge(self):
    return self._merge

  #---------------------------------------------------------------------------
  @merge.setter
  def merge(self, node):
    print "LabelSummaryWidget: setting merge node"
    if self._merge:
      self._merge.RemoveObserver(self._mergeNodeTag)
    self._merge = node
    self._merge.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onMergeModified)
    self.updateStructures()
    
  #---------------------------------------------------------------------------
  def setMerge(self, node):
    print "LabelSummaryWidget: setting merge node"
    if self._merge:
      self._merge.RemoveObserver(self._mergeNodeTag)
    self._merge = node
    self._merge.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onMergeModified)
    self.updateStructures()

  #---------------------------------------------------------------------------
  def cleanup(self):
    if self.colorBox:
      self.colorBox.cleanup()
    if self._merge:
      self._merge.RemoveObserver(self._mergeNodeTag)
      
  #---------------------------------------------------------------------------
  def onMergeModified(self, caller=None, event=None):
    self.updateStructures()

  #---------------------------------------------------------------------------
  def create(self):
    layout = qt.QVBoxLayout(self)

    # buttons frame

    self.structureButtonsFrame = qt.QFrame()
    self.structureButtonsFrame.objectName = 'ButtonsFrame'
    self.structureButtonsFrame.setLayout(qt.QHBoxLayout())
    layout.addWidget(self.structureButtonsFrame)

#     # add button
# 
#     self.addStructureButton = qt.QPushButton("Add Structure")
#     self.addStructureButton.objectName = 'AddStructureButton'
#     self.addStructureButton.setToolTip( "Add a label volume for a structure to edit" )
#     self.structureButtonsFrame.layout().addWidget(self.addStructureButton)

    # structures view

    self.structuresView = qt.QTableView()
    self.structuresView.objectName = 'StructuresView'
    self.structuresView.sortingEnabled = True
    self.structuresView.minimumHeight = 200
    layout.addWidget(self.structuresView)

    # all buttons frame

    self.allButtonsFrame = qt.QFrame()
    self.allButtonsFrame.objectName = 'AllButtonsFrameButton'
    self.allButtonsFrame.setLayout(qt.QHBoxLayout())
    layout.addWidget(self.allButtonsFrame)

    # delete all structures button

    self.deleteStructuresButton = qt.QPushButton("Delete All")
    self.deleteStructuresButton.objectName = 'DeleteStructureButton'
    self.deleteStructuresButton.setToolTip( "Delete all the structure volumes from the scene.\n\nNote: to delete individual structure volumes, use the Data Module." )
    self.allButtonsFrame.layout().addWidget(self.deleteStructuresButton)

    # delete selected structures button

    self.deleteSelectedStructureButton = qt.QPushButton("Delete Selected")
    self.deleteSelectedStructureButton.objectName = 'DeleteSelectedStructureButton'
    self.deleteSelectedStructureButton.setToolTip( "Delete the selected structure volume from the scene." )
    self.allButtonsFrame.layout().addWidget(self.deleteSelectedStructureButton)

    # options frame

    self.optionsFrame = qt.QFrame()
    self.optionsFrame.objectName = 'OptionsFrame'
    self.optionsFrame.setLayout(qt.QHBoxLayout())
    layout.addWidget(self.optionsFrame)

  #---------------------------------------------------------------------------
#   def promptStructure(self):
#     """ask user which label to create"""
# 
#     merge = self.merge
#     if not merge:
#       return
#     colorNode = merge.GetDisplayNode().GetColorNode()
# 
#     if colorNode == "":
#       slicer.util.errorDisplay( "No color node selected" )
#       return
# 
#     if not self.colorBox == "":
#       self.colorBox = ColorBox(colorNode=colorNode)
#       self.colorBox.selectCommand = self.addStructure
#     else:
#       self.colorBox.colorNode = colorNode
#       self.colorBox.parent.populate()
#       self.colorBox.parent.show()
#       self.colorBox.parent.raise_()

  #---------------------------------------------------------------------------
#   def addStructure(self, label=None, options=""):
#     """create the segmentation helper box"""
#     
#     merge = self.merge
# 
#     if not label:
#       # if no label given, prompt the user.  The selectCommand of the colorBox will
#       # then re-invoke this method with the label value set and we will continue
#       label = self.promptStructure()
#       return
# 
#     colorNode = self.merge.GetDisplayNode().GetColorNode()
#     labelName = colorNode.GetColorName(label)
# 
#     if labelName not in self.structureLabelNames:
#       self.updateStructures()
#       
#     self.edit(label)
# 
#     if options.find("noEdit") < 0:
#       self.selectStructure(self.structures.rowCount()-1)

  #---------------------------------------------------------------------------
  def selectStructure(self, idx):
    """programmatically select the specified structure"""
    selectionModel = self.structuresView.selectionModel()
    selectionModel.select(qt.QItemSelection(self.structures.index(idx,0),
                                            self.structures.index(idx,5)),
                                            selectionModel.ClearAndSelect)
    selectionModel.setCurrentIndex(self.structures.index(idx,0), selectionModel.NoUpdate)
    self.structuresView.activated(self.structures.index(idx,0))

  #---------------------------------------------------------------------------
  def deleteSelectedStructure(self, confirm=True):
    """delete the currently selected structure"""

    selectionModel = self.structuresView.selectionModel()
    selected = selectionModel.currentIndex().row()

    if selected >= 0:

      label = self.structures.item(selected,2).text()

      if confirm:
        if not self.confirmDialog( "Delete \'%s\' volume?" % label ):
          return

      slicer.mrmlScene.SaveStateForUndo()

      self.updateStructures()
      if self.structures.rowCount() > 0:
        self.selectStructure((selected-1) if (selected-1 >= 0) else 0)
      else:
        self.edit(0)

  #---------------------------------------------------------------------------
  def deleteStructures(self, confirm=True):
    """delete all the structures"""

    #
    # iterate through structures and delete them
    #
    rows = self.structures.rowCount()

    if confirm:
      if not self.confirmDialog( "Delete %d structure volume(s)?" % rows ):
        return

    slicer.mrmlScene.SaveStateForUndo()

    for labelName in self.structureLabelNames:
      self.deleteLabelFromLabelNode(labelName)
    self.updateStructures()
    self.edit(0)

  #---------------------------------------------------------------------------
  def deleteLabelFromLabelNode(self, labelName):
    """Remove label from label node"""

    self.statusText( "Deleting label from label node..." )
    merge = self.merge
    if not merge:
      return
    colorNode = merge.GetDisplayNode().GetColorNode()
    labelIndex = colorNode.GetColorIndexByName(labelName)

    accum = vtk.vtkImageAccumulate()
    if vtk.VTK_MAJOR_VERSION <= 5:
      accum.SetInput(merge.GetImageData())
    else:
      accum.SetInputConnection(merge.GetImageDataConnection())
    accum.Update()
    lo = int(accum.GetMin()[0])
    hi = int(accum.GetMax()[0])
    if labelIndex not in xrange(lo, hi+1):
      return

    # TODO: pending resolution of bug 1822, run the thresholding
    # in single threaded mode to avoid data corruption observed on mac release
    # builds
    thresholder = vtk.vtkImageThreshold()
    thresholder.SetNumberOfThreads(1)
    thresholder.SetInputConnection( merge.GetImageDataConnection() )
    thresholder.SetInValue(0)
    thresholder.ReplaceInOn()
    thresholder.ReplaceOutOff()
    thresholder.ThresholdBetween(labelIndex, labelIndex)
    thresholder.SetOutputScalarType(merge.GetImageData().GetScalarType())
    thresholder.Update()
    
    merge.GetImageData().DeepCopy(thresholder.GetOutput())
    EditUtil.markVolumeNodeAsModified(merge)

    self.statusText( "Finished deleting label." )

  #---------------------------------------------------------------------------
  def edit(self, label):
    """select the picked label for editing"""

    merge = self.merge
    if not merge:
      return
    
    EditUtil.setLabel(label)
    
  #---------------------------------------------------------------------------    
  def buildStructureList(self):
    """List all labels and their first slice locations
    """
    structureData = []
    
    merge = self.merge
    if not merge:
      return structureData
 
    colorNode = merge.GetDisplayNode().GetColorNode()
    lut = colorNode.GetLookupTable()    
    
    # Get label value range.
    accum = vtk.vtkImageAccumulate()
    accum.SetInputConnection(merge.GetImageDataConnection())
    accum.Update()
    lo = max(int(accum.GetMin()[0]), 1)
    hi = int(accum.GetMax()[0])
    
    # Make sure label exists in merge node.
    thresholder = vtk.vtkImageThreshold()
    thresholder.SetNumberOfThreads(1)
    labelShapeStatisticsFilter = sitk.LabelShapeStatisticsImageFilter()
    labelImage = sitkUtils.PullFromSlicer(merge.GetName())
    outputImage = labelShapeStatisticsFilter.Execute(labelImage, 0, False, False) 
        
    for i in xrange(lo, hi+1):
      thresholder.SetInputConnection(merge.GetImageDataConnection())
      thresholder.SetInValue(i)
      thresholder.SetOutValue(0)
      thresholder.ReplaceInOn()
      thresholder.ReplaceOutOn()
      thresholder.ThresholdBetween(i,i)
      thresholder.SetOutputScalarType(merge.GetImageData().GetScalarType())
      thresholder.Update()
      if thresholder.GetOutput().GetScalarRange() != (0.0, 0.0):
        # The label exists. Get the label index, color name and first slice.
        labelRow = []        
        labelRow.append(str(i)) # label index
        labelRow.append(colorNode.GetColorName(i)) # label name
        dims = labelShapeStatisticsFilter.GetBoundingBox(i)  # [x0, y0, z0, dx, dy, dz]             
        labelRow.append(str(dims[2])) # first slice
        structureData.append(labelRow)
        
    return structureData

  #---------------------------------------------------------------------------
  def updateStructures(self, caller=None, event=None):
    """re-build the Structures frame
    - optional caller and event ignored (for use as vtk observer callback)
    """

    if slicer.mrmlScene.IsBatchProcessing():
      return

    # reset to a fresh model
    self.structures = qt.QStandardItemModel()
    self.structuresView.setModel(self.structures)

    # if no merge volume exists, disable everything - else enable
    merge = self.merge

#     self.addStructureButton.setDisabled(not merge)
    self.deleteStructuresButton.setDisabled(not merge)
    self.deleteSelectedStructureButton.setDisabled(not merge)
    if self.mergeValidCommand:
      # will be passed current
      self.mergeValidCommand(merge)

    if not merge:
      return

    # Get list of labels in this labelNode.
    structureData = self.buildStructureList()
    if len(structureData) == 0:
      return

    colorNode = merge.GetDisplayNode().GetColorNode()
    lut = colorNode.GetLookupTable()
    mergeName = merge.GetName()
    
    for i, structure in enumerate(structureData):
      # structure = [labelIndex, labelName, firstSlice]
      labelIndex = colorNode.GetColorIndexByName(structure[0])
      labelColor = lut.GetTableValue(labelIndex)[0:3]
      color = qt.QColor()
      color.setRgb(labelColor[0]*255,labelColor[1]*255,labelColor[2]*255)
      
      # label index
      item = qt.QStandardItem()
      item.setEditable(False)
      item.setText(labelIndex)
      self.structures.setItem(i,0, item)

      # label color
      item = qt.QStandardItem()
      item.setEditable(False)
      item.setData(color, 1)
      self.structures.setItem(i, 1,  item)

      # structure name
      item = qt.QStandardItem()
      item.setEditable(False)
      item.setText(structure[1])
      self.structures.setItem(i, 2, item)

      # label node name
      item = qt.QStandardItem()
      item.setEditable(False)
      item.setText(mergeName)
      self.structures.setItem(i, 3, item)
      
      # slice
      item = qt.QStandardItem()
      item.setEditable(False)
      item.setText(structure[2])
      self.structures.setItem(i, 4, item)

    for i in range(5):
      self.structuresView.resizeColumnToContents(i)

    self.structures.setHeaderData(0,1,"Number")
    self.structures.setHeaderData(1,1,"Color")
    self.structures.setHeaderData(2,1,"Name")
    self.structures.setHeaderData(3,1,"Label Volume")
    self.structures.setHeaderData(4,1,"Slice")
    self.structuresView.setModel(self.structures)
    self.structuresView.connect("activated(QModelIndex)", self.onStructureClicked)
    self.structuresView.setProperty('SH_ItemView_ActivateItemOnSingleClick', 1)

    self.structureLabelNames = []
    rows = self.structures.rowCount()
    for row in xrange(rows):
      self.structureLabelNames.append(self.structures.item(row,2).text())

  #---------------------------------------------------------------------------
  def onStructureClicked(self, modelIndex):
    if modelIndex.row() != -1:
      self.edit(int(self.structures.item(modelIndex.row(),0).text()))
      self.jumpSlices = True
      if self.jumpSlices:
        slice = int(self.structures.item(modelIndex.row(), 4).text())
        self.setSlice(slice)

  #---------------------------------------------------------------------------
  def setSlice(self, iSlice):
    """ Set the current slice (z index) for all sagittal slice nodes.
    Assumes all volume nodes are the same dimension.
    """
    orientations = {'Sagittal':0, 'Coronal':1, 'Axial':2}
    rasIndex = orientations["Sagittal"]

    nSliceNodes = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceNode')
    layoutManager = slicer.app.layoutManager()
    for iSliceNode in xrange(nSliceNodes):
      sliceNode = slicer.mrmlScene.GetNthNodeByClass(iSliceNode, 'vtkMRMLSliceNode')
      sliceWidgetName = sliceNode.GetLayoutName()
      sliceWidgetOrientation = sliceNode.GetOrientationString() 
      if fnmatch(sliceWidgetOrientation, "Sagittal"):
        ijkToRas = vtk.vtkMatrix4x4()
        sliceLogic = slicer.app.layoutManager().sliceWidget(sliceWidgetName).sliceLogic()
        volNode = sliceLogic.GetLabelLayer().GetVolumeNode()
        # volDims = volNode.GetImageData().GetDimensions()
        if volNode:
          volNode.GetIJKToRASMatrix(ijkToRas)
          posIjk = [0, 0, 0, 1]
          posIjk[2-rasIndex] = iSlice
          posRas = ijkToRas.MultiplyPoint(posIjk)
          sliceLogic.SetSliceOffset(posRas[rasIndex])

  #---------------------------------------------------------------------------
  def confirmDialog(self, message):
    result = qt.QMessageBox.question(slicer.util.mainWindow(),
                    'Editor', message,
                    qt.QMessageBox.Ok, qt.QMessageBox.Cancel)
    return result == qt.QMessageBox.Ok

  #---------------------------------------------------------------------------
  def statusText(self, text):
    slicer.util.showStatusMessage( text,1000 )
    
  #---------------------------------------------------------------------------


    
