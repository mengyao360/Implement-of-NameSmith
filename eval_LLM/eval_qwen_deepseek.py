import argparse
import json

import sacrebleu
from rouge_score import rouge_scorer
from transformers import RobertaTokenizer


def load_results(result_file):
    golds = []
    preds = []

    with open(result_file, "r", encoding="utf-8") as file_obj:
        for line_num, line in enumerate(file_obj, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                print(f"Skip invalid JSON on line {line_num}")
                continue

            gold = str(data.get("method_name", "")).strip()
            pred = str(data.get("prediction", "")).strip()

            if not gold:
                continue

            golds.append(gold)
            preds.append(pred)

    return golds, preds


def write_lines(lines, output_file):
    with open(output_file, "w", encoding="utf-8") as file_obj:
        for line in lines:
            file_obj.write(f"{line}\n")


def cal_scores_from_lists(tokenizer, golds, preds):
    assert len(golds) == len(preds), "Gold and prediction files must have the same number of lines."

    corpus_bleu = _bleu_corpus(tokenizer, golds, preds)
    bleu1, bleu2, bleu3, bleu4 = _bleu_ngrams(tokenizer, golds, preds)
    rouge1, rouge2, rougel = _rouge(tokenizer, golds, preds)

    results = [(tokenizer.tokenize(gold), tokenizer.tokenize(pred)) for gold, pred in zip(golds, preds)]
    results = [
        (
            gold_tokens,
            pred_tokens or ([""] * len(gold_tokens)),
        )
        for gold_tokens, pred_tokens in results
    ]
    precision, recall, f1 = _f1(results)

    exact_match = _exact_match(golds, preds)

    return {
        "count": len(golds),
        "exact_match": round(exact_match, 4),
        "corpus_bleu": round(corpus_bleu, 4),
        "bleu1": round(bleu1, 4),
        "bleu2": round(bleu2, 4),
        "bleu3": round(bleu3, 4),
        "bleu4": round(bleu4, 4),
        "rouge1": round(rouge1, 4),
        "rouge2": round(rouge2, 4),
        "rougel": round(rougel, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def _exact_match(golds, preds):
    matched = 0
    for gold, pred in zip(golds, preds):
        if gold.strip() == pred.strip():
            matched += 1
    return matched / len(golds) if golds else 0.0


def _bleu_corpus(tokenizer, golds, preds):
    tokenized_golds = []
    tokenized_preds = []

    for gold in golds:
        tokenized_golds.append(" ".join(tokenizer.tokenize(gold)))

    for pred in preds:
        tokenized_preds.append(" ".join(tokenizer.tokenize(pred)))

    return sacrebleu.corpus_bleu(tokenized_preds, [tokenized_golds]).score / 100


def _bleu_ngrams(tokenizer, golds, preds):
    tokenized_golds = []
    tokenized_preds = []

    for gold in golds:
        tokenized_golds.append(" ".join(tokenizer.tokenize(gold)))

    for pred in preds:
        tokenized_preds.append(" ".join(tokenizer.tokenize(pred)))

    bleu1 = sacrebleu.BLEU(max_ngram_order=1).corpus_score(tokenized_preds, [tokenized_golds]).score / 100
    bleu2 = sacrebleu.BLEU(max_ngram_order=2).corpus_score(tokenized_preds, [tokenized_golds]).score / 100
    bleu3 = sacrebleu.BLEU(max_ngram_order=3).corpus_score(tokenized_preds, [tokenized_golds]).score / 100
    bleu4 = sacrebleu.BLEU(max_ngram_order=4).corpus_score(tokenized_preds, [tokenized_golds]).score / 100

    return bleu1, bleu2, bleu3, bleu4


def _rouge(tokenizer, golds, preds):
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = {"rouge1": [], "rouge2": [], "rougeL": []}

    for gold, pred in zip(golds, preds):
        tokenized_gold = " ".join(tokenizer.tokenize(gold))
        tokenized_pred = " ".join(tokenizer.tokenize(pred))

        score = scorer.score(tokenized_gold.strip(), tokenized_pred.strip())
        scores["rouge1"].append(score["rouge1"].fmeasure)
        scores["rouge2"].append(score["rouge2"].fmeasure)
        scores["rougeL"].append(score["rougeL"].fmeasure)

    rouge1_avg = sum(scores["rouge1"]) / len(scores["rouge1"])
    rouge2_avg = sum(scores["rouge2"]) / len(scores["rouge2"])
    rouge_l_avg = sum(scores["rougeL"]) / len(scores["rougeL"])

    return rouge1_avg, rouge2_avg, rouge_l_avg


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
    true_positive, false_positive, false_negative = 0, 0, 0

    for original_name, predicted in results:
        filtered_predicted_names = predicted
        filtered_original_subtokens = original_name

        if "".join(filtered_original_subtokens) == "".join(filtered_predicted_names):
            true_positive += len(filtered_original_subtokens)
            continue

        for subtok in filtered_predicted_names:
            if subtok in filtered_original_subtokens:
                true_positive += 1
            else:
                false_positive += 1

        for subtok in filtered_original_subtokens:
            if subtok not in filtered_predicted_names:
                false_negative += 1

    return true_positive, false_positive, false_negative


def print_results(results):
    print("=" * 50)
    print("EVALUATION RESULTS")
    print("=" * 50)
    print(f"Count: {results['count']}")
    print(f"Exact Match: {results['exact_match']}")
    print(f"Corpus BLEU: {results['corpus_bleu']}")
    print(f"BLEU-1: {results['bleu1']}")
    print(f"BLEU-2: {results['bleu2']}")
    print(f"BLEU-3: {results['bleu3']}")
    print(f"BLEU-4: {results['bleu4']}")
    print("-" * 30)
    print(f"ROUGE-1: {results['rouge1']}")
    print(f"ROUGE-2: {results['rouge2']}")
    print(f"ROUGE-L: {results['rougel']}")
    print("-" * 30)
    print(f"Precision: {results['precision']}")
    print(f"Recall: {results['recall']}")
    print(f"F1: {results['f1']}")
    print("=" * 50)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate method-name predictions using BLEU, ROUGE, Exact Match, and F1 metrics."
    )
    parser.add_argument(
        "--tokenizer_path",
        type=str,
        required=True,
        help="Path to the GraphCodeBERT tokenizer",
    )
    parser.add_argument(
        "--result_file",
        type=str,
        required=True,
        help="Path to the JSONL result file",
    )
    parser.add_argument(
        "--gold_output",
        type=str,
        default=None,
        help="Optional path to save extracted gold references",
    )
    parser.add_argument(
        "--pred_output",
        type=str,
        default=None,
        help="Optional path to save extracted predictions",
    )
    parser.add_argument(
        "--save_json",
        type=str,
        default=None,
        help="Optional path to save evaluation metrics as JSON",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    tokenizer = RobertaTokenizer.from_pretrained(args.tokenizer_path)
    golds, preds = load_results(args.result_file)

    if not golds:
        raise ValueError(f"No valid results found in {args.result_file}")

    results = cal_scores_from_lists(tokenizer, golds, preds)

    if args.gold_output:
        write_lines(golds, args.gold_output)

    if args.pred_output:
        write_lines(preds, args.pred_output)

    if args.save_json:
        with open(args.save_json, "w", encoding="utf-8") as file_obj:
            json.dump(results, file_obj, ensure_ascii=False, indent=2)

    print_results(results)


if __name__ == "__main__":
    main()
