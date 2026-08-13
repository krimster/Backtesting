import matplotlib

matplotlib.use("QtAgg")

import matplotlib.pyplot as plt

print("Backend:", matplotlib.get_backend())

plt.plot([1, 2, 3, 4])

plt.show()
