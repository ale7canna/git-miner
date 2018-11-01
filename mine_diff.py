import subprocess
import argparse
import re

reg_exp = re.compile(r"(?P<matches>index\s\w+\.\.\w+(\s\d{6,})?\n---\s(?P<fileA>[\w\/\-\.]+)\n\+\+\+\s(?P<fileB>[\w\/\-\.]+)\n(?P<changes>(?P<hunk_changes>@@ -\d+(,\d+)? \+\d+(,\d+)? @@[ \w\-:\/\.,\+\=\"]*)\n(?P<content>([\s\+\-\\][ @\w\.\-#+:\/\|\[\](),^/*=\"'`<>\\/{/}$]*\n)*))+)")


def git_differences(rev1, rev2):
    if rev1 == None: rev1 = "HEAD~1"
    if rev2 == None: rev2 = "HEAD"
    return subprocess.Popen(["git", "diff", rev1, rev2],
                            stdout=subprocess.PIPE).communicate()[0].decode("utf8")


def get_record_from(differences):
    result = []
    res = [m.groupdict() for m in reg_exp.finditer(differences)]
    for r in res:
        item = {}
        for k,v in r.items():
            if k == "matches" or k == "changes":
                continue
            if k.startswith("file"):
                v = v[2:] if v.startswith("a/") or v.startswith("b/") else v
            item[k] = v
        result.append(item)
    return result


def print_diff_btw(rev1, rev2):
    differences = get_record_from(git_differences(rev1, rev2))
    for d in differences:
        for k,v in d.items():
            print ("################", k)
            print ("################", v)

        print ("################")


def print_diff_stat(rev1, rev2):
    differences = get_record_from(git_differences(rev1, rev2))
    for d in differences:
        f = d["fileA"] if d["fileA"] == d["fileB"] else "{} -> {}".format(d["fileA"], d["fileB"])
        adds = sum (1 if l.startswith("+") else 0 for l in d["content"].split("\n"))
        rems = sum (1 if l.startswith("-") else 0 for l in d["content"].split("\n"))
        print("file:", f, "adds:", adds, "rems:", rems)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculates differences in a file between 2 commits.")
    parser.add_argument("--rev1", type=str, help="The revision to start the comparison from.")
    parser.add_argument("--rev2", type=str, help="The second revision.")
    args = parser.parse_args()

    print_diff_stat(args.rev1, args.rev2)
