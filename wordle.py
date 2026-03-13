
import csv
import numpy as np
import random

valid_solutions = []
letterCount = {}
totalLetters = 0


with open("valid_solutions.csv", "r") as vs_file:
  for row in vs_file:
    word = row.strip().lower()
    if len(word) == 5:
      valid_solutions.append(word)
    for letter in word:
        letterCount[letter] = letterCount.get(letter,0) + 1

        totalLetters += 1

def game_feedback(guess, word):
    feedback = ['-' for _ in range(5)]
    correct_letters = list(word)

    for i in range(5):
        if guess[i] == word[i]:
            feedback[i] = 'G'
            correct_letters[i] = None
    for i in range(5):
        if feedback[i]!= 'G' and guess[i] in correct_letters:
            feedback[i] = 'Y'
            correct_letters[correct_letters.index(guess[i])] = None

    return ''.join(feedback)

def play_baseline(valid_solutions, word=None):

    word_list = valid_solutions.copy()

    if word is None:
        word = random.choice(valid_solutions)
    print("random: ")
    for attempt in range(1, 7):
        guess = random.choice(word_list)
        feedback = game_feedback(guess, word)

        print(f"Guess {attempt}: {guess} → {feedback}")
        if feedback == 'GGGGG':
            print(f"Solved in {attempt} guesses")
            return attempt
        new_words = []
        for w in word_list:
          if game_feedback(guess,w) == feedback:
            new_words.append(w)
        word_list = new_words

    print(f"Failed to solve. Word was {word}")
    return 7

def calc_letterFreq(letterCount, totalLetters):
    letterProbs = {}
    for letter in letterCount:
        letterProbs[letter] = letterCount[letter] / totalLetters
    return letterProbs

def calc_probabilities(valid_solutions, letterCount, totalLetters):
    word_score = {}
    word_prob = {}
    letterProbs = calc_letterFreq(letterCount, totalLetters)

    for word in valid_solutions:
        uniqueLetters = set(word)
        score = sum(letterProbs[letter] for letter in uniqueLetters)


        word_score[word] = score
    totalScore = sum(word_score.values())
    for w in word_score:
      word_prob[w] = word_score[w] / totalScore

    return word_prob

def get_posterior(remaining_words, prior, guess, feedback):
    posterior = {}
    total_prob = 0.0

    for w in remaining_words:
        if game_feedback(guess, w) == feedback:
            likelihood = 1.0
        else:
            likelihood = 0.0
        posterior[w] = prior[w] * likelihood
        total_prob += posterior[w]

    if total_prob > 0:
        for w in posterior:
            posterior[w] /= total_prob
    return posterior

def select_first_guess(prior):
  return max(prior, key=prior.get)

def play_game(prob, word=None):
    probs = prob.copy()
    remaining_words = []

    if word is None:
        word = random.choice(valid_solutions)

    print("bayesian: ")
    for attempt in range(1,7):

        for w, prob in probs.items():
          if prob > 0:
            remaining_words.append(w)

        best_word = None
        best_prob = -1
        for w in remaining_words:
            if probs[w] > best_prob:
              best_prob = probs[w]
              best_word = w
        guess = best_word

        feedback = game_feedback(guess, word)
        posterior = get_posterior(remaining_words, probs, guess, feedback)
        print(f"Guess {attempt}: {guess} → {feedback}")

        if feedback == 'GGGGG':
            print(f"\nSolved in {attempt} guesses")
            return attempt

        probs = posterior

    print(f"\nFailed to solve. Word was: {word}")
    return 7

def compare_games(num_games=100):
    baseline_results = []
    bayes_results = []

    bayes_failure = 0
    baseline_failure = 0
    prob = calc_probabilities(valid_solutions, letterCount, totalLetters)

    for _ in range(num_games):
        random_word = random.choice(valid_solutions)

        baseline_guess = play_baseline(valid_solutions, word=random_word)
        baseline_results.append(baseline_guess)
        if baseline_guess == 7:
          baseline_failure += 1

        bayes_guess = play_game(prob, word=random_word)

        bayes_results.append(bayes_guess)
        if bayes_guess == 7:
          bayes_failure += 1

        baseline_avg = np.mean(baseline_results)
        bayesian_avg = np.mean(bayes_results)


    print("\n--- Summary ---")
    print("Baseline average guesses: ", baseline_avg)
    print("Bayesian average guesses: ", bayesian_avg)
    return baseline_results, bayes_results, baseline_avg, bayesian_avg

baseline_results, bayes_results, baseline_avg, bayesian_avg = compare_games(num_games=100)

def print_results_table(baseline_results, bayes_results, baseline_avg, bayesian_avg):

    baseline_minGuesses = np.min(baseline_results)
    bayesian_minGuesses = np.min(bayes_results)

    baseline_maxGuesses = np.max(baseline_results)
    bayesian_maxGuesses = np.max(bayes_results)

    baseline_percent = np.mean(np.array(baseline_results) <= 3) * 100
    bayesian_percent = np.mean(np.array(bayes_results) <= 3) * 100

    print("| Metric                 | Baseline | Bayesian |")
    print("|------------------------|----------|----------|")
    print(f"| Average guesses        | {baseline_avg:.2f}     | {bayesian_avg:.2f}     |")
    print(f"| Min guesses            | {baseline_minGuesses}        | {bayesian_minGuesses}        |")
    print(f"| Max guesses            | {baseline_maxGuesses}        | {bayesian_maxGuesses}        |")
    print(f"| % solved ≤3 guesses    | {baseline_percent:.1f}%     | {bayesian_percent:.1f}%     |")


print_results_table(baseline_results, bayes_results, baseline_avg, bayesian_avg)