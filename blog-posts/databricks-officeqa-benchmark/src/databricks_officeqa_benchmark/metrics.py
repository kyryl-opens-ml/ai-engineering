import re
import string
from collections import Counter


def normalize_answer(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def exact_match(ground_truth: str, prediction: str) -> float:
    return float(normalize_answer(ground_truth) == normalize_answer(prediction))


def f1_score(ground_truth: str, prediction: str) -> float:
    gt = normalize_answer(ground_truth).split()
    pred = normalize_answer(prediction).split()
    if not gt or not pred:
        return float(gt == pred)

    common = Counter(gt) & Counter(pred)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred)
    recall = num_same / len(gt)
    return 2 * precision * recall / (precision + recall)
