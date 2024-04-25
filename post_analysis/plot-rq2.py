import matplotlib.pyplot as plt
import matplotlib.ticker as plticker


def plot(ax, road_type, file_name):
    y = [i * 20 for i in range(13)]
    patterns = ['o', '.', 'D', 'x', 's', 'v', '^', '<', '>']

    with open(file_name, 'r') as f:
        i = 0
        for line in f:
            tokens = line.strip().split(',')
            alg_data = [float(tokens[i]) for i in range(1, len(tokens))]
            alg_data.insert(0, 0.0)
            ax.plot(y, alg_data, marker=patterns[i], label=tokens[0])
            i += 1

    plt.xlim([0, 240])
    plt.ylim([0, 0.5])
    ax.set_ylabel('Average TSE', size=14)
    ax.set_xlabel('Execution Time (min)', size=14)
    ax.set_title(road_type, fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.xaxis.set_major_locator(plticker.MultipleLocator(base=40))
    ax.yaxis.set_major_locator(plticker.MultipleLocator(base=0.1))


if __name__ == '__main__':
    plt.rcParams["font.family"] = "Times New Roman"
    fig, axs = plt.subplots(1, 3, figsize=(13, 4))

    plot(axs[0], 'Straight', 'processed_data/RQ2/RQ2-ST.txt')
    plot(axs[1], 'Left-Turn', 'processed_data/RQ2/RQ2-LT.txt')
    plot(axs[2], 'Right-Turn', 'processed_data/RQ2/RQ2-RT.txt')

    lines, labels = fig.axes[-1].get_legend_handles_labels()
    fig.legend(lines, labels,
               loc='upper center',
               prop={'size': 14},
               ncol=4,
               borderaxespad=0.1,
               bbox_to_anchor=(0.5, 0.97))
    fig.tight_layout(rect=[0, 0, 1, 0.85])
    fig.savefig('RQ2.pdf', bbox_inches='tight', dpi=1000)
    plt.show()
