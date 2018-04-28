import json
import io
import random
import numpy


class NewMarkov:

    def __init__(self):
        self.words = {} # {word: {word: prob}}
        try:
            self.words_file = open("words.json", "+r")
            try:
                self.words = json.load(self.words_file)
            except json.JSONDecodeError:
                print("File empty!")

        except FileNotFoundError:
            self.words_file = open("words.json", "+w")

    def read(self, text):
        txt = text.split()
        for i in range(len(txt) - 1):
            if txt[i] in self.words:
                if txt[i + 1] in self.words[txt[i]]:
                    self.words[txt[i]][txt[i + 1]] += 1
                else:
                    self.words[txt[i]][txt[i + 1]] = 1
            else:
                self.words[txt[i]] = {}
                self.words[txt[i]][txt[i+1]] = 1

    def write(self, n=10):
        text = [random.choice(list(self.words.keys()))]
        n -= 1
        for i in range(n):
            if text[i] in self.words:
                wordlist = list(self.words[text[i]].keys())
                counts = list(self.words[text[i]].values())
                sum = 0
                for all in counts:
                    sum += all
                for i in range(len(counts)):
                    counts[i] /= sum
                word = numpy.random.choice(wordlist, p=counts)
                text.append(word)
            else:
                text.append(random.choice(list(self.words.keys())))
        return " ".join(text)

    def save(self):
        self.words_file.flush()
        json.dump(self.words, self.words_file)

if __name__ == "__main__":
    mk = NewMarkov()
    mk.read("this is a test")
    mk.save()
    print(mk.write(10))
    mk.words_file.close()