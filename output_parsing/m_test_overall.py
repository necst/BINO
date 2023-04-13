import argparse
import os.path
import os
from classes.projects_results import ProjectsResults
import numpy as np
import matplotlib.pyplot as plt


x_values = list(np.arange(0.75, 1.0, 0.01)) + [1.0]
PALETTE = ["red", "blue", "green", "black", "orange"]
PROJECTS_DIR = os.path.join("github_projects", "projects")
METHODS = []
METHODS += ["std::map::operator[]", "std::map::lower_bound", "std::map::upper_bound", "std::map::find", "std::map::erase", "std::map::at"]
METHODS += ["std::vector::push_back", "std::vector::resize", "std::vector::clear","std::vector::reserve","std::vector::erase", "std::vector::insert", "std::vector::emplace_back"]
METHODS += ["std::deque::push_back", "std::deque::pop_front", "std::deque::operator[]", "std::deque::push_front", "std::deque::pop_back"]


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
    for i in range(5, 10):
        y_values = []
        print("M = %d" % i)
        for j in np.arange(0.75, 1.0, 0.01):
            n, tp, fp = prjs_res.get_stats_by_M_and_S(i, j)
            rec = tp/n
            prec = (tp/(tp + fp))
            f1 = (2 * ((prec * rec) / (prec + rec)))
            y_values.append(f1)
            print("F1: %f, S: %.2f" % (f1, j))
        y_values.append(f1)
        print("F1: %f, S: %.2f" % (f1, j + 0.01))
        print("")
        plt.plot(x_values, y_values, color=PALETTE[k], label="M = %d / N = %d" % (i, n))
        k += 1
    plt.legend()
    #plt.title("overall")
    plt.xlabel("S")
    plt.xlim([0.75, 1.0])
    plt.ylabel("F1-Score")
    plt.savefig(os.path.join(prj_path, "outputs", "m_test_overall", "overall.pdf"))
    plt.clf()