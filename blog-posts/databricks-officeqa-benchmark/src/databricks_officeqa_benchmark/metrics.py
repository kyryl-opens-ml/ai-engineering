import re
import string
from collections import Counter


_ARTICLES_RE = re.compile(r"\b(a|an|the)\b", re.IGNORECASE)


def normalize_answer(text: str) -> str:
    text = text.strip().lower()
    text = _ARTICLES_RE.sub(" ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def exact_match(ground_truth: str, prediction: str) -> float:
    return float(normalize_answer(ground_truth) == normalize_answer(prediction))


def f1_score(ground_truth: str, prediction: str) -> float:
    gt_tokens = normalize_answer(ground_truth).split()
    pred_tokens = normalize_answer(prediction).split()
    if not gt_tokens and not pred_tokens:
        return 1.0
    if not gt_tokens or not pred_tokens:
        return 0.0

    common = Counter(gt_tokens) & Counter(pred_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gt_tokens)
    return 2 * precision * recall / (precision + recall)


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0
