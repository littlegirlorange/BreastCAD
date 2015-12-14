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

currentImageFilenameParts = enum('PatientID',
                                 'DICOMNumber',
                                 'SeriesDate',
                                 'AccessionNumber',
                                 'SeriesNumber',
                                 'SeriesName',
                                 'mc')

currentLesionMapFilenameParts = enum('PatientID',
                                     'DICOMNumber',
                                     'SeriesDate',
                                     'AccessionNumber',
                                     'SeriesNumber',
                                     'SeriesName',
                                     'LesionProbMap',
                                     'thresh',
                                     'vr')

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
                              'mc',
                              'warped',
                              'elastix')

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
                                  'LesionProbMap',
                                  'warped',
                                  'elastix',
                                  'thresh',
                                  'vr')

lesionMapTag = "vr"
motionCorrectionTag = "mc"
pastImageTag = "elastix"


