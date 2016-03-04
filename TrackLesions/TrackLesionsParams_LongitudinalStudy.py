from TrackLesionsUtils import enum


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


imageFilenameParts = enum('PatientID',
                          'SeriesDate',
                          'AccessionNumber',
                          'SeriesID')





