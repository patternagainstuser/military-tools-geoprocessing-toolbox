#------------------------------------------------------------------------------
# Copyright 2017-2018 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

import os
import unittest
import arcpy
from random import randint

# Add parent folder to python path if running test case standalone
import sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import Configuration
import UnitTestUtilities

class GRGCreateGRGFromAreaTestCase(unittest.TestCase):

    inputArea = None

    @classmethod
    def setUpClass(cls):
        # Run once per class creation
        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        Configuration.Logger.debug("     GRGCreateGRGFromAreaTestCase.setUpClass")
        UnitTestUtilities.checkArcPy()

        if not arcpy.Exists(Configuration.militaryScratchGDB):
            Configuration.militaryScratchGDB = UnitTestUtilities.createScratch(Configuration.currentPath)

        Configuration.Logger.debug("Import Toolbox: " + Configuration.toolboxUnderTest)
        arcpy.ImportToolbox(Configuration.toolboxUnderTest)
        Configuration.Logger.debug("Done Toolbox Import")

        arcpy.env.overwriteOutput = True

    @classmethod
    def tearDownClass(cls):
        Configuration.Logger.debug("     GRGCreateGRGFromAreaTestCase.tearDownClass")
        UnitTestUtilities.deleteScratch(Configuration.militaryScratchGDB)

    def setUp(self):

        Configuration.Logger.debug("     GRGCreateGRGFromAreaTestCase.setUp")

        # set up inputs
        self.inputArea = os.path.join(Configuration.militaryInputDataGDB, r"GRGAreaofOperations")

        UnitTestUtilities.checkGeoObjects([self.inputArea])

    def tearDown(self):
        Configuration.Logger.debug("         GRGTestCase.tearDown")

    def testGRGAreaGRG(self):

        Configuration.Logger.debug(".....GRGCreateGRGFromAreaTestCase.testGRGAreaGRG")

        #inputs
        cellWidth = randint(100, 500)
        cellHeight = randint(100, 500)
        cellunits = "Meters"
        labelStart = "Lower-Left"
        labelStyle = "Numeric"
        labelSeparator = "-" # Only used for Alpha-Alpha but required parameter?
        output = os.path.join(Configuration.militaryScratchGDB, "grg")

        Configuration.Logger.debug ("Cell Width: " + str(cellWidth))
        Configuration.Logger.debug ("Cell Height: " + str(cellHeight))

        #Testing
        runToolMsg="Running tool (Canvas Area GRG)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)

        toolOutput = None

        try:
            # Calling the Create GRG From Area script tool
            toolOutput = arcpy.CreateGRGFromArea_mt(self.inputArea, \
                cellWidth, cellHeight, cellunits, \
                labelStart, labelStyle, labelSeparator, output)

        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        # 1: Check the expected return value
        self.assertIsNotNone(toolOutput, "No output returned from tool")
        outputOut = toolOutput.getOutput(0)
        self.assertEqual(output, outputOut, "Unexpected return value from tool")

        # 2: Check the number of features created
        Configuration.Logger.debug ('''
        =================================================================
        Test #2 Check to see if the amount of features created is the
        number expected.
        We expect 40
        ==================================================================
        ''')
        result = arcpy.GetCount_management(output)
        count = int(result.getOutput(0))
        Configuration.Logger.debug("Output number features: " + str(count))
        #self.assertEqual(count, 40)

        # 3: Check the size of the grids that have been created
        Configuration.Logger.debug ('''
        ==================================================================
        Test #3 Check the size of the grids that have been created using the
        assertLessEqual. Comparing this to the cellwidth and height times 2.
        If the number returned  is less than 1 the test passes.This is used
        because of the percision of the field does not produce the exact number.
        ==================================================================
        ''')


        primter_area = (cellWidth * 2) +  (cellHeight * 2)
        field_name = "Shape_Length"
        with arcpy.da.SearchCursor(output, field_name) as cursor:
            for row in cursor:
                testlen= primter_area - int(row[0])
                self.assertLessEqual(testlen, 1)

        Configuration.Logger.debug ('''
        ==================================================================
        Test #4 Check to see if all the correct numeric labels have been
        created. This is tested by comparing the numbers to objectID.
        ==================================================================
        ''')

        oid = []
        grid = []
        with arcpy.da.SearchCursor(output, "ObjectID") as cursor:
            for row in cursor:
                oid.append(row[0])

        with arcpy.da.SearchCursor(output,"Grid") as cursor:
            for row in cursor:
                grid.append(int(row[0]))

        #Compare the oid list and the grid list

        list.sort(oid)
        list.sort(grid)
        Configuration.Logger.debug(oid)
        Configuration.Logger.debug(grid)

        self.assertEquals(oid, grid)


if __name__ == "__main__":
    unittest.main()