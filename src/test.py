import sys

import numpy as np

from ai.q import Q, QSmall
from ai.random_ai import R

np.set_printoptions(threshold=sys.maxsize)

if __name__ == "__main__":
    # r = R()
    # r.train(epochs=1_000_000)

    # start new model
    q = QSmall()
    q.train(
        epochs=10_000,
        discount_rate=0.9,
        # exploration_factor=1.0,
        save_state=True,
    )

    # use existing model
    # q, (epochs, discount_rate, _) = QSmall.from_state_file()

    # train existing model
    # q.train(
    #     epochs=10_000,
    #     discount_rate=discount_rate,
    #     save_state=True,
    # )

    # different stats
    indices = np.random.choice(q.q.shape[0], size=20, replace=False)
    for i, line in zip(indices, q.q[indices]):
        print(line, i % 3)

    print(f"Explored:       {np.count_nonzero(q.n) / q.n.size:.4f}")
    print(f"Fully explored: {np.count_nonzero(q.n > 5) / q.n.size:.4f}")

    q_n_2_rerolls = q.n[np.arange(q.n.shape[0]) % 3 == 2]
    q_n_1_rerolls = q.n[np.arange(q.n.shape[0]) % 3 == 1]
    q_n_0_rerolls = q.n[np.arange(q.n.shape[0]) % 3 == 0, :13]

    print(f"Fully explored with 2 rerolls left:    {np.count_nonzero(q_n_2_rerolls > 5) / q_n_2_rerolls.size:.4f}")
    print(f"Fully explored with 1 reroll left:    {np.count_nonzero(q_n_1_rerolls > 5) / q_n_1_rerolls.size:.4f}")
    print(f"Fully explored with 0 rerolls left: {np.count_nonzero(q_n_0_rerolls > 5) / q_n_0_rerolls.size:.4f}")

    # test training so far on 1k epochs
    q.test()
