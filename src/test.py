import sys
from time import time

import matplotlib.pyplot as plt
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
        epochs=100_000,
        discount_rate=0.95,
        # exploration_decay=lambda e: max(e * 0.999997, 0.1),
        save_state=True,
    )

    # use existing model
    q, (epochs, discount_rate, exploration_factor) = QSmall.from_state_file()

    # train existing model
    # q.train(
    #     epochs=400_000,
    #     discount_rate=discount_rate,
    #     # exploration_factor=exploration_factor,
    #     # exploration_decay=lambda e: max(e * 0.999997, 0.1),
    #     save_state=True,
    # )

    # print(q.n[np.random.choice(q.q.shape[0], size=20, replace=False)])

    print(f"Explored:       {np.count_nonzero(q.n) / q.n.size:.4f}")
    print(f"Fully explored: {np.count_nonzero(q.n > 5) / q.n.size:.4f}")

    # test training so far
    # q.train(
    #     epochs=1_000,
    #     discount_rate=discount_rate,
    #     exploration_factor=0.0,  # don't allow exploration, use only current knowledge
    #     # no decay
    #     save_state=False,  # DO NOT persist state
    # )

    # a = q.n[np.any(q.n != 0, axis=1)]
    # lines = 10

    # for i in range(len(a) // lines):
    #     print(a[i * lines : (i + 1) * lines])
    #     input()
