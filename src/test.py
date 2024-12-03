import sys

import numpy as np

from ai.q import Q

np.set_printoptions(threshold=sys.maxsize)

if __name__ == "__main__":
    exploration_threshold = 20

    # start new model
    # q = Q()
    # q.train(
    #     epochs=50_000,
    #     discount_rate=0.2,
    #     # exploration_factor=0.0,
    #     exploration_threshold=exploration_threshold,
    #     save_state=True,
    # )

    # use existing model
    q, (epochs, discount_rate, _) = Q.from_state_file()

    # train existing model
    # q.train(
    #     epochs=40_000,
    #     discount_rate=discount_rate,
    #     save_state=True,
    # )

    # different stats
    indices = np.random.choice(q.q.shape[0], size=20, replace=False)
    for i, line in zip(indices, q.q[indices]):
        print(line, i % 3)

    print(f"Explored:       {np.count_nonzero(q.n) / q.n.size:.4f}")
    print(f"Fully explored: {np.count_nonzero(q.n > exploration_threshold) / q.n.size:.4f}")

    q_n_2_rerolls = q.n[np.arange(q.n.shape[0]) % 3 == 2]
    q_n_1_rerolls = q.n[np.arange(q.n.shape[0]) % 3 == 1]
    q_n_0_rerolls = q.n[np.arange(q.n.shape[0]) % 3 == 0, :13]

    print(f"Fully explored with 2 rerolls left:    {np.count_nonzero(q_n_2_rerolls > exploration_threshold) / q_n_2_rerolls.size:.4f}")
    print(f"Fully explored with 1 reroll left:    {np.count_nonzero(q_n_1_rerolls > exploration_threshold) / q_n_1_rerolls.size:.4f}")
    print(f"Fully explored with 0 rerolls left: {np.count_nonzero(q_n_0_rerolls > exploration_threshold) / q_n_0_rerolls.size:.4f}")

    # test training so far on 1k epochs
    q.test()
