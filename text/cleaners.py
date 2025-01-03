""" from https://github.com/keithito/tacotron """

'''
Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
'''

import re
from unidecode import unidecode
import decimal
from phonemizer import phonemize
from number_to_words_ht import number_to_words_ht
from threading import Lock

# Custom IPA mappings for Haitian Creole
_IPA_RULES = [
    (r'ch', 'ʃ'),      # 'ch' → 'ʃ'
    (r'ou', 'u'),      # 'ou' → 'u'
    (r'ay', 'aj'),     # 'ay' → 'aj'
    (r'ye', 'je'),     # 'ye' → 'je'
    (r'ò', 'ɔ'),       # 'ò' → 'ɔ'
    (r'j', 'ʒ'),       # 'j' → 'ʒ'
    (r'k', 'k'),       # 'k' → 'k'
    (r'pe', 'pˈe'),    # 'pe' with stress
    (r' ', ' ')        # Ensure spaces remain
]

# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
  ('mrs', 'misess'),
  ('mr', 'mister'),
  ('dr', 'doctor'),
  ('st', 'saint'),
  ('co', 'company'),
  ('jr', 'junior'),
  ('maj', 'major'),
  ('gen', 'general'),
  ('drs', 'doctors'),
  ('rev', 'reverend'),
  ('lt', 'lieutenant'),
  ('hon', 'honorable'),
  ('sgt', 'sergeant'),
  ('capt', 'captain'),
  ('esq', 'esquire'),
  ('ltd', 'limited'),
  ('col', 'colonel'),
  ('ft', 'fort'),
]]

# List of (regular expression, replacement) pairs for _hat_abbreviations:
_hat_abbreviations = [(re.compile('\\b%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('Dr.', 'Doktè'),
    ('Pr.', 'Pwofesè'),
    ('Rev.', 'Reveran'),
    ('Fr.', 'Frè'),
    ('Mèt', 'Mèt'),
    ('Mgr.', 'Monseyè'),
    ('Min.', 'Minis'),
    ('Dep.', 'Depite'),
    ('Sen.', 'Senatè'),
    ('Gov.', 'Gouvènè'),
    ('Jr.', 'Jinyò'),
    ('Sr.', 'Sè'),
    ('Pè.', 'Pè'),
    ('Rep.', 'Reprezantan'),
    ('Dir.', 'Direktè'),
    ('Secr.', 'Sekretè'),
    ('Gr.', 'Gran'),
    ('Pt.', 'Piti'),
    ('Mt.', 'Mòn'),
    ('Rte.', 'Rout'),
    ('St.', 'Sen'),
    # ('Rep. Ayiti', 'Repiblik Ayiti'),
    # ('Univ.', 'Inivèsite'),
    # ('ONG', 'Òganizasyon Non-Gouvènmantal'),
    # ('Fond.', 'Fondasyon'),
    # ('Inst.', 'Enstitisyon'),
    # ('LONI', 'Òganizasyon Nasyonzini'),
    # ('OEA', 'Òganizasyon Eta Ameriken'),
    # ('FAES', 'Fon Asistans Ekonomik ak Sosyal'),
    # ('PNH', 'Polis Nasyonal d Ayiti')

    ('vi', 'lavi'),
    ('Iv', 'Yves'),
]]


# List of (regular expression, replacement) pairs for _special_characters:
_special_characters = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('[\s]*/[\s]*', ', '), # Forward slash - U+002F
    ('[\s]*[-]+[\s]*', '; '), # Hyphen - U+002D
    ('[\s]*[—]+[\s]*', '; '), # Em dash - U+2014
]]

phonemize_lock = Lock()

def expand_abbreviations(text):
  for regex, replacement in _abbreviations:
    text = re.sub(regex, replacement, text)
  return text


def expand_hat_abbreviations(text):
  for regex, replacement in _hat_abbreviations:
    text = re.sub(regex, replacement, text)
  return text


def expand_numbers(text):
  def replace_number(match):
    try:
#      print(f"match: {match.group()}")
      return number_to_words_ht(int(match.group()))
    except (ValueError, decimal.InvalidOperation):
      return match.group()
  return re.sub(r'\d+', replace_number, text)


def lowercase(text):
  return text.lower()


def collapse_whitespace(text):
  return re.sub(_whitespace_re, ' ', text)


def convert_to_ascii(text):
  return unidecode(text)


def apply_ipa_rules(text):
  """Applies custom Haitian Creole IPA rules."""
  for pattern, replacement in _IPA_RULES:
      text = re.sub(pattern, replacement, text)
  return text
  
  
def convert_special_characters(text):
  '''Convert special characters to their respective.'''
  for regex, replacement in _special_characters:
    text = re.sub(regex, replacement, text)
  return text


def basic_cleaners(text):
  '''Basic pipeline that lowercases and collapses whitespace without transliteration.'''
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def transliteration_cleaners(text):
  '''Pipeline for non-English text that transliterates to ASCII.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def english_cleaners(text):
  '''Pipeline for English text, including abbreviation expansion.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_abbreviations(text)
  phonemes = phonemize(text, language='en-us', backend='espeak', strip=True)
  phonemes = collapse_whitespace(phonemes)
  return phonemes


def english_cleaners2(text):
  '''Pipeline for English text, including abbreviation expansion. + punctuation + stress'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_abbreviations(text)
  phonemes = phonemize(text, language='en-us', backend='espeak', strip=True, preserve_punctuation=True, with_stress=True)
  phonemes = collapse_whitespace(phonemes)
  return phonemes


def haitian_creole_cleaners(text):
  '''Pipeline for Haitian Creole text, including abbreviation expansion.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_hat_abbreviations(text)
  phonemes = phonemize(text, language='ht', backend='espeak', strip=True)
  phonemes = collapse_whitespace(phonemes)
  return phonemes


def haitian_creole_cleaners2(text):
  '''Pipeline for Haitian Creole text, including abbreviation expansion, punctuation, and stress.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_hat_abbreviations(text)
  text = convert_special_characters(text)
  text = expand_numbers(text)
#  print(f"cleaned text: {text}")
  with phonemize_lock:
    phonemes = phonemize(text, language='ht', backend='espeak', strip=True, preserve_punctuation=True, with_stress=True)
    phonemes = collapse_whitespace(phonemes)
    return phonemes
  

def haitian_creole_cleaners3(text):
  '''Pipeline for Haitian Creole text, including abbreviation expansion, punctuation, and stress.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_hat_abbreviations(text)
  text = convert_special_characters(text)
  text = expand_numbers(text)
  text = apply_ipa_rules(text)  # Apply custom IPA rules
  text = collapse_whitespace(text)
#  print(f"cleaned text: {text}")
  return text
