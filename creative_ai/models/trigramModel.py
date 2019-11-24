from creative_ai.utils.print_helpers import ppGramJson

class TrigramModel():

    def __init__(self):
        """
        Requires: nothing
        Modifies: self (this instance of the NGramModel object)
        Effects:  This is the NGramModel constructor. It sets up an empty
                  dictionary as a member variable.

        This function is done for you.
        """

        self.nGramCounts = {}

    def __str__(self):
        """
        Requires: nothing
        Modifies: nothing
        Effects:  Returns the string to print when you call print on an
                  NGramModel object. This string will be formatted in JSON
                  and display the currently trained dataset.

        This function is done for you.
        """

        return ppGramJson(self.nGramCounts)


###############################################################################
# Begin Core >> FOR CORE IMPLEMENTION, DO NOT EDIT ABOVE OF THIS SECTION <<
###############################################################################

    def trainModel(self, text):
        """
        Requires: text is a list of lists of strings
        Modifies: self.nGramCounts, a three-dimensional dictionary. For
                  examples and pictures of the TrigramModel's version of
                  self.nGramCounts, see the spec.
        Effects:  this function populates the self.nGramCounts dictionary,
                  which has strings as keys and dictionaries as values,
                  where those inner dictionaries have strings as keys
                  and dictionaries of {string: integer} pairs as values.
                  Returns self.nGramCounts
        """
        for list in text:
            for word in list:
                i = list.index(word)
                if i < len(list) - 2:
                    if list[i] in self.nGramCounts:
                        if list[i + 1] in self.nGramCounts[list[i]]:
                            if list[i + 2] in self.nGramCounts[list[i]][list[i + 1]]:
                                self.nGramCounts[list[i]][list[i + 1]][list[i + 2]] += 1
                            else:
                                self.nGramCounts[list[i]][list[i + 1]][list[i + 2]] = 1
                        else:
                            self.nGramCounts[list[i]][list[i + 1]] = {list[i + 2] : 1}
                    else:
                        self.nGramCounts[list[i]] = {list[i + 1]: {list[i + 2]: 1}}

        return self.nGramCounts

    def trainingDataHasNGram(self, sentence):
        """
        Requires: sentence is a list of strings
        Modifies: nothing
        Effects:  returns True if this n-gram model can be used to choose
                  the next token for the sentence. For explanations of how this
                  is determined for the TrigramModel, see the spec.
        """
        if sentence[-1] in self.nGramCounts:
            if sentence[-2] in self.nGramCounts[sentence[-1]]:
                return True
        return False


    def getCandidateDictionary(self, sentence):
        """
        Requires: sentence is a list of strings, and trainingDataHasNGram
                  has returned True for this particular language model
        Modifies: nothing
        Effects:  returns the dictionary of candidate next words to be added
                  to the current sentence. For details on which words the
                  TrigramModel sees as candidates, see the spec.
        """
        return self.nGramCounts[sentence[-2]][sentence[-1]]

###############################################################################
# End Core
###############################################################################

###############################################################################
# Main
###############################################################################

if __name__ == '__main__':
    # An example trainModel test case
    uni = TrigramModel()

    text1 = [ ['the', 'brown', 'fox']]
    uni.trainModel(text1)

    text = [ ['the', 'brown', 'fox', 'fled'], ['the', 'lazy', 'dog'] ]
    uni.trainModel(text)

    print(uni)

    sentence = ['he', 'smelled', 'the', 'brown']
    print(uni.getCandidateDictionary(sentence))
