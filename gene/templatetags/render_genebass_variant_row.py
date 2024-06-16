from django import template
register = template.Library()

#defines a custom inclusion template tag named render_genebass_variant_row. When this tag is used in a Django template, it will render the 'genebass/genebass_variant_row.html' template file and pass the genebass_variant data as the context for that template.

#This is a decorator that registers a function as an inclusion template tag. It specifies the template file 'genebass/genebass_variant_row.html' that will be rendered when the inclusion tag is used in a template.
@register.inclusion_tag('genebass/genebass_variant_row.html')
#implementation of the inclusion tag. It takes a single argument genebass_variant, which represents the data that will be passed to the template.
def render_genebass_variant_row(genebass_variant):
    #returns a dictionary containing the context data to be passed to the template
    return {'genebass_variant': genebass_variant}

