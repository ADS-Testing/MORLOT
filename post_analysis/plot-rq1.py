import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import matplotlib
from matplotlib.pyplot import figure


def plot(ax,indx,road_type,file_name):
    labels = []
    data = []
    with open(file_name, 'r') as f:
        for line in f:
            tokens = line.strip().split(',')
            labels.append(tokens[0])
            print(labels)
            alg_data = [float(tokens[i]) for i in range(1, len(tokens)-1)]
            data.append(alg_data)

    ax[indx].boxplot(data, labels=labels,showmeans=True)
    ax[indx].set_title(road_type,fontsize=12)
    matplotlib.pyplot.yticks(fontsize=12)
    ax[indx].tick_params(axis='both', which='major', labelsize=14)

    matplotlib.pyplot.xticks(fontsize=12)
    axes = plt.gca()

    ax[indx].set_ylabel('TSE',fontsize=12)
    ax[indx].tick_params(axis='x', rotation=90)


if __name__ == '__main__':
    plt.rcParams["font.family"] = "Times New Roman"
    fig, ax = plt.subplots(1,3,figsize=(6, 4))
    plot(ax,0,'Straight','processed_data/RQ1/RQ1-ST.txt')
    plot(ax,1,'Left-Turn','processed_data/RQ1/RQ1-LT.txt')
    plot(ax,2,'Right-Turn','processed_data/RQ1/RQ1-RT.txt')

    fig.tight_layout()


    plt.show()
    fig.savefig('RQ1.pdf',bbox_inches='tight', dpi=100)
