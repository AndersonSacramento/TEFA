from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn



def is_event(frame):
    if frame and frame.name == 'Event':
        return frame
    elif frame:
        for rel in filter_inheritance(frame):
            parcial_r = is_event(rel.Parent)
            if parcial_r:
                return parcial_r

def filter_inheritance(frame):
    return [rel for rel in frame.frameRelations if rel.type.name == 'Inheritance' and frame.name == rel.Child.name]

def filter_core_fe(frame):
    return [fe for fe in frame.FE.values() if fe.coreType == 'Core']



def fn_to_wn_pos(notation):
    return {'n': wn.NOUN,
            'v': wn.VERB,
            'a': wn.ADJ }.get(notation, notation)

def get_lemma_from_lexunit_name(lexunit_name, lang='por'):
    name, pos = lexunit_name.split('.')
    pos = fn_to_wn_pos(pos)
    try:
        return {name for lemma in wn.synsets(name, pos) for name in lemma.lemma_names(lang=lang)}
    except KeyError:
        return {}


def lemma_frames(lang='por'):
    for frame in fn.frames():
        if not is_event(frame): continue
        for lexunit in frame.lexUnit.values():
            print(lexunit.name)
            _ , pos = lexunit.name.split('.')
            pos = fn_to_wn_pos(pos)
            for lemma_name in get_lemma_from_lexunit_name(lexunit.name, lang=lang):
                yield LemmaFN(lexunitid=lexunit.ID,
                              lemma=lemma_name,
                              pos=pos,
                              frameid=frame.ID,
                              lang=lang)
                # {'lexunit_id': lexunit.ID,
                #  'lemma_name': lemma_name,
                #  'pos': pos,
                #  'fn_id': frame.ID,
                #  'lang': lang}
                
