def enum(*sequential, **named):
    '''
    http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    To call:
    >>> Numbers = enum('ZERO', 'ONE', 'TWO')
    >>> Numbers.ZERO
    0
    >>> Numbers.ONE
    1
    '''
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


motionCorrectionStepTag = "mc"
breastSegmentationStepTag = "mask"
registrationStepTag = "reg"
annStepTag = "LesionProbMap"
thresholdStepTag = "thresh"
vesselRemovalStepTag = "vr"
lesionMapTag = annStepTag + "_" + thresholdStepTag + "_" + vesselRemovalStepTag
pastImageTag = registrationStepTag

preContrastSeriesNameTag = "_Sag.VIBRANT.MPH"
postContrastSeriesNameTag = "Sag.VIBRANT.MPH"
breastSegmentationSeriesNameTag = "_?_Sag.VIBRANT.wo.FS"
lesionMapSeriesNameTag = "_?_Sag.VIBRANT.wo.FS"


currentImageFilenameParts = enum('PatientID',
                                 'DICOMNumber',
                                 'SeriesDate',
                                 'AccessionNumber',
                                 'SeriesNumber',
                                 'SeriesName',
                                 motionCorrectionStepTag)

currentLesionMapFilenameParts = enum('PatientID',
                                     'DICOMNumber',
                                     'SeriesDate',
                                     'AccessionNumber',
                                     'SeriesNumber',
                                     'SeriesName',
                                     annStepTag,
                                     thresholdStepTag,
                                     vesselRemovalStepTag)

pastImageFilenameParts = enum('FixedPatientID',
                              'FixedDICOMNumber',
                              'FixedSeriesDate',
                              'FixedAccessionNumber',
                              'FixedSeriesNumber',
                              'FixedSeriesName',
                              'PatientID',
                              'DICOMNumber',
                              'SeriesDate',
                              'AccessionNumber',
                              'SeriesNumber',
                              'SeriesName',
                              motionCorrectionStepTag,
                              registrationStepTag)

pastLesionMapFilenameParts = enum('FixedPatientID',
                                  'FixedDICOMNumber',
                                  'FixedSeriesDate',
                                  'FixedAccessionNumber',
                                  'FixedSeriesNumber',
                                  'FixedSeriesName',
                                  'PatientID',
                                  'DICOMNumber',
                                  'SeriesDate',
                                  'AccessionNumber',
                                  'SeriesNumber',
                                  'SeriesName',
                                  annStepTag,
                                  registrationStepTag,
                                  thresholdStepTag,
                                  vesselRemovalStepTag)




