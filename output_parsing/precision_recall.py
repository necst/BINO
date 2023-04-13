import argparse
import os.path
import os
from classes.projects_results import ProjectsResults
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axis import Axis
import matplotlib.ticker as ticker
import math


x_values = list(np.arange(0.75, 1.0, 0.01))
PALETTE = ["red", "blue", "green", "black", "orange"]
PROJECTS_DIR = os.path.join("github_projects", "projects")
METHODS = []
METHODS += ["std::map::operator[]", "std::map::lower_bound", "std::map::upper_bound", "std::map::find", "std::map::erase", "std::map::at"]
METHODS += ["std::vector::push_back", "std::vector::resize", "std::vector::clear","std::vector::reserve","std::vector::erase", "std::vector::insert", "std::vector::emplace_back"]
METHODS += ["std::deque::push_back", "std::deque::pop_front", "std::deque::operator[]", "std::deque::push_front", "std::deque::pop_back"]


def f1_score(rec, prec):
    return (2 * rec * prec) / (rec + prec)

def dir_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(path + " is not a valid directory path.")
    return path


if __name__=="__main__":
    # Projecj path
    prj_path = os.path.dirname(os.path.abspath(__file__))
    # Argument parsing
    parser = argparse.ArgumentParser(description="Script to test M.")
    # Required argument
    parser.add_argument(dest="test_dir",
                        type=dir_path,
                        help="Directory that contains the experiments' results.")    
    args = parser.parse_args()
    # Iterating over classes under test
    test_dir = args.test_dir
    classes = os.listdir(test_dir)
    # Initializing first class
    prjs_0_path = os.path.join(test_dir, classes[0], PROJECTS_DIR)
    if not os.path.exists(prjs_0_path) or not os.path.isdir(prjs_0_path):
        raise Exception("Directory must contains a directory for each class under test and inside of them the \"github_projects\" directory.")
    prjs_res = ProjectsResults(prjs_0_path)
    for class_i in classes[1:]:
        prjs_i_path = os.path.join(test_dir, class_i, PROJECTS_DIR)
        # Directory prjs_directory must exists
        if not os.path.exists(prjs_i_path) or not os.path.isdir(prjs_i_path):
            raise Exception("Directory must contains a directory for each class under test and inside of them the \"github_projects\" directory.")
        prjs_res_tmp = ProjectsResults(prjs_i_path)
        prjs_res.merge(prjs_res_tmp)
    # Computing
    prjs_res.filter_methods(keep=METHODS)
    k = 0
    for i in [6]:
        #print("")
        #print("M = %d" % i)
        s_values = []
        rec_values = []
        prec_values = []
        for j in np.arange(0.75, 0.99, 0.01):
            n, tp, fp = prjs_res.get_stats_by_M_and_S(i, j)
            rec = tp/n
            prec = (tp/(tp + fp))
            rec_values.append(rec)
            prec_values.append(prec)
            s_values.append(j)
        rec_values.append(rec)
        prec_values.append(prec)
        s_values.append(j)
        # Subplots
        fig, ax1 = plt.subplots()
        # Recall plot
        color = 'tab:red'
        ax1.set_xlabel('S')
        ax1.set_ylabel('Recall', color='tab:red')
        ax1.plot(x_values, rec_values, color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim([0.2, 0.9])
        # Initiate same axis
        ax2 = ax1.twinx()
        # Precision plot
        color = 'tab:blue'
        ax2.set_ylabel('Precision', color=color)
        ax2.plot(x_values, prec_values, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim([0.2, 0.9])
        # End
        fig.tight_layout()
        plt.savefig(os.path.join(prj_path, "outputs", "precision_recall", "precision_recall_%d.pdf" % i))
        plt.clf()
        # Plotting Prec-Rec curve
        new_rec = []
        new_prec = []
        new_s_values = []
        while len(rec_values):
            min_value = min(rec_values)
            min_index = rec_values.index(min_value)
            tmp_s = s_values.pop(min_index)
            tmp_rec = rec_values.pop(min_index)
            tmp_prec = prec_values.pop(min_index)
            if math.isclose(tmp_s, 0.78):
                rec_value_1 = tmp_rec
                prec_value_1 = tmp_prec
            if math.isclose(tmp_s, 0.84):
                rec_value_2 = tmp_rec
                prec_value_2 = tmp_prec
            print("X %f - Y: %f - F1: %f - S: %f" % (tmp_rec, tmp_prec, (2 * tmp_prec * tmp_rec) / (tmp_rec + tmp_prec), tmp_s))
            new_rec.append(tmp_rec)
            new_prec.append(tmp_prec)
            new_s_values.append(tmp_s)
        plt.figure()

        plt.plot(new_rec, new_prec, color="blue", label='_nolegend_')
        plt.plot([rec_value_1], [prec_value_1], marker="*", color="red")
        plt.plot([rec_value_2], [prec_value_2], marker="*", color="black")
        label_1 = 'F1-Score: %.3f, S: %.2f' % (f1_score(rec_value_1, prec_value_1), 0.78)
        label_2 = 'F1-Score: %.3f, S: %.2f' % (f1_score(rec_value_2, prec_value_2), 0.84)
        plt.legend(loc='upper right', handles=[plt.plot([],[], marker="*", color="red")[0], plt.plot([],[], marker="*", color="black")[0]], labels=[label_1, label_2], handlelength=0)
        plt.hlines(y=prec_value_1, xmin=0, xmax=rec_value_1, linestyles="dashed")
        plt.hlines(y=prec_value_2, xmin=0, xmax=rec_value_2, linestyles="dashed")
        plt.vlines(x=rec_value_1, ymin=0, ymax=prec_value_1, linestyles="dashed")
        plt.vlines(x=rec_value_2, ymin=0, ymax=prec_value_2, linestyles="dashed")
        plt.xticks(list(plt.xticks()[0]) + [rec_value_1, rec_value_2], rotation="vertical")
        plt.yticks(list(plt.yticks()[0]) + [prec_value_1, prec_value_2])
        ax = plt.gca()
        formatter = ticker.FormatStrFormatter("%1.2f")
        Axis.set_major_formatter(ax.xaxis, formatter)
        Axis.set_major_formatter(ax.yaxis, formatter)
        plt.xlim([0.27, 0.70])
        plt.ylim([0.60, 0.82])
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.subplots_adjust(bottom=0.15)
        plt.savefig(os.path.join(prj_path, "outputs", "precision_recall", "precision_recall_curve_%d.pdf" % i))
        plt.clf()

            

