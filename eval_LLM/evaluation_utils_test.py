import argparse
from evaluation_utils import cal_scores
from transformers import AutoTokenizer


def evaluate_with_params(tokenizer_path, gold_file, pred_file):
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    
    # Calculate scores
    corpus_bleu, bleu1, bleu2, bleu3, bleu4, rouge1, rouge2, rougel, precision, recall, f1 = cal_scores(
        tokenizer, 
        gold_file, 
        pred_file
    )
    
    results = {
        'corpus_bleu': corpus_bleu,
        'bleu1': bleu1,
        'bleu2': bleu2,
        'bleu3': bleu3,
        'bleu4': bleu4,
        'rouge1': rouge1,
        'rouge2': rouge2,
        'rougel': rougel,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
    
    return results


def print_results(results):
    """Print evaluation results in a formatted way"""
    print("=" * 50)
    print("EVALUATION RESULTS")
    print("=" * 50)
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


def main():
    parser = argparse.ArgumentParser(description='Evaluate model predictions using BLEU, ROUGE, and F1 metrics')
    
    parser.add_argument('--tokenizer_path', type=str, required=True,
                        help='Path to the GraphCodeBERT tokenizer')
    parser.add_argument('--gold_file', type=str, required=True,
                        help='Path to the gold reference file')
    parser.add_argument('--pred_file', type=str, required=True,
                        help='Path to the prediction file')
    
    args = parser.parse_args()
    
    # Evaluate with parameters
    results = evaluate_with_params(args.tokenizer_path, args.gold_file, args.pred_file)
    
    # Print results
    print_results(results)


if __name__ == "__main__":
    main()