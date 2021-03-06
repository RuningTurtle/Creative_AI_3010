import random
from creative_ai.data.dataLoader import prepData
from creative_ai.models.unigramModel import UnigramModel
from creative_ai.models.bigramModel import BigramModel
from creative_ai.models.trigramModel import TrigramModel
from creative_ai.models.quadgramModel import QuadgramModel
from creative_ai.utils.print_helpers import key_value_pairs

class LanguageModel():

    def __init__(self, models=None):
        """
        Requires: nothing
        Modifies: self (this instance of the LanguageModel object)
        Effects:  This is the LanguageModel constructor. It sets up an empty
                  dictionary as a member variable.

        This function is done for you.
        """

        if models != None:
            self.models = models
        else:
            self.models = [QuadgramModel(), TrigramModel(), BigramModel(), UnigramModel()]

    def __str__(self):
        """
        Requires: nothing
        Modifies: nothing
        Effects:  This is a string overloaded. This function is
                  called when languageModel is printed.
                  It will show the number of trained paths
                  for each model it contains. It may be
                  useful for testing.

        This function is done for you.
        """

        output_list = [
            '{} contains {} trained paths.'.format(
                model.__class__.__name__, key_value_pairs(model.nGramCounts)
                ) for model in self.models
            ]

        output = '\n'.join(output_list)

        return output

    def updateTrainedData(self, text, prepped=True):
        """
        Requires: text is a 2D list of strings
        Modifies: self (this instance of the LanguageModel object)
        Effects:  adds new trained data to each of the languageModel models.
        If this data is not prepped (prepped==False) then it is prepepd first
        before being passed to the models.

        This function is done for you.
        """

        if (not prepped):
            text = prepData(text)

        for model in self.models:
            model.trainModel(text)


###############################################################################
# Begin Core >> FOR CORE IMPLEMENTION, DO NOT EDIT ABOVE OF THIS SECTION <<
###############################################################################

    def selectNGramModel(self, sentence):
        """
        Requires: self.models is a list of NGramModel objects sorted by descending
                  priority: tri-, then bi-, then unigrams.

                  sentence is a list of strings.
        Modifies: nothing
        Effects:  returns the best possible model that can be used for the
                  current sentence based on the n-grams that the models know.
                  (Remember that you wrote a function that checks if a model can
                  be used to pick a word for a sentence!)

        self sorts by tri-, bi-, unigrams
        sentence is a list of strings

        using n-grams, returns best model for current sentence
        use function that checks if a model can be used to pick a word for that sentence

        """

        if self.models[0].trainingDataHasNGram(sentence):
            return self.models[0]
        elif self.models[1].trainingDataHasNGram(sentence):
            return self.models[1]
        elif self.models[2].trainingDataHasNGram(sentence):
            return self.models[2]
        else:
            return self.models[3]

    def weightedChoice(self, candidates):
        """
        Requires: candidates is a dictionary; the keys of candidates are items
                  you want to choose from and the values are integers
        Modifies: nothing
        Effects:  returns a candidate item (a key in the candidates dictionary)
                  based on the algorithm described in the spec.

        choose things from a dictionary
        returns an item described by the algorithm from the spec

        """
        tokens = list(candidates.keys())
        cumulative_count = []
        for v in candidates.values():
            if (len(cumulative_count) == 0):
                # empty, first case
                cumulative_count.append(v)
            else:
                cumulative_count.append(v + cumulative_count[-1])
        rand_num = random.randrange(0, cumulative_count[-1])
        for i in range(len(cumulative_count)):
            if cumulative_count[i] > rand_num:
                return tokens[i]
        return "FIXME"

    def getNextToken(self, sentence, filter=None):
        """
        Requires: sentence is a list of strings, and this model can be used to
                  choose the next token for the current sentence
        Modifies: nothing
        Effects:  returns the next token to be added to sentence by calling
                  the getCandidateDictionary and weightedChoice functions.
                  For more information on how to put all these functions
                  together, see the spec.

                  If a filter is being used, and none of the models
                  can produce a next token using the filter, then a random
                  token from the filter is returned instead.

        sentence is list of strings
        this is used to choose the next token or word for the current sentence

        calls getCandidateDictionary and weightedChoice
        if filter is used, while no model produces a next token through the filter, filter chooses random token

        """
        # gives dictionary to use, whichever of the three models

        dict = self.selectNGramModel(sentence).getCandidateDictionary(sentence)

        # if self.selectNGramModel(sentence) == self.models[0]:
        #     Dictionary = self.models[0].getCandidateDictionary(sentence)
        # elif self.selectNGramModel(sentence) == self.models[1]:
        #     Dictionary = self.models[1].getCandidateDictionary(sentence)
        # elif self.selectNGramModel(sentence) == self.models[2]:
        #     Dictionary = self.models[2].getCandidateDictionary(sentence)
        # elif self.selectNGramModel(sentence) == self.models[3]:
        #     Dictionary = self.models[3].getCandidateDictionary(sentence)

        # returns a choice from weighted dictionary
        if filter == None:
            return self.weightedChoice(dict)

        # if there are strings in filter
        else:
            filtered_candidates = {fc: dict[fc] for fc in filter}
            # filteredCandidates = {}
            # for fc in filter:
            #     if index in filter:
            #         filteredCandidates[index] = value
        #if there are no items in filteredCandidates
            if filtered_candidates == {}:
                return random.choice(filter)
        #if there are items in filteredCandidates
            else:
                return self.weightedChoice(filtered_candidates)

###############################################################################
# End Core
###############################################################################

###############################################################################
# Main
###############################################################################

if __name__ == '__main__':
    # remove 'pass' before adding test cases

    testModel = LanguageModel()
    testDictionary1 = {'north': 4, 'south': 1, 'east': 3, 'west': 2}
    print(testModel.weightedChoice(testDictionary1))


    # test cases here
