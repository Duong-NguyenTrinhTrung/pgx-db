from django import template

register = template.Library()

COLORS = [
    '#FFE169',
    '#FAD643',
    '#EDC531',
    '#DBB42C',
    '#C9A227',
    '#B69121',
    '#A47E1B',
    '#926C15',
    '#805B10',
    '#76520E',
] 


@register.inclusion_tag('gene/variant_cell.html')
def render_variant_values_in_color_ranges(value):
    if value:
        value = float(value)
    else:
        value = 0.0

    if value < 0.1:
        color = COLORS[0]
    elif value < 0.2:
        color = COLORS[1]
    elif value < 0.3:
        color = COLORS[2]
    elif value < 0.4:
        color = COLORS[3]
    elif value < 0.5:
        color = COLORS[4]
    elif value < 0.6:
        color = COLORS[5]
    elif value < 0.7:
        color = COLORS[6]
    elif value < 0.8:
        color = COLORS[7]
    elif value < 0.9:
        color = COLORS[8]
    else:
        color = COLORS[9]

    return {
        'color': color,
        'value': value,
    }


