from django.shortcuts import render
from gene.models import Gene
import json
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
from collections import OrderedDict
from protein.models import Species 

# Create your views here.


def common_menu(request):
    context = {
        'DOCUMENTATION_URL': settings.DOCUMENTATION_URL,  # Add DOCUMENTATION_URL to the context
    }
    return render(request, 'common.html', context)

def autocompleteModel(request):
    template_name = 'selection.html'
    if request.is_ajax():
        q = request.GET.get('term', '').capitalize()
        search_qs = Gene.objects.filter(name__startswith=q)
        results = []
        print (q)
        for r in search_qs:
            results.append(r.FIELD)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


class AbsTargetSelectionTable(TemplateView):
    """An abstract class for the tablew target selection page used in many apps.

    To use it in another app, create a class-based view that extends this class
    """

    template_name = 'common/drugselectiontable.html'

    type_of_selection = 'drug_table'
    # selection_only_receptors = False
    import_export_box = True
    step = 1
    number_of_steps = 2
    title = 'SELECT DRUGS'
    description = 'Select drugs in the table (below) or browse the drug classification tree (right).  \
        + \n\nOnce you have selected all your targets, click the green button.'
    documentation_url = settings.DOCUMENTATION_URL

    docs = False
    filters = True

    drug_input = False

    default_species = 'Human'
    # default_slug = '000'
    # default_subslug = '00'

    # numbering_schemes = False
    search = False
    family_tree = True
    redirect_on_select = False
    # filter_gprotein = False
    selection_heading = False
    buttons = {
        'continue': {
            'label': 'Continue to next step',
            'url': '#',
            'color': 'success',
        },
    }
    # OrderedDict to preserve the order of the boxes
    selection_boxes = OrderedDict([
        # ('reference', False),
        ('drugs', True),
        # ('segments', False),
    ])

    # proteins and families
    #try - except block prevents manage.py from crashing - circular dependencies between protein - common
    # try:
    #     if ProteinFamily.objects.filter(slug=default_slug).exists():
    #         ppf = ProteinFamily.objects.get(slug=default_slug)
    #         pfs = ProteinFamily.objects.filter(parent=ppf.id).filter(slug__startswith=default_subslug)
    #         ps = Protein.objects.filter(family=ppf)
    #         psets = ProteinSet.objects.all().prefetch_related('proteins')
    #         tree_indent_level = []
    #         action = 'expand'
    #         # remove the parent family (for all other families than the root of the tree, the parent should be shown)
    #         del ppf

    #         # Load the target table data
    #         table_data = getTargetTable()
    # except Exception as e:
    #     pass

    # species
    sps = Species.objects.all()

    # g proteins
    # g_prots_slugs = ['100_001_002', '100_001_003', '100_001_001', '100_001_004', '100_001_005']
    # gprots = ProteinFamily.objects.filter(slug__in=g_prots_slugs)
    # gprots = ProteinGProtein.objects.all()

    # numbering schemes
    # gns = ResidueNumberingScheme.objects.exclude(slug=settings.DEFAULT_NUMBERING_SCHEME).exclude(slug__in=default_schemes_excluded)

    def get_context_data(self, **kwargs):
        """Get context from parent class

        (really only relevant for children of this class, as TemplateView does
        not have any context variables)
        """

        context = super().get_context_data(**kwargs)

        # get selection from session and add to context
        # get simple selection from session
        simple_selection = self.request.session.get('selection', False)

        # create full selection and import simple selection (if it exists)
        selection = Selection()

        # on the first page of a workflow, clear the selection (or dont' import from the session)
        if self.step is not 1:
            if simple_selection:
                selection.importer(simple_selection)

        # default species selection
        if self.default_species:
            sp = Species.objects.get(common_name=self.default_species)
            o = SelectionItem('species', sp)
            selection.species = [o]

        # update session
        simple_selection = selection.exporter()
        self.request.session['selection'] = simple_selection

        context['selection'] = {}
        for selection_box, include in self.selection_boxes.items():
            if include:
                context['selection'][selection_box] = selection.dict(selection_box)['selection'][selection_box]
        if self.filters:
            context['selection']['species'] = selection.species
            # context['selection']['annotation'] = selection.annotation
            # context['selection']['g_proteins'] = selection.g_proteins
            # context['selection']['pref_g_proteins'] = selection.pref_g_proteins

        # get attributes of this class and add them to the context
        attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
        for a in attributes:
            if not(a[0].startswith('__') and a[0].endswith('__')):
                context[a[0]] = a[1]
        return context
