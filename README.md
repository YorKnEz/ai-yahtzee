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


