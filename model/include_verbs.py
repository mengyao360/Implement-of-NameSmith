import spacy

nlp = spacy.load("en_core_web_sm")

def best_t(preds, tokenizer):
    beams_with_verbs = []
    for i, beam in enumerate(preds):
        t = beam.cpu().numpy().tolist()
        if 0 in t:
            t = t[:t.index(0)]

        token_texts = tokenizer.convert_ids_to_tokens(t)

        has_verb = False
        for tok_str in token_texts:
            doc = nlp(tok_str)
            if any(tok.pos_ == "VERB" for tok in doc):
                has_verb = True
                break
            
        text = tokenizer.decode(t, clean_up_tokenization_spaces=False)


        if has_verb:
            beams_with_verbs.append(t)

    if beams_with_verbs:
        return beams_with_verbs[0]
    else:
        t = preds[0].cpu().numpy().tolist()
        if 0 in t:
            t = t[:t.index(0)]
        return t
