cmake_minimum_required(VERSION 2.8.9)

project(BreastCAD)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/BreastCAD")
set(EXTENSION_CATEGORY "Custom")
set(EXTENSION_CONTRIBUTORS "Maggie Kusano (Martel Group)")
set(EXTENSION_DESCRIPTION "UI for research use of BreastCAD pipeline components")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/BreastCAD.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/BreastCAD/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(TrackLesions)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
