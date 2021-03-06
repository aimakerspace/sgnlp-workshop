import logging
import os
from collections import Counter, OrderedDict

import torch
import torchtext.vocab

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"


class CustomSaPreprocessor:
    def __init__(self, vocab, tokenizer=None, seq_len=100):

        self.vocab = vocab
        self.seq_len = seq_len

        if tokenizer is not None:
            self.tokenizer = tokenizer
        else:
            try:
                import nltk

                self.tokenizer = nltk.word_tokenize
            except ModuleNotFoundError:
                logging.error(
                    "The package 'nltk' is not installed. Install it to use the word tokenizer."
                )

    def __call__(self, sentences):
        pad_token = self.vocab[PAD_TOKEN]

        tokenized_ids_sentences = []
        for sentence in sentences:
            tokenized_sentence = self.tokenizer(sentence)
            tokenized_ids_sentence = [self.vocab[word] for word in tokenized_sentence]
            if len(tokenized_sentence) < self.seq_len:
                # do padding
                tokenized_ids_sentence = [pad_token] * (
                    self.seq_len - len(tokenized_ids_sentence)
                ) + tokenized_ids_sentence
            else:
                tokenized_ids_sentence = tokenized_ids_sentence[: self.seq_len]
            tokenized_ids_sentences.append(tokenized_ids_sentence)
        return torch.IntTensor(tokenized_ids_sentences)

    @staticmethod
    def build_vocab(sentences, tokenizer, vocab_size):
        corpus = Counter()
        for sentence in sentences:
            tokenized_sentence = tokenizer(sentence)
            corpus.update(tokenized_sentence)

        # Total vocab size includes <pad> and <unk>
        od = OrderedDict()
        od[PAD_TOKEN] = 1
        od[UNK_TOKEN] = 1
        most_common = corpus.most_common(vocab_size - 2)
        for token, count in most_common:
            od[token] = count
        vocab = torchtext.vocab.vocab(od)
        vocab.set_default_index(1)

        return vocab

    @staticmethod
    def save_vocab(vocab, output_dir):
        torch.save(vocab, os.path.join(output_dir, "vocab.pt"))
