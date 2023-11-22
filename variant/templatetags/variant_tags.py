from django.template import library

register = library.Library()


@register.inclusion_tag('variant/genebass_variant_row.html')
def render_genebass_variant_row(genebass):
    return {'genebass': genebass}
