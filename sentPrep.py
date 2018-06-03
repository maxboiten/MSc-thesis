#Code mostly adapted from pattern.nl (see https://github.com/clips/pattern/blob/master/pattern/text/nl/inflect.py)
import re

def is_vowel(x):
    return x in ("a", "e", "i", "o", "u")

adjective_attributive = {
        "civiel": "civiele",
        "complex": "complexe",
        "enkel": "enkele",
        "grof": "grove",
        "half": "halve",
        "luttel": "luttele",
        "mobiel": "mobiele",
        "parijs": "parijse",
        "ruw": "ruwe",
        "simpel": "simpele",
        "stabiel": "stabiele",
        "steriel": "steriele",
        "subtiel": "subtiele",
        "teer": "tere",
        "moe": "moe",
        "taboe": "taboe",
        "voldoende": "voldoende"
    }
adjective_predicative = {v:k for k,v in adjective_attributive.items()}

def attributive(adjective: str):
    ''' For a predicative adjective, returns the attributive form (lowercase).
        In Dutch, the attributive is formed with -e: "fel" => "felle kritiek".
    '''

    w = adjective.lower()
    if w in adjective_attributive:
        return adjective_attributive[w]
    if w.endswith("e"):
        return w
    if w.endswith(("er","st")) and len(w) > 4:
        return w + "e"
    if w.endswith("ees"):
        return w[:-2] + w[-1] + "e"
    if w.endswith("el") and len(w) > 2 and not is_vowel(w[-3]):
        return w + "e"
    if w.endswith("ig"):
        return w + "e"
    if len(w) > 2 and (not is_vowel(w[-1]) and is_vowel(w[-2]) and is_vowel(w[-3]) or w[:-1].endswith("ij")):
        if w.endswith("f"): w = w[:-1] + "v"
        if w.endswith("s"): w = w[:-1] + "z"
        if w[-2] == w[-3]:
            w = w[:-2] + w[-1]
    elif len(w) > 1 and is_vowel(w[-2]) and w.endswith(tuple("bdfgklmnprst")):
        w = w + w[-1]
    return w + "e"

def predicative(adjective: str):
    """ Returns the predicative adjective (lowercase).
        In Dutch, the attributive form preceding a noun is common:
        "rake opmerking" => "raak", "straffe uitspraak" => "straf", "dwaze blik" => "dwaas".
    """
    w = adjective.lower()
    if w in adjective_predicative:
        return adjective_predicative[w]
    if w.endswith("ste"):
        return w[:-1]
    if w.endswith("ere"):
        return w[:-1]
    if w.endswith("bele"):
        return w[:-1]
    if w.endswith("le") and len(w) > 2 and is_vowel(w[-3]) and not w.endswith(("eule", "oele")):
        return w[:-2] + w[-3] + "l"
    if w.endswith("ve") and len(w) > 2 and is_vowel(w[-3]) and not w.endswith(("euve", "oeve", "ieve")):
        return w[:-2] + w[-3] + "f"
    if w.endswith("ze") and len(w) > 2 and is_vowel(w[-3]) and not w.endswith(("euze", "oeze", "ieze")):
        return w[:-2] + w[-3] + "s"
    if w.endswith("ve"):
        return w[:-2] + "f"
    if w.endswith("ze"):
        return w[:-2] + "s"
    if w.endswith("e") and len(w) > 2:
        if not is_vowel(w[-2]) and w[-2] == w[-3]:
            return w[:-2]
        if len(w) > 3 and not is_vowel(w[-2]) and is_vowel(w[-3]) and w[-3] != "i" and not is_vowel(w[-4]):
            return w[:-2] + w[-3] + w[-2]
        return w[:-1]
    return w

def lemmaGetter(token):
    if (token.pos == 83) & (re.search('vervneut__Case=Nom',token.tag_) is not None):
        lemma = predicative(token.lemma_)
        if re.search('Degree=Sup',token.tag_) is not None:
            if lemma.endswith('st'):
                return lemma[:-2]
        elif re.search('Degree=Cmp',token.tag_) is not None:
            if lemma.endswith('r'):
                return predicative(lemma[:-1])
        return lemma
    else:
        lemma = token.lemma_
        if re.search('Degree=Sup',token.tag_) is not None:
            if lemma.endswith('st'):
                return lemma[:-2]
        elif re.search('Degree=Cmp',token.tag_) is not None:
            if lemma.endswith('r'):
                return predicative(lemma[:-1])
        return lemma