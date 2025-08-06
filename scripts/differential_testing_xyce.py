import os
import numpy
import shutil
import subprocess
from spicelib import RawRead
import math
import multiprocessing


def simulate_on_xyce_sparse(filepath, filename, maxtime):
    test_path = "./test/ksparse"
    if not os.path.exists(test_path):
        os.makedirs(test_path)
    new_path = os.path.join(test_path, filename)
    shutil.copy(filepath, new_path)
    with open(new_path, "r") as f:
        lines = f.readlines()
    f.close()
    with open(new_path, "w") as f:
        f.write(lines[0].strip() + "\n")
        f.write(".options linsol type=ksparse\n")
        for i in range(1, len(lines)):
            f.write(lines[i].strip() + "\n")
    f.close()
    cmd ="/home/user/XyceInstall/Serial/bin/Xyce -l "+ filename[:-4] + ".log -r " + filename[:-4] + ".raw "+ filename
    try:
        result = subprocess.run(cmd, cwd=test_path, timeout=maxtime, shell=True)
        if result.returncode == 0:
            return 0
        else:
            return 1
    except subprocess.TimeoutExpired:
        cmd = "pkill -f Xyce"  # 超时后终止Xyce进程
        subprocess.run(cmd, shell=True)
        return 2


def simulate_on_xyce_klu(filepath, filename, maxtime):
    test_path = "./test/klu"
    if not os.path.exists(test_path):
        os.makedirs(test_path)
    new_path = os.path.join(test_path, filename)
    shutil.copy(filepath, new_path)
    with open(new_path, "r") as f:
        lines = f.readlines()
    f.close()
    with open(new_path, "w") as f:
        f.write(lines[0].strip() + "\n")
        f.write(".options linsol type=klu\n")
        for i in range(1, len(lines)):
            f.write(lines[i].strip() + "\n")
    f.close()
    cmd = "/home/user/XyceInstall/Serial/bin/Xyce -l "+ filename[:-4] + ".log -r " + filename[:-4] + ".raw "+ filename
    try:
        result = subprocess.run(cmd, cwd=test_path, timeout=maxtime, shell=True)
        if result.returncode == 0:
            return 0
        else:
            return 1
    except subprocess.TimeoutExpired:
        cmd = "pkill -f Xyce"  # 超时后终止Xyce进程
        subprocess.run(cmd, shell=True)
        return 2

def compare_worker(path1, path2, error, return_dict):
    try:
        raw_file1 = RawRead(path1)
        raw_file2 = RawRead(path2)

        trace_names1 = raw_file1.get_trace_names()
        trace_names2 = raw_file2.get_trace_names()

        for i, trace_name1 in enumerate(trace_names1):
            if i >= len(trace_names2):
                return_dict["result"] = 1
                return

            trace_name2 = trace_names2[i]
            if trace_name1 == "time":
                continue

            trace1 = raw_file1.get_trace(trace_name1)
            trace2 = raw_file2.get_trace(trace_name2)
            wave1 = trace1.get_wave(0)
            wave2 = trace2.get_wave(0)

            if len(wave1) != len(wave2):
                return_dict["result"] = 1
                return

            for value1, value2 in zip(wave1, wave2):
                min_value = min(abs(value1), abs(value2))
                if min_value == 0:
                    if abs(value1 - value2) > numpy.float32(error):
                        return_dict["result"] = 1
                        return
                elif abs(value1 - value2) > numpy.float32(error) * min_value:
                    return_dict["result"] = 1
                    return

        return_dict["result"] = 0
    except Exception as e:
        print(f"Error in compare_worker: {e}")
        return_dict["result"] = 1


def compare_raw_files_by_index(path1, path2, error, timeout=10):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=compare_worker, args=(path1, path2, error, return_dict))
    p.start()
    p.join(timeout)

    if p.is_alive():
        print("比较超时，终止进程")
        p.terminate()
        p.join()
        return 2  # 超时

    return return_dict.get("result", 1)

def differential_testing(filepath, filename, maxtime, error):
    code1 = simulate_on_xyce_sparse(filepath, filename, maxtime)
    print("sparse code:" + str(code1))
    code2 = simulate_on_xyce_klu(filepath, filename, maxtime)
    print("klu code:" + str(code2))
    compare_code = -1
    raw_file_path1 = f"./test/ksparse/{filename[:-4]}.raw"
    raw_file_path2 = f"./test/klu/{filename[:-4]}.raw"
    if code1 == 0 and code2 == 0:
        if os.path.exists(raw_file_path1) and os.path.exists(raw_file_path2):
            compare_code = compare_raw_files_by_index(raw_file_path1, raw_file_path2, error)
        else:
            compare_code = 2
    print("compare code:" + str(compare_code))
    with open("./test/output.txt", "w") as f:
        f.write(f"code1:{str(code1)}\n")
        f.write(f"code2:{str(code2)}\n")
        f.write(f"code3:{str(compare_code)}\n")
    f.close()
    run_results = {"sparse": code1, "klu": code2}
    compare_results = {("sparse", "klu"): compare_code}

    return run_results, compare_results