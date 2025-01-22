# Yahtzee AI

This is a project focused on implementing an AI for the Yahtzee game using Q-learning. An implementation of the game is also provided for the ease of training our AI and for just playing the game.

Our team is composed of: Chirvasă Matei-George, Mitreanu Alexandru, Prodan Sabina-Alina.

In what follows we will describe our progress throughout the semester.

## Homework 1

For this task we had to implement the game Yahtzee and add a Random AI.

As a bonus, we implemented dice animations by implementing a state machine of possible dice states, which allowed us to easily implement the animations.

## Homework 2

For this task we had to implement the AI for the game using Q-learning. Obviously, we tried numerous ways of training the AI, but, in the end, we arrived at the following configuration:
- the AI is trained on a single-player game (i.e. it doesn't have to wait for a second player to move, which speeds up learning)
- in training mode, the AI decides which action to take by the following method:
    - if the respective `(state, action)` pair (states and actions will be defined below) has been visited less than `exploration_threshold` times, then the reward of that pair will be set to `1_000_000` (i.e. a very large number, way more than any other pair could ever give as a reward), this encourages the AI to explore barely visited states
    - if the `(state, action)` pair has been visited more than `exploration_threshold` times, then the reward of that pair is taken from the Q table
    - the action taken can be described using the following formula:
        $$a' = \argmax_{a} Q'(s, a)$$ where $Q'$ is either $1\_000\_000$ or $Q(s, a)$ (as defined above)
    - note: we implemented another exploration strategy using softmax, but we ended up not using it so it won't be detailed here
- state representation
    - a state contains information about the current dice configuration (i.e. player AI currently has dice (1, 2, 3, 5, 6) on the table) and the rerolls left (i.e. player AI currently has 1 reroll left)
    - we encode this information as a number, thus we get 756 possible states (252 dice orders (if sorted) * 3 rerolls = 756 states)
    - even though the state does not fully describe the game state (for example, it doesn't contain any information about the currently picked categories), it seems that it is more than enough information to train an AI that can almost beat a human player (results will be detailed below)
- there are 45 possible actions
    - 13 actions, one for each category that can be picked
    - 31 actions, one for each reroll action. A reroll action is defined by a list of indices of the dice that the AI wants to reroll (e.g. (1, 2) means the AI wants to reroll dice 1 and 2)
    - 1 action for the terminal state (this is used to indicate that the game ended)
- rewards are computed using a simple formula:
    - if the action taken was a category pick (one of the first 13), then the reward is the score of that category with the exception of CHANCE which is multiplied with `0.3` to discourage the AI from relying on it.
    - if the action taken was a reroll, the reward is computed as: `(sum(scores) + first_six_bonus + yahtzee_bonus) / CATEGORY_COUNT`, which can be interpreted as the average score that could be obtained with those dice 
        (where `scores` are the possible scores obtainable in each category, `first_six_bonus` is `35` only if the AI can complete the first six categories with a score over `63` and `yahtzee_bonus` is `100` only if the AI already got an Yahtzee and it just got another one)
- training is done by playing `epochs` games, after each move updating the Q table with:
    $$Q(s, a) = (1 - \alpha) \cdot Q(s, a) + \alpha \cdot (R(s, a) + \gamma \max_{a'} Q(s', a'))$$ where $\gamma$ is the `discount_rate`, a hyperparameter and $\alpha$ is the `learning_rate`, which is computed as the inverse of the number of times that `(s, a)` has been visited (which makes the AI learn less from frequently visited states)

Below we provide our results and the hyperparameters used for training.

### Q-learning Results

| id | epochs | discount_rate | exploration_threshold | exploration strategy | average score* | graphs | state |
|----|--------|---------------|-----------------------|----------------------|----------------|--------|-------|
| 1  | 100k   | 0.9           | 20                    | argmax               | 150            | [train](graphs/1_q_train_scores.png), [train_avg_1k](graphs/1_q_train_avg_scores_1k.png), [test](graphs/1_q_test_scores.png) | [state](states/1.npz)
| 1  | +100k  | 0.9           | 20                    | argmax               | 150            | [train](graphs/2_q_train_scores.png), [train_avg_1k](graphs/2_q_train_avg_scores_1k.png), [test](graphs/2_q_test_scores.png) | [state](states/2.npz)
| 2  | 200k   | 0.9           | 20                    | argmax               | 150            | [train](graphs/3_q_train_scores.png), [train_avg_1k](graphs/3_q_train_avg_scores_1k.png), [test](graphs/3_q_test_scores.png) | [state](states/3.npz)
| 3  | 100k   | 0.95          | 20                    | argmax               | 140            | [train](graphs/4_q_train_scores.png), [train_avg_1k](graphs/4_q_train_avg_scores_1k.png), [test](graphs/4_q_test_scores.png) | [state](states/4.npz)
| 4  | 100k   | 0.85          | 20                    | argmax               | 155            | [train](graphs/5_q_train_scores.png), [train_avg_1k](graphs/5_q_train_avg_scores_1k.png), [test](graphs/5_q_test_scores.png) | [state](states/5.npz)
| 4  | +100k  | 0.85          | 20                    | argmax               | 155            | [train](graphs/6_q_train_scores.png), [train_avg_1k](graphs/6_q_train_avg_scores_1k.png), [test](graphs/6_q_test_scores.png) | [state](states/6.npz)
| 5  | 100k   | 0.85          | 20                    | argmax               | 155            | [train](graphs/7_q_train_scores.png), [train_avg_1k](graphs/7_q_train_avg_scores_1k.png), [test](graphs/7_q_test_scores.png) | [state](states/7.npz)

\*) The average score is computed over 1k epochs intervals.

5 had rewards fixed

## Homework 3

For this task we had to implement different NLP functionalities on an arbitrary romanian text. Our features were:
- stylometric analysis
- language detection
- replacing the words in a phrase with synonyms/hypernyms/negated antonyms
- keyword extraction using Lesk algorithm
- phrase generation using a `gpt_neo` transformer

## Final Additions

Before our presentation we added two important features:
- statistics collection (track the progress of our player throughout time)
- chatbot (the user can now talk to a chatbot which uses GPT-4o behind the scenes to give answers)

## Contributions

Throughout this semester, we worked together most of the time in order to achieve our goals, but, if we were to mention the special contributions each of us had for this project it would go like this:

Chirvasă Matei-George: AI development, UI for chatbot, statistics
Mitreanu Alexandru: AI development, UI for the rest of the game
Prodan Sabina-Alina: NLP and chatbot

## References

1. Mitchell, T. M. (1997). Machine Learning.
2. Sutton, R. S. and Barto, A. G. (2018). Reinforcement Learning An Introduction Second Edition.
3. Russell, S.; Norvig, P. (1995). Artificial Intelligence: A Modern Approach.
4. https://github.com/Alegzandra/Romanian-NLP-tools
5. https://huggingface.co/dumitrescustefan/gpt-neo-romanian-780m


