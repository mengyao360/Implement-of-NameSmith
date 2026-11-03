from collections import Counter
import sacrebleu
from rouge_score import rouge_scorer

def cal_scores(tokenizer, gold_file, pred_file):
    with open(gold_file, 'r', encoding='utf-8') as f:
        golds = [line.strip() for line in f.readlines()]
    with open(pred_file, 'r', encoding='utf-8') as f:
        preds = [line.strip() for line in f.readlines()]
    assert len(golds) == len(preds), "Gold and prediction files must have the same number of lines."

    # cal corpus bleu with tokenizer
    corpus_bleu = _bleu_corpus(tokenizer, golds, preds)
    
    # cal bleu1, bleu2, bleu3, bleu4 with tokenizer
    bleu1, bleu2, bleu3, bleu4 = _bleu_ngrams(tokenizer, golds, preds)

    # cal rouge with tokenizer
    rouge1, rouge2, rougel = _rouge(tokenizer, golds, preds)

    results = [(tokenizer.tokenize(gold), tokenizer.tokenize(pred)) for gold, pred in zip(golds, preds)]
    results = [
        (
            gold_tokens, 
            pred_tokens or ([''] * len(gold_tokens))
        ) 
        for gold_tokens, pred_tokens in results
    ]
    precision, recall, f1 = _f1(results)

    return (
        round(corpus_bleu, 4),
        round(bleu1, 4),
        round(bleu2, 4),
        round(bleu3, 4),
        round(bleu4, 4),
        round(rouge1, 4),
        round(rouge2, 4),
        round(rougel, 4),
        round(precision, 4),
        round(recall, 4),
        round(f1, 4)
    )

def _bleu_corpus(tokenizer, golds, preds):
    # Tokenize using GraphCodeBERT tokenizer and rejoin with spaces
    tokenized_golds = []
    tokenized_preds = []
    
    for gold in golds:
        tokens = tokenizer.tokenize(gold)
        # Join tokens with space to create tokenized string
        tokenized_gold = ' '.join(tokens)
        tokenized_golds.append(tokenized_gold)
    
    for pred in preds:
        tokens = tokenizer.tokenize(pred)
        # Join tokens with space to create tokenized string
        tokenized_pred = ' '.join(tokens)
        tokenized_preds.append(tokenized_pred)
    
    return sacrebleu.corpus_bleu(tokenized_preds, [tokenized_golds]).score / 100


def _bleu_ngrams(tokenizer, golds, preds):
    # Tokenize using GraphCodeBERT tokenizer and rejoin with spaces
    tokenized_golds = []
    tokenized_preds = []
    
    for gold in golds:
        tokens = tokenizer.tokenize(gold)
        # Join tokens with space to create tokenized string
        tokenized_gold = ' '.join(tokens)
        tokenized_golds.append(tokenized_gold)
    
    for pred in preds:
        tokens = tokenizer.tokenize(pred)
        # Join tokens with space to create tokenized string
        tokenized_pred = ' '.join(tokens)
        tokenized_preds.append(tokenized_pred)
    
    # Calculate BLEU-1, BLEU-2, BLEU-3, BLEU-4 
    bleu1 = sacrebleu.BLEU(max_ngram_order=1).corpus_score(tokenized_preds, [tokenized_golds]).score / 100
    bleu2 = sacrebleu.BLEU(max_ngram_order=2).corpus_score(tokenized_preds, [tokenized_golds]).score / 100
    bleu3 = sacrebleu.BLEU(max_ngram_order=3).corpus_score(tokenized_preds, [tokenized_golds]).score / 100
    bleu4 = sacrebleu.BLEU(max_ngram_order=4).corpus_score(tokenized_preds, [tokenized_golds]).score / 100
    
    return bleu1, bleu2, bleu3, bleu4


def _rouge(tokenizer, golds, preds):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
    
    for gold, pred in zip(golds, preds):
        # Tokenize using GraphCodeBERT tokenizer
        gold_tokens = tokenizer.tokenize(gold)
        pred_tokens = tokenizer.tokenize(pred)
        
        # Join tokens with space to create tokenized strings
        tokenized_gold = ' '.join(gold_tokens)
        tokenized_pred = ' '.join(pred_tokens)
        
        score = scorer.score(tokenized_gold.strip(), tokenized_pred.strip())
        scores['rouge1'].append(score['rouge1'].fmeasure)
        scores['rouge2'].append(score['rouge2'].fmeasure)
        scores['rougeL'].append(score['rougeL'].fmeasure)
    
    rouge1_avg = sum(scores['rouge1']) / len(scores['rouge1'])
    rouge2_avg = sum(scores['rouge2']) / len(scores['rouge2'])
    rougeL_avg = sum(scores['rougeL']) / len(scores['rougeL'])
    
    return rouge1_avg, rouge2_avg, rougeL_avg


def _f1(results):
    true_positive, false_positive, false_negative = update_per_subtoken_statistics(results)

    if true_positive + false_positive > 0:
        precision = true_positive / (true_positive + false_positive)
    else:
        precision = 0
    if true_positive + false_negative > 0:
        recall = true_positive / (true_positive + false_negative)
    else:
        recall = 0
    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0
    return precision, recall, f1

def update_per_subtoken_statistics(results):
    true_positive, false_positive, false_negative=0,0,0
    for original_name, predicted in results:
        filtered_predicted_names = predicted
        filtered_original_subtokens = original_name

        if ''.join(filtered_original_subtokens) == ''.join(filtered_predicted_names):
            true_positive += len(filtered_original_subtokens)
            continue

        for subtok in filtered_predicted_names:
            if subtok in filtered_original_subtokens:
                true_positive += 1
            else:
                false_positive += 1
        for subtok in filtered_original_subtokens:
            if not subtok in filtered_predicted_names:
                false_negative += 1

    return true_positive, false_positive, false_negative