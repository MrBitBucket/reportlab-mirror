#!/usr/bin/env python

"Make the ReportLab vector logo from canned data."

import pprint, os, string

from reportlab.lib.units import cm
from reportlab.lib.colors import *
from reportlab.graphics.shapes import *
from reportlab.graphics.widgetbase import *
from reportlab.graphics import renderPDF


_LOGODATA = {'CreateDocumentVersion': '1',
 'CurrentPage': '0',
 'DocumentHTML': {'AfterContent': '',
                  'AlinkColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAAEAAYY=',
                  'BGColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgEBhg==',
                  'BeforeContent': '',
                  'BodyString': '',
                  'CenterInTable': 'YES',
                  'Coalesce': '3',
                  'ColorFromView': 'YES',
                  'Description': '',
                  'DestinationDirectory': '',
                  'HTMLClass': 'DocumentHTML',
                  'HandCraftedBody': 'NO',
                  'Head': '',
                  'HomePageName': 'index',
                  'ImagePath': '',
                  'Keywords': '',
                  'LinkColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAAABAYY=',
                  'NavBarAbove': 'YES',
                  'NavBarBelow': 'NO',
                  'NavBarIconStyle': '1',
                  'OutputFileType': '0',
                  'OutputLine': 'NO',
                  'PageTitlePrefix': '',
                  'TableOfContentsType': '0',
                  'TextColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                  'ThumbnailSize': '160',
                  'UseBiggerFonts': 'NO',
                  'UseDocumentHTML': 'YES',
                  'UseGraphicalNavBar': 'YES',
                  'VlinkColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='},
 'DocumentWindowFrame': '{{314, 60}, {610, 676}}',
 'GridColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZoM/KqqrAYY=',
 'GridSpacing': '8.000000',
 'GridVisible': 'NO',
 'PageList': [{'CurentLayer': '0',
               'GraphicsList': [{'Bounds': '{{80.5625, 71.1875}, {430, 269}}',
                                 'Class': 'Group',
                                 'Effects': [],
                                 'GroupGraphics': [{'Bounds': '{{111, 0}, {198, 269}}',
                                                    'Class': 'Group',
                                                    'Effects': [],
                                                    'GroupGraphics': [{'BezierDict': {'Operations': ['0',
                                                                                                     '1',
                                                                                                     '1',
                                                                                                     '1'],
                                                                                      'Points': ['{13.875, 0}',
                                                                                                 '{49.5, 35.75}',
                                                                                                 '{35.875, 49.75}',
                                                                                                 '{0, 13.75}']},
                                                                       'Bounds': '{{147.875, 0.75}, {49.5, 49.75}}',
                                                                       'CTMKey': 'YES',
                                                                       'Class': 'MultiLine',
                                                                       'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                                    'EffectClass': 'FillEffect'},
                                                                                   {'Antialias': 'YES',
                                                                                    'ClosePath': 'YES',
                                                                                    'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                                               'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                                    'EffectClass': 'StrokeEffect',
                                                                                    'LineWidth': '0.00'}],
                                                                       'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                                       'Layer': '0',
                                                                       'UniqueID': '1092'},
                                                                      {'Bounds': '{{139.375, 39.625}, {50.491, 19.08}}',
                                                                       'Class': 'Rectangle',
                                                                       'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                                    'EffectClass': 'FillEffect'},
                                                                                   {'Antialias': 'YES',
                                                                                    'ClosePath': 'YES',
                                                                                    'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                                               'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                                    'EffectClass': 'StrokeEffect',
                                                                                    'LineWidth': '0.00'}],
                                                                       'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                                       'Layer': '0',
                                                                       'UniqueID': '1087'},
                                                                      {'Bounds': '{{139.375, 8.29166}, {19.08, 50.4583}}',
                                                                       'Class': 'Rectangle',
                                                                       'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                                    'EffectClass': 'FillEffect'},
                                                                                   {'Antialias': 'YES',
                                                                                    'ClosePath': 'YES',
                                                                                    'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                                               'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                                    'EffectClass': 'StrokeEffect',
                                                                                    'LineWidth': '0.00'}],
                                                                       'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                                       'Layer': '0',
                                                                       'UniqueID': '1062'},
                                                                      {'Bounds': '{{178, 36.5}, {19.33, 58}}',
                                                                       'Class': 'Rectangle',
                                                                       'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                                    'EffectClass': 'FillEffect'},
                                                                                   {'Antialias': 'YES',
                                                                                    'ClosePath': 'YES',
                                                                                    'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                                               'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                                    'EffectClass': 'StrokeEffect',
                                                                                    'LineWidth': '0.00'}],
                                                                       'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                                       'Layer': '0',
                                                                       'UniqueID': '1056'},
                                                                      {'Bounds': '{{0.447998, 0.625}, {19.08, 113.375}}',
                                                                       'Class': 'Rectangle',
                                                                       'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                                    'EffectClass': 'FillEffect'},
                                                                                   {'Antialias': 'YES',
                                                                                    'ClosePath': 'YES',
                                                                                    'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                                               'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                                    'EffectClass': 'StrokeEffect',
                                                                                    'LineWidth': '0.00'}],
                                                                       'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                                       'Layer': '0',
                                                                       'UniqueID': '1053'},
                                                                      {'Bounds': '{{178.444, 167.624}, {18.9945, 101.238}}',
                                                                       'Class': 'Rectangle',
                                                                       'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                                    'EffectClass': 'FillEffect'},
                                                                                   {'Antialias': 'YES',
                                                                                    'ClosePath': 'YES',
                                                                                    'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                                               'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                                    'EffectClass': 'StrokeEffect',
                                                                                    'LineWidth': '0.00'}],
                                                                       'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                                       'Layer': '0',
                                                                       'UniqueID': '1050'},
                                                                      {'Bounds': '{{0.5, 249.768}, {196.875, 19.08}}',
                                                                       'Class': 'Rectangle',
                                                                       'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                                    'EffectClass': 'FillEffect'},
                                                                                   {'Antialias': 'YES',
                                                                                    'ClosePath': 'YES',
                                                                                    'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                                               'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                                    'EffectClass': 'StrokeEffect',
                                                                                    'LineWidth': '0.00'}],
                                                                       'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                                       'Layer': '0',
                                                                       'UniqueID': '1047'},
                                                                      {'Bounds': '{{0.447998, 0.695976}, {161.302, 19.08}}',
                                                                       'Class': 'Rectangle',
                                                                       'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                                    'EffectClass': 'FillEffect'},
                                                                                   {'Antialias': 'YES',
                                                                                    'ClosePath': 'YES',
                                                                                    'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                                               'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                                    'EffectClass': 'StrokeEffect',
                                                                                    'LineWidth': '0.00'}],
                                                                       'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                                       'Layer': '0',
                                                                       'UniqueID': '1022'},
                                                                      {'Bounds': '{{0.447998, 187.75}, {19.08, 81.074}}',
                                                                       'Class': 'Rectangle',
                                                                       'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                                    'EffectClass': 'FillEffect'},
                                                                                   {'Antialias': 'YES',
                                                                                    'ClosePath': 'YES',
                                                                                    'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                                               'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                                    'EffectClass': 'StrokeEffect',
                                                                                    'LineWidth': '0.00'}],
                                                                       'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                                       'Layer': '0',
                                                                       'UniqueID': '1020'}],
                                                    'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                    'Layer': '0',
                                                    'OriginalSize': '{198, 269}',
                                                    'UniqueID': '1094'},
                                                   {'BezierDict': {'Operations': ['0',
                                                                                  '1',
                                                                                  '1',
                                                                                  '2',
                                                                                  '2',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '1',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '1',
                                                                                  '3',
                                                                                  '0',
                                                                                  '1',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '1',
                                                                                  '1',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '2',
                                                                                  '1',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '3',
                                                                                  '0',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '3',
                                                                                  '0',
                                                                                  '1',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '3',
                                                                                  '0',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '1',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '2',
                                                                                  '3',
                                                                                  '0'],
                                                                   'Points': ['{51.4688, 71.2547}',
                                                                              '{30.3281, 71.2547}',
                                                                              '{20.6719, 48.0516}',
                                                                              '{20.5781, 47.6578}',
                                                                              '{20.4141, 47.1375}',
                                                                              '{20.1797, 46.4906}',
                                                                              '{19.9453, 45.8438}',
                                                                              '{19.6562, 45.0703}',
                                                                              '{19.3125, 44.1703}',
                                                                              '{19.4531, 48.4734}',
                                                                              '{19.4531, 71.2547}',
                                                                              '{0, 71.2547}',
                                                                              '{0, 6.11719}',
                                                                              '{20.0156, 6.11719}',
                                                                              '{28.8282, 6.11719}',
                                                                              '{35.4219, 7.67811}',
                                                                              '{39.7969, 10.8}',
                                                                              '{45.3594, 14.7938}',
                                                                              '{48.1406, 20.475}',
                                                                              '{48.1406, 27.8438}',
                                                                              '{48.1406, 35.7188}',
                                                                              '{44.4063, 41.1609}',
                                                                              '{36.9375, 44.1703}',
                                                                              '{19.5469, 36.2812}',
                                                                              '{20.8594, 36.2812}',
                                                                              '{23.1094, 36.2812}',
                                                                              '{24.9844, 35.5078}',
                                                                              '{26.4844, 33.9609}',
                                                                              '{27.9844, 32.4141}',
                                                                              '{28.7344, 30.4453}',
                                                                              '{28.7344, 28.0547}',
                                                                              '{28.7344, 23.189}',
                                                                              '{25.9063, 20.7563}',
                                                                              '{20.25, 20.7563}',
                                                                              '{19.5469, 20.7563}',
                                                                              '{83.1562, 55.8141}',
                                                                              '{101.531, 56.1516}',
                                                                              '{100.219, 61.4672}',
                                                                              '{97.6641, 65.468}',
                                                                              '{93.8672, 68.1539}',
                                                                              '{90.0703, 70.8399}',
                                                                              '{85.1094, 72.1828}',
                                                                              '{78.9844, 72.1828}',
                                                                              '{71.7343, 72.1828}',
                                                                              '{66.0469, 70.1578}',
                                                                              '{61.9219, 66.1078}',
                                                                              '{57.8281, 62.0015}',
                                                                              '{55.7812, 56.3907}',
                                                                              '{55.7812, 49.275}',
                                                                              '{55.7812, 42.0468}',
                                                                              '{57.9844, 36.1547}',
                                                                              '{62.3906, 31.5984}',
                                                                              '{66.7969, 27.014}',
                                                                              '{72.4843, 24.7219}',
                                                                              '{79.4531, 24.7219}',
                                                                              '{86.3907, 24.7219}',
                                                                              '{91.9219, 26.9297}',
                                                                              '{96.0469, 31.3453}',
                                                                              '{100.172, 35.7891}',
                                                                              '{102.234, 41.6812}',
                                                                              '{102.234, 49.0219}',
                                                                              '{102.141, 52.0172}',
                                                                              '{74.5781, 52.0172}',
                                                                              '{74.7969, 56.686}',
                                                                              '{76.2656, 59.0203}',
                                                                              '{78.9844, 59.0203}',
                                                                              '{81.1094, 59.0203}',
                                                                              '{82.5, 57.9516}',
                                                                              '{83.1562, 55.8141}',
                                                                              '{83.5781, 42.9047}',
                                                                              '{83.5781, 42.0609}',
                                                                              '{83.4688, 41.2875}',
                                                                              '{83.25, 40.5844}',
                                                                              '{83.0312, 39.8812}',
                                                                              '{82.7266, 39.2766}',
                                                                              '{82.3359, 38.7703}',
                                                                              '{81.9453, 38.2641}',
                                                                              '{81.4844, 37.8633}',
                                                                              '{80.9531, 37.568}',
                                                                              '{80.4219, 37.2727}',
                                                                              '{79.8438, 37.125}',
                                                                              '{79.2188, 37.125}',
                                                                              '{77.9062, 37.125}',
                                                                              '{76.8438, 37.6664}',
                                                                              '{76.0312, 38.7492}',
                                                                              '{75.2187, 39.832}',
                                                                              '{74.8125, 41.2172}',
                                                                              '{74.8125, 42.9047}',
                                                                              '{128.297, 91.5891}',
                                                                              '{109.5, 91.5891}',
                                                                              '{109.5, 25.65}',
                                                                              '{128.297, 25.65}',
                                                                              '{127.875, 32.1047}',
                                                                              '{128.656, 30.7547}',
                                                                              '{129.453, 29.6086}',
                                                                              '{130.266, 28.6664}',
                                                                              '{131.078, 27.7242}',
                                                                              '{131.953, 26.9578}',
                                                                              '{132.891, 26.3672}',
                                                                              '{133.828, 25.7766}',
                                                                              '{134.836, 25.3477}',
                                                                              '{135.914, 25.0805}',
                                                                              '{136.992, 24.8133}',
                                                                              '{138.188, 24.6797}',
                                                                              '{139.5, 24.6797}',
                                                                              '{144.375, 24.6797}',
                                                                              '{148.344, 26.8734}',
                                                                              '{151.406, 31.2609}',
                                                                              '{154.438, 35.5922}',
                                                                              '{155.953, 41.3437}',
                                                                              '{155.953, 48.5156}',
                                                                              '{155.953, 55.8}',
                                                                              '{154.5, 61.5656}',
                                                                              '{151.594, 65.8125}',
                                                                              '{148.75, 70.0594}',
                                                                              '{144.828, 72.1828}',
                                                                              '{139.828, 72.1828}',
                                                                              '{135.266, 72.1828}',
                                                                              '{131.281, 69.8063}',
                                                                              '{127.875, 65.0531}',
                                                                              '{128.031, 66.4875}',
                                                                              '{128.125, 67.725}',
                                                                              '{128.156, 68.7656}',
                                                                              '{128.25, 69.8344}',
                                                                              '{128.297, 71.114}',
                                                                              '{128.297, 72.6047}',
                                                                              '{136.5, 48.0094}',
                                                                              '{136.5, 45.0281}',
                                                                              '{136.117, 42.7149}',
                                                                              '{135.352, 41.0695}',
                                                                              '{134.586, 39.4242}',
                                                                              '{133.5, 38.6016}',
                                                                              '{132.094, 38.6016}',
                                                                              '{129.187, 38.6016}',
                                                                              '{127.734, 41.7937}',
                                                                              '{127.734, 48.1781}',
                                                                              '{127.734, 54.7032}',
                                                                              '{129.141, 57.9656}',
                                                                              '{131.953, 57.9656}',
                                                                              '{133.359, 57.9656}',
                                                                              '{134.469, 57.0938}',
                                                                              '{135.281, 55.35}',
                                                                              '{136.094, 53.6062}',
                                                                              '{136.5, 51.1594}',
                                                                              '{136.5, 48.0094}',
                                                                              '{208.875, 49.1484}',
                                                                              '{208.875, 56.1797}',
                                                                              '{206.719, 61.7765}',
                                                                              '{202.406, 65.9391}',
                                                                              '{198.094, 70.1016}',
                                                                              '{192.313, 72.1828}',
                                                                              '{185.062, 72.1828}',
                                                                              '{177.937, 72.1828}',
                                                                              '{172.266, 70.0594}',
                                                                              '{168.047, 65.8125}',
                                                                              '{163.859, 61.5375}',
                                                                              '{161.766, 55.8}',
                                                                              '{161.766, 48.6}',
                                                                              '{161.766, 41.4}',
                                                                              '{163.906, 35.6203}',
                                                                              '{168.188, 31.2609}',
                                                                              '{172.438, 26.8734}',
                                                                              '{178.078, 24.6797}',
                                                                              '{185.109, 24.6797}',
                                                                              '{192.516, 24.6797}',
                                                                              '{198.328, 26.8594}',
                                                                              '{202.547, 31.2188}',
                                                                              '{206.766, 35.5781}',
                                                                              '{208.875, 41.5546}',
                                                                              '{208.875, 49.1484}',
                                                                              '{190.641, 48.6}',
                                                                              '{190.641, 46.9125}',
                                                                              '{190.516, 45.3867}',
                                                                              '{190.266, 44.0227}',
                                                                              '{190.016, 42.6586}',
                                                                              '{189.656, 41.4914}',
                                                                              '{189.188, 40.5211}',
                                                                              '{188.719, 39.5508}',
                                                                              '{188.156, 38.7984}',
                                                                              '{187.5, 38.2641}',
                                                                              '{186.844, 37.7297}',
                                                                              '{186.109, 37.4625}',
                                                                              '{185.297, 37.4625}',
                                                                              '{183.703, 37.4625}',
                                                                              '{182.422, 38.475}',
                                                                              '{181.453, 40.5}',
                                                                              '{180.484, 42.2719}',
                                                                              '{180, 44.9297}',
                                                                              '{180, 48.4734}',
                                                                              '{180, 51.961}',
                                                                              '{180.484, 54.6187}',
                                                                              '{181.453, 56.4469}',
                                                                              '{182.422, 58.4719}',
                                                                              '{183.719, 59.4844}',
                                                                              '{185.344, 59.4844}',
                                                                              '{186.875, 59.4844}',
                                                                              '{188.141, 58.4859}',
                                                                              '{189.141, 56.4891}',
                                                                              '{190.141, 54.2672}',
                                                                              '{190.641, 51.6375}',
                                                                              '{190.641, 48.6}',
                                                                              '{234.938, 71.2547}',
                                                                              '{216.141, 71.2547}',
                                                                              '{216.141, 25.65}',
                                                                              '{234.938, 25.65}',
                                                                              '{233.953, 34.5516}',
                                                                              '{236.797, 27.8859}',
                                                                              '{241.5, 24.5531}',
                                                                              '{248.062, 24.5531}',
                                                                              '{248.062, 43.5375}',
                                                                              '{246, 42.525}',
                                                                              '{244.25, 42.0187}',
                                                                              '{242.812, 42.0187}',
                                                                              '{240.281, 42.0187}',
                                                                              '{238.336, 42.8414}',
                                                                              '{236.977, 44.4867}',
                                                                              '{235.617, 46.132}',
                                                                              '{234.938, 48.5297}',
                                                                              '{234.938, 51.6797}',
                                                                              '{274.875, 71.2547}',
                                                                              '{256.031, 71.2547}',
                                                                              '{256.031, 39.2766}',
                                                                              '{250.688, 39.2766}',
                                                                              '{250.688, 25.65}',
                                                                              '{256.031, 25.65}',
                                                                              '{256.031, 12.2344}',
                                                                              '{274.875, 12.2344}',
                                                                              '{274.875, 25.65}',
                                                                              '{281.109, 25.65}',
                                                                              '{281.109, 39.2766}',
                                                                              '{274.875, 39.2766}',
                                                                              '{321.094, 71.2547}',
                                                                              '{286.875, 71.2547}',
                                                                              '{286.875, 6.11719}',
                                                                              '{306.422, 6.11719}',
                                                                              '{306.422, 55.6031}',
                                                                              '{321.094, 55.6031}',
                                                                              '{371.438, 71.2547}',
                                                                              '{352.594, 71.2547}',
                                                                              '{352.75, 69.7359}',
                                                                              '{352.875, 68.2875}',
                                                                              '{352.969, 66.9094}',
                                                                              '{353.062, 65.5312}',
                                                                              '{353.156, 64.4203}',
                                                                              '{353.25, 63.5766}',
                                                                              '{350, 69.3141}',
                                                                              '{345.641, 72.1828}',
                                                                              '{340.172, 72.1828}',
                                                                              '{335.422, 72.1828}',
                                                                              '{331.656, 70.0453}',
                                                                              '{328.875, 65.7703}',
                                                                              '{326.125, 61.5234}',
                                                                              '{324.75, 55.6453}',
                                                                              '{324.75, 48.1359}',
                                                                              '{324.75, 40.8797}',
                                                                              '{326.172, 35.1703}',
                                                                              '{329.016, 31.0078}',
                                                                              '{331.859, 26.789}',
                                                                              '{335.734, 24.6797}',
                                                                              '{340.641, 24.6797}',
                                                                              '{345.672, 24.6797}',
                                                                              '{349.734, 27.4078}',
                                                                              '{352.828, 32.8641}',
                                                                              '{352.766, 32.3016}',
                                                                              '{352.719, 31.8094}',
                                                                              '{352.688, 31.3875}',
                                                                              '{352.656, 30.9656}',
                                                                              '{352.625, 30.6141}',
                                                                              '{352.594, 30.3328}',
                                                                              '{352.406, 27.675}',
                                                                              '{352.266, 25.65}',
                                                                              '{371.438, 25.65}',
                                                                              '{352.406, 47.8828}',
                                                                              '{352.406, 46.1953}',
                                                                              '{352.336, 44.7609}',
                                                                              '{352.195, 43.5797}',
                                                                              '{352.055, 42.3984}',
                                                                              '{351.828, 41.4352}',
                                                                              '{351.516, 40.6898}',
                                                                              '{351.203, 39.9445}',
                                                                              '{350.797, 39.4102}',
                                                                              '{350.297, 39.0867}',
                                                                              '{349.797, 38.7633}',
                                                                              '{349.188, 38.6016}',
                                                                              '{348.469, 38.6016}',
                                                                              '{345.281, 38.6016}',
                                                                              '{343.688, 42.4125}',
                                                                              '{343.688, 50.0344}',
                                                                              '{343.688, 55.4907}',
                                                                              '{345.109, 58.2188}',
                                                                              '{347.953, 58.2188}',
                                                                              '{350.922, 58.2188}',
                                                                              '{352.406, 54.7735}',
                                                                              '{352.406, 47.8828}',
                                                                              '{399.328, 71.2547}',
                                                                              '{380.109, 71.2547}',
                                                                              '{380.109, 0}',
                                                                              '{398.906, 0}',
                                                                              '{398.906, 24.975}',
                                                                              '{398.906, 27.0844}',
                                                                              '{398.812, 29.5031}',
                                                                              '{398.625, 32.2313}',
                                                                              '{400.344, 29.475}',
                                                                              '{402.078, 27.5203}',
                                                                              '{403.828, 26.3672}',
                                                                              '{405.641, 25.2422}',
                                                                              '{407.922, 24.6797}',
                                                                              '{410.672, 24.6797}',
                                                                              '{415.797, 24.6797}',
                                                                              '{419.766, 26.8031}',
                                                                              '{422.578, 31.05}',
                                                                              '{425.391, 35.2688}',
                                                                              '{426.797, 41.2171}',
                                                                              '{426.797, 48.8953}',
                                                                              '{426.797, 56.236}',
                                                                              '{425.344, 61.9453}',
                                                                              '{422.438, 66.0234}',
                                                                              '{419.562, 70.1297}',
                                                                              '{415.578, 72.1828}',
                                                                              '{410.484, 72.1828}',
                                                                              '{408.016, 72.1828}',
                                                                              '{405.922, 71.6766}',
                                                                              '{404.203, 70.6641}',
                                                                              '{403.359, 70.1297}',
                                                                              '{402.492, 69.4125}',
                                                                              '{401.602, 68.5125}',
                                                                              '{400.711, 67.6125}',
                                                                              '{399.812, 66.4875}',
                                                                              '{398.906, 65.1375}',
                                                                              '{398.938, 65.6719}',
                                                                              '{398.969, 66.1289}',
                                                                              '{399, 66.5086}',
                                                                              '{399.031, 66.8883}',
                                                                              '{399.062, 67.2047}',
                                                                              '{399.094, 67.4578}',
                                                                              '{407.344, 48.5156}',
                                                                              '{407.344, 41.9906}',
                                                                              '{405.75, 38.7281}',
                                                                              '{402.562, 38.7281}',
                                                                              '{399.75, 38.7281}',
                                                                              '{398.344, 41.8078}',
                                                                              '{398.344, 47.9672}',
                                                                              '{398.344, 54.4078}',
                                                                              '{399.797, 57.6281}',
                                                                              '{402.703, 57.6281}',
                                                                              '{405.797, 57.6281}',
                                                                              '{407.344, 54.5907}',
                                                                              '{407.344, 48.5156}',
                                                                              '{407.344, 48.5156}']},
                                                    'Bounds': '{{1.8958, 92.0274}, {426.797, 91.5891}}',
                                                    'CTMKey': 'YES',
                                                    'Class': 'Spline',
                                                    'Effects': [{'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg=='],
                                                                 'EffectClass': 'FillEffect'},
                                                                {'Antialias': 'YES',
                                                                 'Colors': ['BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                                                                            'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='],
                                                                 'EffectClass': 'StrokeEffect',
                                                                 'LineWidth': '0.15',
                                                                 'Outset': '{{1, 1}, {1, 1}}'}],
                                                    'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                                    'Layer': '0',
                                                    'ScaleY': '0.900000',
                                                    'UniqueID': '1077'}],
                                 'HTMLRecord': {'HTMLRecordClass': 'HTMLRecord'},
                                 'Layer': '0',
                                 'OriginalSize': '{430, 269}',
                                 'UniqueID': '1095'}],
               'Layers': [{'LayerNumber': '0',
                           'Locked': 'NO',
                           'Printable': 'YES',
                           'Visible': 'YES'},
                          {'LayerNumber': '1',
                           'Locked': 'NO',
                           'Printable': 'YES',
                           'Visible': 'YES'}],
               'PageClass': 'Page',
               'PageHTML': {'AfterContent': '',
                            'AlinkColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAAEAAYY=',
                            'BGColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgEBhg==',
                            'BeforeContent': '',
                            'BodyString': '',
                            'CenterInTable': 'YES',
                            'ColorFromView': 'YES',
                            'Description': '',
                            'HTMLClass': 'PageHTML',
                            'HandCraftedBody': 'NO',
                            'Head': '',
                            'ImagePath': '',
                            'Keywords': '',
                            'LinkColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAAABAYY=',
                            'NavBarAbove': 'YES',
                            'NavBarBelow': 'NO',
                            'OutputFileType': '0',
                            'OutputLine': 'NO',
                            'TextColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMDhAJmZgABhg==',
                            'UseBiggerFonts': 'NO',
                            'UseDocumentHTML': 'YES',
                            'VlinkColor': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAdOU0NvbG9yAISECE5TT2JqZWN0AIWEAWMBhARmZmZmAQAAAYY='},
               'PageSize': '{595, 842}'}],
 'PrintInfo': 'BAt0eXBlZHN0cmVhbYED6IQBQISEhAtOU1ByaW50SW5mbwGEhAhOU09iamVjdACFkoSEhBNOU011dGFibGVEaWN0aW9uYXJ5AISEDE5TRGljdGlvbmFyeQCUhAFpEpKEhIQITlNTdHJpbmcBlIQBKxBOU0pvYkRpc3Bvc2l0aW9uhpKEmZkPTlNQcmludFNwb29sSm9ihpKEmZkOTlNCb3R0b21NYXJnaW6GkoSEhAhOU051bWJlcgCEhAdOU1ZhbHVlAJSEASqEhAFmnVqGkoSZmQtOU1BhcGVyTmFtZYaShJmZAkE0hpKEmZkPTlNQcmludEFsbFBhZ2VzhpKEnZyEhAFzngCGkoSZmQ1OU1JpZ2h0TWFyZ2luhpKEnZyfnUiGkoSZmQhOU0NvcGllc4aShJ2chIQBU58BhpKEmZkPTlNTY2FsaW5nRmFjdG9yhpKEnZyEhAFkoAGGkoSZmQtOU0ZpcnN0UGFnZYaShJ2cqZ8BhpKEmZkUTlNWZXJ0aWNhbFBhZ2luYXRpb26GkoSdnKSeAIaShJmZFU5TSG9yaXpvbmFsUGFnaW5hdGlvboaShJ2cpJ4ChpKEmZkWTlNIb3Jpem9udGFsbHlDZW50ZXJlZIaShJ2cpJ4BhpKEmZkMTlNMZWZ0TWFyZ2luhpKEnZyfnUiGkoSZmQ1OU09yaWVudGF0aW9uhpKEnZykngCGkoSZmRlOU1ByaW50UmV2ZXJzZU9yaWVudGF0aW9uhpKjkoSZmQpOU0xhc3RQYWdlhpKEnZyEl5eCf////4aShJmZC05TVG9wTWFyZ2luhpKEnZyfnVqGkoSZmRROU1ZlcnRpY2FsbHlDZW50ZXJlZIaStJKEmZkLTlNQYXBlclNpemWGkoSenISEDHtfTlNTaXplPWZmfaGBAlOBA0qGhoY=',
 'SnapToGrid': 'NO',
 'ViewRect': '{{62.1875, 1.74623e-08}, {464.844, 499.219}}',
 'Zoom': '1.280000'}

######################################################################
# Math helpers
######################################################################

def scaleBackAfterSkew(width, height, skewTransform, _debug=0):
    "Returns a scaling transform to re-fit a skewed rect into its original size rect."

    # Not excessively tested!! Handle with care!

    mm = mmult
    x0, y0 = width, height
    if _debug:
        print "before skewing: x1, y1", x0, y0
    trans0 = skewTransform
    x1, y1 = transformPoint(trans0, (width, height))
    if _debug:
        print "after skewing: x1, y1", x1, y1

    scx = scale(1, 1)
    scy = scale(1, 1)
    fx = x0/x1
    if fx < 1:
        scx = scale(fx, 1)
        if _debug:
            print 'fx', fx
            print 'scx', scx
    fy = y0/y1
    if fy < 1:
        scy = scale(1, fy)
        if _debug:
            print 'fy', fy
            print 'scy', scy
    sc = mm(scx, scy)
    if _debug:
        print 'sc', sc

    trans1 = mm(sc, trans0)
    x1, y1 = transformPoint(trans1, (width, height))
    if _debug:
        print "final: x1, y1", x1, y1

    return trans1


######################################################################
# Data handling
######################################################################

def bounds2rect(bounds):
    "Convert a Bounds value to a RL rectangle tuple."

    bounds = string.replace(bounds, '{', '(')
    bounds = string.replace(bounds, '}', ')')
    (x, y), (width, height) = eval(bounds)
    bounds = x, y, width, height

    return bounds


def bezierDict2data(dict):
    "Fetch Bezier path data from a dict."

    bounds = bounds2rect(dict['Bounds'])
    ops = dict['BezierDict']['Operations']
    ops = map(lambda x:int(x), ops)
    pts = dict['BezierDict']['Points']
    pts = map(lambda x:eval(x[1:-1]), pts)

    return ops, pts, bounds


def rectDict2data(dict):
    "Fetch rectangle data from a dict."

    bounds = bounds2rect(dict['Bounds'])
    rot = dict.get('Rotation', 0)

    return bounds, rot


def displacePoints(pts, dx, dy):
    "Return a list of points displaced by (dx, dy)."

    for i in xrange(len(pts)):
        p = pts[i]
        pts[i] = (p[0]+dx, p[1]+dy)

    return pts


######################################################################


class RLVectorLogo(Widget):
    """Vectorised ReportLab logo.

    This is based on a Create XML file that was transformed into
    a canned Python dictionary containing the polygon path data.
    For further information about Create see www.stone.com.

    The logo can be drawn either fully vertical, skewed, boxed and/
    or shadowed. The shadow consists of an identical logo copy being
    drawn behind the 'real' logo in a color-mix composed of a 50-50
    blend between the logo's stroke and fill/background color, weigh-
    ted by the shadow factor attribute.
    
    Instances are guaranteed to draw only inside the area defined by
    the rectangle (x, y, width, height), independant of the skewing
    values or the border width of the enclosing box if provided.
    This was tested only for 'reasonable' values, though. The only
    exception is when setting 'noRescale' to 1, which suppress all
    rescaling (this can be useful for ensuring the original aspect
    ratio, but you should use it only when you know what you do!).
    """

    _attrMap = AttrMap(
        x = AttrMapValue(isNumber,
            desc='x-coord (default 0)'),
        y = AttrMapValue(isNumber,
            desc='y-coord (default 0)'),
        width = AttrMapValue(isNumber,
            desc='width (default 129)'),
        height = AttrMapValue(isNumber,
            desc='height (default 86)'),

        shadow = AttrMapValue(isNumberOrNone,
            desc='None or fraction (default 0.75)'),
        dx = AttrMapValue(isNumber,
            desc='shadow x-displacement (default 2)'),
        dy = AttrMapValue(isNumber,
            desc='shadow y-displacement (default 2)'),
        skewX = AttrMapValue(isNumber,
            desc='x-skew (default 10)'),
        skewY = AttrMapValue(isNumber,
            desc='y-skew (default 0)'),
        noRescale = AttrMapValue(isNumber,
            desc='allow drawing outside regular area (default 0)'),

        strokeColor = AttrMapValue(isColorOrNone,
            desc='lettering stroke color'),
        fillColor = AttrMapValue(isColorOrNone,
            desc='background color'),

        strokeWidth = AttrMapValue(isNumber,
            desc='lettering stroke width (default 0)'),
        borderWidth = AttrMapValue(isNumber,
            desc='enclosing border width (default 0)'),
        )

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 129
        self.height = 86

        self.dx = 2
        self.dy = 2
        self.shadow = 0.75

        self.strokeColor = black # Or ReportLabBlue, mostly...
        self.fillColor = white   # Used for enclosing box.

        self.skewX = 10
        self.skewY = 0
        self.strokeWidth = 0
        self.borderWidth = 0
        self.noRescale = 1       # should be set to 0 by default

        self._showPoints = 0
        self._debug = 0

        # Find outer bounds of the graphic.
        bounds = _LOGODATA['PageList'][0]['GraphicsList'][0]['Bounds']        
        bounds = bounds2rect(bounds)
        bounds = map(float, bounds)
        self._width, self._height = bounds[2:4]


    def demo(self):
        d = shapes.Drawing(self.width, self.height)
        d.add(self)

        return d


    def makeShadowColor(self, color1, color2, fraction):
        "Derive a shadow color from two colors and a weight fraction."

        c1, c2 = color1, color2
        f = fraction
        shadowColor = Color((c1.red + c2.red)/2.*f,
                            (c1.green + c2.green)/2.*f,
                            (c1.blue + c2.blue)/2.*f)

        return shadowColor


    def _addDisks(self, drawing, pts):
        "Add a list of disks with changing colors from blue to red."
        
        startCol = blue
        endCol = red
        for i in range(len(pts)):
            pt = pts[i]
            c = linearlyInterpolatedColor(startCol, endCol, 0, len(pts), i)
            disk = Circle(pt[0], pt[1], 2)
            disk.strokeColor = c
            disk.fillColor = c
            drawing.add(disk)


    def _addPaths(self, group, ops, pts, isShadow=0):
        # This could, perhaps also use Path(points, operators) syntax...
        # (if it gets the winding right).

        g = group

        moveTo, lineTo, curveTo, close = range(4)
        left, right = 1, -1

        path = Path()
        circleLists = []
        lines = []

        strokeColor = self.strokeColor
        fillColor = self.fillColor

        j = 0
        for i in xrange(len(ops)):
            op = ops[i]
            pt = pts[j]

            if op == moveTo:
                path.strokeWidth = self.strokeWidth
                points = []
                path.moveTo(pt[0], pt[1])
                points.append(pt)
            elif op == 1:
                path.lineTo(pt[0], pt[1])
                points.append(pt)
            elif op == 2:
                cpt1, cpt2 = pts[j+1], pts[j+2] # control points
                j = j + 2
                path.curveTo(pt[0], pt[1],
                             cpt1[0], cpt1[1],
                             cpt2[0], cpt2[1])
                points.append(pt)
                lines.append((cpt1, cpt2))
            elif op == 3:
                path.closePath()
                if isShadow:
                    path.strokeColor = fillColor
                    path.fillColor = fillColor
                else:
                    path.strokeColor = strokeColor
                    path.fillColor = strokeColor
                j = j - 1
                circleLists.append(points)
                points = []
                
            j = j + 1

        if points:
            path.closePath()
            if isShadow:
                path.strokeColor = self._shadowColor
                path.fillColor = self._shadowColor
            else:
                path.strokeColor = strokeColor
                path.fillColor = strokeColor
            circleLists.append(points)

        g.add(path)

        if self._showPoints:
            for points in circleLists:
                self._addDisks(g, points)


    def _addBox(self):
        "Add the logo's filled enclosing box."

        g = Group()

        rect = Rect(0, 0, self._width, self._height)
        rect.strokeColor = None
        rect.fillColor = self.fillColor
        g.add(rect)

        return g


    def _addRect(self, group, bounds, rot, isShadow):
        "Add a rectangle."
        
        x, y, width, height = bounds
        strokeColor, fillColor = self.strokeColor, self.fillColor

        rect = Rect(x, y, width, height)
        rect.strokeWidth = self.strokeWidth
        if isShadow:
            rect.strokeColor = self._shadowColor
            rect.fillColor = self._shadowColor
        else:
            rect.strokeColor = strokeColor
            rect.fillColor = strokeColor

        if rot != 0:
            rect.strokeColor = red
            rect.fillColor = red

        g = Group()
        g.add(rect)
        if rot != 0:
            # doesn't work yet!
            cx = x+width/2.0
            cy = y+height/2.0
##            g.shift(-cx, -cy)
##            g.rotate(rot)
##            g.shift(cx, cy)   

        group.add(g)


    def _addDebuggingAids(self):
        "Add red frames and circles for visual debugging purposes."

        m = self.borderWidth
        mm = mmult

        stuff = []

        tr = translate(self.x, self.y)
        skx = skewX(self.skewX)
        sky = skewY(self.skewY)
        trans0 = mm(skx, sky)
        x0, y0 = transformPoint(tr, (m, m))
        scaleBack = scaleBackAfterSkew(self.width, self.height, trans0)
        trans1 = mm(tr, scaleBack)
        x1, y1 = transformPoint(trans1, (self.width-m, self.height-m))
        trans2 = mm(tr, trans0)
        x2, y2 = transformPoint(trans2, (self.width-m, self.height-m))

        f = Group()
        c0 = Circle(x0, y0, 5)
        c1 = Circle(x1, y1, 5)
        c2 = Circle(x2, y2, 5)
        c0.fillColor = red
        c1.fillColor = red
        c2.fillColor = green
        f.add(c0)
        f.add(c1)
        f.add(c2)
        stuff.append(f)

        rect = Rect(self.x, self.y, self.width, self.height)
        rect.strokeColor = red
        rect.fillColor = None
        stuff.append(rect)

        if self.borderWidth:
            m = self.borderWidth
            rect = Rect(self.x+m, self.y+m, self.width-2*m, self.height-2*m)
            rect.strokeColor = red
            rect.fillColor = None
            stuff.append(rect)

        return stuff


    def drawCreateElementInBounds(self, g, el, bounds=None, isShadow=0):
        "Add a Create element to a group after converting it to some shapes."
        
        klass = el['Class']
        if klass == 'Group':
            for sel in el['GroupGraphics']:
                self.drawCreateElementInBounds(g, sel, bounds, isShadow)
        elif klass == 'Spline':
            ops, pts, elBounds = bezierDict2data(el)
            pts = map(lambda p:(p[0],-p[1]), pts)
            dx, dy = elBounds[0:2]
            dpts = displacePoints(pts, 0, self._height)
            dpts = displacePoints(dpts, dx, -dy)
            self._addPaths(g, ops, dpts, isShadow)
        elif klass == 'Rectangle':
            elBounds, rot = rectDict2data(el)
            x, y, width, height = elBounds
            x = x + bounds[0]
            y = self._height - y - height
            elBounds = x, y, width, height
            self._addRect(g, elBounds, rot, isShadow)
        elif klass == 'MultiLine':
            ops, pts, elBounds = bezierDict2data(el)
            pts = map(lambda p:(p[0],-p[1]), pts)
            dx, dy = elBounds[0:2]
            dx, dy = dx + bounds[0], dy + bounds[1]
            dpts = displacePoints(pts, 0, self._height)
            dpts = displacePoints(dpts, dx, -dy)
            self._addPaths(g, ops, dpts, isShadow)
        else:
            print 'Unknown Create element: %s' % klass


    def _addLogo(self, total, isShadow=0):
        g = Group() # will contain text glyphs and paper border

        # transform data into shapes
        dict = _LOGODATA
        groupGraph = dict['PageList'][0]['GraphicsList'][0]['GroupGraphics']
        for el in groupGraph:
            bounds = bounds2rect(el['Bounds'])
            self.drawCreateElementInBounds(g, el, bounds, isShadow)

        # add real logo
        m = self.borderWidth
        if self.shadow:
            g.scale((self.width-2*m-self.dx)/self._width,
                    (self.height-2*m-self.dy)/self._height)
        else:
            g.scale((self.width-2*m)/self._width,
                    (self.height-2*m)/self._height)
        g.skew(self.skewX, self.skewY)

        # rescale logo if needed to fit into original area
        skx = skewX(self.skewX)
        sky = skewY(self.skewY)
        sk = mmult(skx, sky)
        scaleBack = scaleBackAfterSkew(self.width, self.height, sk)
        scaleBackBox = scaleBackAfterSkew(self.width-2*m, self.height-2*m, sk)
        self._rescaleX, self._rescaleY = scaleBackBox[0], scaleBackBox[3]

        if not self.noRescale:
            g.scale(scaleBack[0], scaleBack[3])

        if isShadow:
            g.shift(self.x + m + self.dx, self.y + m + self.dy)
        else:
            g.shift(self.x + m, self.y + m)

        total.add(g)

        # add visual debugging aids
        if self._debug:
            for stuff in self._addDebuggingAids():
                total.add(stuff)


    def draw(self):
        total = Group() # will contain everything

        # add shadow logo
        if self.shadow != None and 0 <= self.shadow <= 1:
            msc = self.makeShadowColor
            self._shadowColor = msc(self.strokeColor, self.fillColor, self.shadow)
            self._addLogo(total, isShadow=1)

        # add real logo
        self._addLogo(total)

        # add enclosing box as first group element
        h = Group()
        h.add(self._addBox())
        m = self.borderWidth
        ex = self.width
        ey = self.height
        if self.noRescale:
            # we now draw outside the original area...
            fx, fy = self._rescaleX, self._rescaleY
            ex = (self.width-2*m) * (1./fx) + 2*m
            ey = (self.height-2*m) * (1./fy) + 2*m
        scx = (ex)/self._width
        scy = (ey)/self._height
        h.scale(scx, scy)
        h.shift(self.x, self.y)
        total.insert(0, h)

        return total


def main():
    from reportlab.rl_config import _verbose

    # make first PDF page with reasonable logos
    top = 27.7*cm
    left = 0.5*cm
    
    l1 = RLVectorLogo()
    l1.x = left
    l1.y = top - 100
    l1.width = 150
    l1.height = 100

    l2 = RLVectorLogo()
    l2.x = left + 200
    l2.y = top - 100
    l2.width = 150
    l2.height = 100
    l2.strokeColor = ReportLabBlue
    l2.skewX = 0
    l2.skewY = 0

    l11 = RLVectorLogo()
    l11.x = left + 400
    l11.y = top - 100
    l11.width = 150
    l11.height = 100
    l11.shadow = None
    l11.strokeColor = ReportLabBlue
    l11.skewX = 0
    l11.skewY = 0

    l3 = RLVectorLogo()
    l3.x = left
    l3.y = top - 100 - 150
    l3.width = 150
    l3.height = 100

    l4 = RLVectorLogo()
    l4.x = left + 200
    l4.y = top - 100 - 150
    l4.width = 150
    l4.height = 100
    l4.strokeColor = ReportLabBlue

    l12 = RLVectorLogo()
    l12.x = left + 400
    l12.y = top - 100 - 150
    l12.width = 150
    l12.height = 100
    l12.shadow = None
    l12.strokeColor = black

    l5 = RLVectorLogo()
    l5.x = left
    l5.y = top - 100 - 2*150
    l5.width = 150
    l5.height = 100
    l5.skewX = 20
    l5.skewY = 10

    l6 = RLVectorLogo()
    l6.x = left + 200
    l6.y = top - 100 - 2*150
    l6.width = 150
    l6.height = 100
    l6.strokeColor = ReportLabBlue
    l6.skewX = 20
    l6.skewY = 10

    l15 = RLVectorLogo()
    l15.x = left + 400
    l15.y = top - 100 - 2*150
    l15.width = 150
    l15.height = 100
    l15.strokeColor = yellow
    l15.fillColor = navy
    l15.borderWidth = 5
    l15.skewX = 10
    l15.skewY = 0

    l7 = RLVectorLogo()
    l7.x = left
    l7.y = top - 100 - 3*150
    l7.width = 150
    l7.height = 100
    l7.skewX = 0
    l7.skewY = 0
    l7.borderWidth = 5
    l7.strokeColor = white
    l7.fillColor = black

    l8 = RLVectorLogo()
    l8.x = left + 200
    l8.y = top - 100 - 3*150
    l8.width = 150
    l8.height = 100
    l8.skewX = 0
    l8.skewY = 0
    l8.borderWidth = 5
    l8.strokeColor = white
    l8.fillColor = ReportLabBlue

    l13 = RLVectorLogo()
    l13.x = left + 400
    l13.y = top - 100 - 3*150
    l13.width = 150
    l13.height = 100
    l13.skewX = 0
    l13.skewY = 0
    l13.borderWidth = 5
    l13.strokeColor = white
    l13.shadow = None
    l13.fillColor = ReportLabBlue

    l9 = RLVectorLogo()
    l9.x = left
    l9.y = top - 100 - 4*150
    l9.width = 150
    l9.height = 100
##    l9.skewY = 10
    l9.borderWidth = 5
    l9.strokeColor = white
    l9.fillColor = black

    l10 = RLVectorLogo()
    l10.x = left + 200
    l10.y = top - 100 - 4*150
    l10.width = 150
    l10.height = 100
    l10.borderWidth = 5
    l10.strokeColor = white
    l10.fillColor = ReportLabBlue

    l14 = RLVectorLogo()
    l14.x = left + 400
    l14.y = top - 100 - 4*150
    l14.width = 150
    l14.height = 100
    l14.borderWidth = 5
    l14.strokeColor = white
    l14.shadow = None
    l14.fillColor = black

    d = Drawing(21*cm, 29.7*cm)
    for logo in (l1, l2, l3, l4, l5, l6, l7, l8, l9, l10,
                 l11, l12, l13, l14, l15):
        d.add(logo)
    filename = 'rllogos.pdf'
    renderPDF.drawToFile(d, filename, '')
    if _verbose:
        print "saved %s" % filename


if __name__ == '__main__':
    main()
