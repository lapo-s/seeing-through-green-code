This code was used to perform the NLP analysis. Specifically:

- *code_based_green.py* identify green patents as per standare classification (i.e. ENVTECH, y-tagging scheme and WIPO green inventory)
- *preprocessing_and_W2V.py* perform patents texts preprocessing and train the Word2Vec model, producing a list of expression from which we selected our baseline vocabulary expansion
- *match.py* perform our classification procedure on the subset of green patents extracted with *code_based_green.py*, and, separately, on the residual subset.
