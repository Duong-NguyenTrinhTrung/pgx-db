from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# from common import definitions
# from common.selection import SimpleSelection, Selection, SelectionItem

from common.views import AbsTargetSelectionTable

import os
from collections import OrderedDict
from io import BytesIO
import xlsxwriter, xlrd


class TargetSelection(AbsTargetSelectionTable):
    step = 1
    number_of_steps = 2
    docs = "sites.html#site-search-manual"
    title = "SELECT RECEPTORS"
    selection_boxes = OrderedDict([
        ('reference', False),
        ('targets', True),
        ('segments', False),
    ])
    buttons = {
        "continue": {
            "label": "Next",
            "onclick": "submitSelection('/sitesearch/segmentselection');",
            "color": "success",
        },
    }