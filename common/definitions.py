from collections import OrderedDict
from decimal import Decimal

from django.core.cache import cache

AMINO_ACIDS = OrderedDict([
    ('A', 'Ala'),
    ('C', 'Cys'),
    ('D', 'Asp'),
    ('E', 'Glu'),
    ('F', 'Phe'),
    ('G', 'Gly'),
    ('H', 'His'),
    ('I', 'Ile'),
    ('K', 'Lys'),
    ('L', 'Leu'),
    ('M', 'Met'),
    ('N', 'Asn'),
    ('P', 'Pro'),
    ('Q', 'Gln'),
    ('R', 'Arg'),
    ('S', 'Ser'),
    ('T', 'Thr'),
    ('V', 'Val'),
    ('W', 'Trp'),
    ('Y', 'Tyr'),
    ('B', 'Asx'),
    ('Z', 'Glx'),
    ('J', 'Xle'),
    ('-', 'Gap'),
    ('+', 'Tie')
])

FULL_AMINO_ACIDS = OrderedDict([
    ('A', 'Alanine'),
    ('C', 'Cysteine'),
    ('D', 'Aspartate'),
    ('E', 'Glutamate'),
    ('F', 'Phenylalanine'),
    ('G', 'Glycine'),
    ('H', 'Histidine'),
    ('I', 'Isoleucine'),
    ('K', 'Lysine'),
    ('L', 'Leucine'),
    ('M', 'Methionine'),
    ('N', 'Asparagine'),
    ('P', 'Proline'),
    ('Q', 'Glutamine'),
    ('R', 'Arginine'),
    ('S', 'Serine'),
    ('T', 'Threonine'),
    ('V', 'Valine'),
    ('W', 'Tryptophan'),
    ('Y', 'Tyrosine'),
    ('B', 'Aspartate or Asparagine'),
    ('Z', 'Glutamate or Glutamine'),
    ('J', 'Leucine or Isoleucine'),
    ('-', 'Gap'),
    ('+', 'Tie')
])