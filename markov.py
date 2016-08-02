import random
#import io
#import json

class Markov:
	vocab = {}
	words = []
	def readText(txt):
		txt = txt.split()
		for i in range(len(txt) - 1):
			try:
				Markov.vocab[txt[i]].append(txt[i + 1])
			except:
				Markov.vocab[txt[i]] = [txt[i + 1]]
			Markov.words.append(txt[i])
			
				
	def writeText(n = 100):
		text = [random.choice(Markov.words)]
		n -= 1
		try:
			for i in range(n):
				tmp = Markov.vocab[text[i]]
				text.append(random.choice(tmp))
		except KeyError:
			print("Just a key error, nothing to see here!")
		return " ".join(text)

if __name__ == "__main__":
	text = """test"""
	Markov.readText(text)
	print(Markov.writeText())
#test
