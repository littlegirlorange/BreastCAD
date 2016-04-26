from TrackLesionsUtils import enum

# [Path to longitudinal studies]
defaultPath = "M:\\maggieData\\Lara\\ToContour\\Invasive"

# [Path to radiology reports]
reportPath = "M:\\maggieData\\Lara\\Reports"

# [Unique tags used to differentiate image types based on file name]
motionCorrectionStepTag = "mc"
breastSegmentationStepTag = "mask"
registrationStepTag = "reg"
annStepTag = "LesionProbMap"
thresholdStepTag = "thresh"
vesselRemovalStepTag = "vr"
lesionMapTag = annStepTag + "_" + thresholdStepTag + "_" + vesselRemovalStepTag
pastImageTag = registrationStepTag
woFatSatSeriesNameTag = "_wo.FS"
subtractionSeriesNameTag = "_???-???"
maskSeriesNameTag = "_mask"
preContrastSeriesNameTag = "_Sag.VIBRANT.MPH"
postContrastSeriesNameTag = "Sag.VIBRANT.MPH"
breastSegmentationSeriesNameTag = "_?_Sag.VIBRANT.wo.FS"
lesionMapSeriesNameTag = "_?_Sag.VIBRANT.wo.FS"

# [Positions of patient and series identification tags within a file name]
#   Assumes tags are separated by underscores ("_").
#   Example: for files named <PatientID>_<SeriesDate>_<AccessionNumber>_<SeriesID>.mha
#   (e.g., 190_20100423_5251288_801-800.mha),
#   imageFilenameParts = enum('PatientID',
#                             'SeriesDate',
#                             'AccessionNumber',
#                             'SeriesID')
imageFilenameParts = enum('PatientID',
                          'SeriesDate',
                          'AccessionNumber',
                          'SeriesID')




