#!/usr/bin/env python
import sys

sys.dont_write_bytecode = True  # Suppress .pyc files

import random

import pysynth_e
import numpy
from creative_ai.utils.menu import Menu
from creative_ai.data.dataLoader import *
from creative_ai.models.musicInfo import *
from creative_ai.models.languageModel import LanguageModel
from creative_ai.plotly.makeChart import *
from creative_ai.reddit.writePosts import *

# FIXME Add your team name
TEAM = 'Garden Man'
LYRICSDIRS = ['the_beatles']
TESTLYRICSDIRS = ['the_beatles_test']
MUSICDIRS = ['kirby']
WAVDIR = 'creative_ai/wav/'


def output_models(val, output_fn=None):
    """
    Requires: nothing
    Modifies: nothing
    Effects:  outputs the dictionary val to the given filename. Used
              in Test mode.

    This function has been done for you.
    """
    from pprint import pprint
    if output_fn == None:
        print("No Filename Given")
        return
    with open('TEST_OUTPUT/' + output_fn, 'wt') as out:
        pprint(val, stream=out)


def sentenceTooLong(desiredLength, currentLength):
    """
    Requires: nothing
    Modifies: nothing
    Effects:  returns a bool indicating whether or not this sentence should
              be ended based on its length.

    This function has been done for you.
    """
    STDEV = 1
    val = random.gauss(currentLength, STDEV)
    return val > desiredLength


def printSongLyrics(verseOne, verseTwo, chorus):
    """
    Requires: verseOne, verseTwo, and chorus are lists of lists of strings
    Modifies: nothing
    Effects:  prints the song.

    This function is done for you.
    """
    verses = [verseOne, chorus, verseTwo, chorus]

    print()
    for verse in verses:
        for line in verse:
            print((' '.join(line)).capitalize())
        print()


def trainLyricModels(lyricDirs, test=False):
    """
    Requires: lyricDirs is a list of directories in data/lyrics/
    Modifies: nothing
    Effects:  loads data from the folders in the lyricDirs list,
              using the pre-written DataLoader class, then creates an
              instance of each of the NGramModel child classes and trains
              them using the text loaded from the data loader. The list
              should be in tri-, then bi-, then unigramModel order.
              Returns the list of trained models.

    This function is done for you.
    """
    model = LanguageModel()

    for ldir in lyricDirs:
        lyrics = prepData(loadLyrics(ldir))
        model.updateTrainedData(lyrics)

    return model


def trainMusicModels(musicDirs):
    """
    Requires: musicDirs is a list of directories in data/midi/
    Modifies: nothing
    Effects:  works exactly as trainLyricsModels, except that
              now the dataLoader calls the DataLoader's loadMusic() function
              and takes a music directory name instead of an artist name.
              Returns a list of trained models in order of tri-, then bi-, then
              unigramModel objects.

    This function is done for you.
    """
    model = LanguageModel()

    for mdir in musicDirs:
        music = prepData(loadMusic(mdir))
        model.updateTrainedData(music)

    return model


def runLyricsGenerator(models):
    """
    Requires: models is a list of a trained nGramModel child class objects
    Modifies: nothing
    Effects:  generates a verse one, a verse two, and a chorus, then
              calls printSongLyrics to print the song out.
    """
    verseOne = []
    verseTwo = []
    chorus = []

    for _ in range(4):
        verseOne.append(generateTokenSentence(models, 7))
        verseTwo.append(generateTokenSentence(models, 7))
        chorus.append(generateTokenSentence(models, 9))

    printSongLyrics(verseOne, verseTwo, chorus)


def makeSongComponent(model, desiredBars):
    '''
    Requires: model is a single trained languageModel object.
              desiredBars is number of bars wanted for this componenet.
    Modifies: nothing.
    Returns: a sentence (music componenet) of desired length (measured in bars).
    '''
    # Create sentence with starting characters
    sentence = ["^::^", "^:::^"]
    currentBars = 0.0
    # Continue adding notes until it has desired amount of bars
    while True:
        sentence.append(model.getNextToken(sentence))
        # Don't want ending character in songs
        if sentence[-1] == "$:::$":
            sentence.pop()
            continue
        # Longer notes = smaller duration value
        currentNoteDuration = abs(1.0 / sentence[-1][1])
        currentBars += currentNoteDuration
        # Break if reached desiredBars
        if currentBars == desiredBars:
            break
        # Shorten final note exceeding desiredBars
        if currentBars > desiredBars:
            newDuration = 1.0 / (currentBars - desiredBars)
            replaceNote = (sentence[-1][0], newDuration)
            sentence[-1] = replaceNote
            break
    # Return sentence without starting characters
    return sentence[2:]


def buildupSong(source, sourceBars, magnitude=2):
    '''
    Requires: source is a list of pysynth tuples, sourceBars is the length of
              source measured in bars, magnitude is an integer
    Modifies: nothing
    Returns: A new song componenet of same length made by multiplying a portion
             of source
    '''
    # Create return list
    sentence = []
    currentBars = 0.0
    # Copy notes from source until sourceBars / magnitude
    desiredBars = sourceBars / magnitude
    for note in source:
        sentence.append(note)
        currentBars += abs(1.0 / note[1])
        if currentBars == desiredBars:
            break
        elif currentBars > sourceBars:
            newDuration = 1.0 / (currentBars - desiredBars)
            replaceNote = (sentence[-1][0], newDuration)
            sentence[-1] = replaceNote
            break
    # multiply sentence to match desired length (bars)
    sentence *= magnitude
    return sentence


def runMusicGenerator(models, songName):
    """
    Requires: models is a list of trained models
    Modifies: nothing
    Effects:  uses models to generate a song and write it to the file
              named songName.wav
    Returns:  the generated song as a list of tuples
    """
    verseOne = []  # 8 Bars
    verseTwo = []  # 8 Bars
    preChorus = []  # 7 Bars
    chorus = []  # 8 Bars

    # Reuse sentence: AABBCCBB
    A = makeSongComponent(models, 1)
    B = makeSongComponent(models, 1)
    C = makeSongComponent(models, 1)
    verseOne.extend(A * 2 + B * 2 + C * 2 + B * 2)
    # Reuse sentence: ABCB Motif: DDD-
    A = makeSongComponent(models, 1 / 2)
    B = makeSongComponent(models, 1 / 2)
    C = makeSongComponent(models, 1 / 2)
    D = makeSongComponent(models, 3 / 2)
    chorus.extend(D + A + D + B + D + C + D + B)
    # Reuse sentence: buildup over 8 bars
    A = (makeSongComponent(models, 1)) * 3
    B = buildupSong(A, 2)
    C = buildupSong(A, 1, 4)
    D = buildupSong(A, 1, 8)
    preChorus.extend(A + B + C + D)

    # Make song
    song = []
    song.extend(chorus)
    song.extend(verseOne)
    song.extend(preChorus)
    song.extend([("r", 8), ("d1", 16), ("c#1", 16), ("c1", 16), ("b1", 16), ("a#1", 16), ("a1", 16)])
    song.extend(chorus)

    pysynth_e.make_wav(song, fn=songName)

    return song


###############################################################################
# Begin Core >> FOR CORE IMPLEMENTION, DO NOT EDIT OUTSIDE OF THIS SECTION <<
###############################################################################

def generateTokenSentence(model, desiredLength):
    """
    Requires: model is a single trained languageModel object.
              desiredLength is the desired length of the sentence.
    Modifies: nothing
    Effects:  returns a list of strings where each string is a word in the
              generated sentence. The returned list should NOT include
              any of the special starting or ending symbols.

              For more details about generating a sentence using the
              NGramModels, see the spec.
    """
    # Create sentence with starting characters
    sentence = ["^::^", "^:::^"]
    # Continuously add new words until sentence needs to end
    while True:
        if sentence[-1] == "$:::$":
            break
        # Discount starting characters
        current_length = len(sentence) - 2
        if current_length >= desiredLength:
            break
        if sentenceTooLong(desiredLength, current_length):
            break
        # Add new word to sentence
        sentence.append(model.getNextToken(sentence))
    # Clear ending character if present
    if sentence[-1] == "$:::$":
        sentence.remove("$:::$")
    # Return sentence without starting characters
    return sentence[2:]


###############################################################################
# End Core
###############################################################################

###############################################################################
# Main
###############################################################################

PROMPT = [
    'Generate song lyrics by The Beatles',
    'Generate a song using data from Nintendo Gamecube or a library of your choice',
    'Generate a bot post of video game music *Limited to one post every 10 minutes*',
    'Quit the music generator'
]


def main():
    """
    Requires: Nothing
    Modifies: Nothing
    Effects:  This is your main function, which is done for you. It runs the
              entire generator program for both the reach and the core.

              It prompts the user to choose to generate either lyrics or music.
    """

    mainMenu = Menu(PROMPT)

    lyricsTrained = False
    musicTrained = False

    print('Welcome to the {} music generator!'.format(TEAM))
    while True:
        userInput = mainMenu.getChoice()

        if userInput == 1:
            if not lyricsTrained:
                print('Starting lyrics generator...')
                lyricsModel = trainLyricModels(LYRICSDIRS)
                lyricsTrained = True

            runLyricsGenerator(lyricsModel)

        elif userInput == 2:
            if not musicTrained:
                # Prompt user for music directories
                print("Please enter music directory(s) separated by a single comma: (default is Nintendo Gamecube)")
                userDirs = input().split(",")
                MUSICDIRS = []
                MUSICDIRS.extend(userDirs)
                if MUSICDIRS == []:
                    MUSICDIRS = ["gamecube"]

                print('Starting music generator...')
                musicModel = trainMusicModels(MUSICDIRS)
                musicTrained = True

            songName = input('What would you like to name your song? ')

            song = runMusicGenerator(musicModel, WAVDIR + songName + '.wav')

            choice = input("Would you like to see its bar graph? (y/n): ")
            if choice == "y":
                makeBarChart(song, WAVDIR, songName)
            choice = input("Would you like to see its synthesia? (y/n): ")
            if choice == "y":
                makeSynthesia(song, WAVDIR, songName)

        elif userInput == 3:
            reddit_write()

        elif userInput == 4:
            print('Thank you for using the {} music generator!'.format(TEAM))
            sys.exit()


# This is how python tells if the file is being run as main
if __name__ == '__main__':
    main()
    # note that if you want to individually test functions from this file,
    # you can comment out main() and call those functions here. Just make
    # sure to call main() in your final submission of the project!
