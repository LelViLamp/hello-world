import nltk
from langdetect import detect
from nltk.tokenize import sent_tokenize


# sample texts for language detection and sentence splitting
sample_texts = [
    # https://www.stupidedia.org/stupi/Python_(Programmiersprache)
    """Python ist eine Programmiersprache die schon lange mit C++ konkurriert. Sie wurde in C (Programmiersprache) realisiert. Im Gegensatz zu C++ ist Python nämlich eine verwendbare Sprache, da sie ohne Präprozessor auskommt. Die Entwurfsphilosphie ist es, möglichst unleserlichen Quellcode erstellen zu können. Python wurde von Monty Python entwickelt und nach der Schlange benannt. Python enthält so viele eingebaute Funktionen, dass es 3 Jahre dauert ein einzelnes Programm das in Python geschrieben wurde zu starten. Python ist Open Source und hat schon Level 13.
    Python wurde entworfen, um den Funktionsumfang moderner Programmiersprachen mit der Unleserlichkeit von Brainfuck zu verbinden. Allerdings ist Python damit nicht ganz erfolgreich, da der Funktionsumfang von Jahr zu Jahr kleiner wird. Daher sollte man keine Module einbinden, da diese schon im nächsten Monat einfach verschwunden sein können. Python hat außerdem Typen, im Gegensatz zu Brainfuck, aber keine Typüberprüfung. Damit ist es leichter Fehler zu erzeugen als im Konkurrenzprodukt C++.""",

    # https://en.wikipedia.org/wiki/Python_(programming_language)
    """Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including structured (particularly procedural), object-oriented and functional programming. It is often described as a "batteries included" language due to its comprehensive standard library. Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language and first released it in 1991 as Python 0.9.0. Python 2.0 was released in 2000. Python 3.0, released in 2008, was a major revision not completely backward-compatible with earlier versions. Python 2.7.18, released in 2020, was the last release of Python 2. Python consistently ranks as one of the most popular programming languages, and has gained widespread use in the machine learning community.""",
]

# German sentence splitters
nltk.download('punkt')
nltk.download('punkt_tab')

language_names = {'de': 'german', 'en': 'english'}

for index, text in enumerate(sample_texts):
    language_short = detect(text)
    if language_short not in language_names:
        continue
    language_long = language_names[language_short]
    print(f"Text #{index} is in '{language_short}' --> '{language_long}'")
    sentences = sent_tokenize(text, language=language_long)
    print(sentences)
