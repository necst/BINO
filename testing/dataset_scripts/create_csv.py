import sys
import os

if __name__=="__main__":
    if len(sys.argv) == 2:
        prjs_dir = sys.argv[1]
        prjs = os.listdir(prjs_dir)
        s = ""
        for prj in prjs:
            s += "x,\"https://api.github.com/repos/%s\",x\n" % prj.replace("___", "/")
        s = s[:-1]
        f = open("projects.csv", "w")
        f.write(s)
        f.close()
    else:
        print("Usage: ./create_csv.py <dir>")