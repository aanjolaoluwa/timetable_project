import matplotlib.pyplot as plt


def plot_convergence(ga, sa, tabu):
    plt.figure(figsize=(10,5))

    plt.plot(ga, label="Genetic Algorithm")
    plt.plot(sa, label="Simulated Annealing")
    plt.plot(tabu, label="Tabu Search")

    plt.title("Algorithm Convergence Comparison")
    plt.xlabel("Iterations")
    plt.ylabel("Fitness")
    plt.legend()
    plt.grid()
    plt.show()


def plot_final_comparison(ga, sa, tabu):
    plt.figure(figsize=(7,5))

    plt.bar(["GA", "SA", "Tabu"], [ga, sa, tabu])

    plt.title("Final Fitness Comparison")
    plt.ylabel("Fitness Score")
    plt.grid(axis="y")
    plt.show()