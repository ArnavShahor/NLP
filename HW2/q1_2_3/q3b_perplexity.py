"""
Q3(b): perplexity of the Word-Level Neural Bi-gram LM (Section 1) on the
Wikipedia and Shakespeare passages.

Reuses the trained parameters from saved_params_40000.npy and the existing
eval_neural_lm function in q1d_neural_lm.py. Run from the q1_2_3 directory:

    python q3b_perplexity.py
"""

import numpy as np
import pandas as pd

from data_utils import utils
import q1d_neural_lm

VOCAB_PATH = "data/lm/vocab.ptb.txt"
SAVED_PARAMS_PATH = "saved_params_40000.npy"
WIKIPEDIA_PATH = "wikipedia_pos_fromat.txt"
SHAKESPEARE_PATH = "shakespare_pos_fromat.txt"

VOCAB_SIZE = 2000
INPUT_DIM = 50
HIDDEN_DIM = 50


def main():
    vocab = pd.read_table(
        VOCAB_PATH,
        header=None, sep=r"\s+", index_col=0,
        names=["count", "freq"],
    )
    num_to_word = dict(enumerate(vocab.index[:VOCAB_SIZE]))
    word_to_num = utils.invert_dict(num_to_word)
    num_to_word_embedding = q1d_neural_lm.load_vocab_embeddings()

    dimensions = [INPUT_DIM, HIDDEN_DIM, VOCAB_SIZE]
    params = np.load(SAVED_PARAMS_PATH)

    # eval_neural_lm reads these as module-level globals; set them before calling.
    q1d_neural_lm.word_to_num = word_to_num
    q1d_neural_lm.num_to_word_embedding = num_to_word_embedding
    q1d_neural_lm.params = params
    q1d_neural_lm.dimensions = dimensions

    wiki_ppl = q1d_neural_lm.eval_neural_lm(WIKIPEDIA_PATH)
    shakespeare_ppl = q1d_neural_lm.eval_neural_lm(SHAKESPEARE_PATH)

    print("Word-Level Neural Bi-gram (Section 1) perplexity:")
    print(f"  Wikipedia:   {wiki_ppl:.4f}")
    print(f"  Shakespeare: {shakespeare_ppl:.4f}")


if __name__ == "__main__":
    main()
