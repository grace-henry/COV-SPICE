import math
import os
import numpy
import shutil
import subprocess

from spicelib import RawRead


def simulate_on_ngspice_44(filepath, filename, maxtime):
    test_path = "./test/ngspice44"
    if not os.path.exists(test_path):
        os.makedirs(test_path)
    new_path = os.path.join(test_path, filename)
    shutil.copy(filepath, new_path)
    with open(new_path, "r") as f:
        lines = f.readlines()
    f.close()
    with open(new_path, "w") as f:
        f.write(lines[0].strip() + "\n")
        f.write(".options sparse\n")
        for i in range(1, len(lines)):
            f.write(lines[i].strip() + "\n")
    f.close()
    cmd = "ngspice44 -b -r " + filename[:-4] + ".raw -o " + filename[:-4] + ".log " + filename
    try:
        result = subprocess.run(cmd, cwd=test_path, timeout=maxtime, shell=True)
        if result.returncode == 0:
            return 0
        else:
            return 1
    except subprocess.TimeoutExpired:
        subprocess.run(f"pkill -f ngspice44", shell=True)
        return 2


def simulate_on_ngspice_43(filepath, filename, maxtime):
    test_path = "./test/ngspice43"
    if not os.path.exists(test_path):
        os.makedirs(test_path)
    new_path = os.path.join(test_path, filename)
    shutil.copy(filepath, new_path)
    with open(new_path, "r") as f:
        lines = f.readlines()
    f.close()
    with open(new_path, "w") as f:
        f.write(lines[0].strip() + "\n")
        f.write(".options sparse\n")
        for i in range(1, len(lines)):
            f.write(lines[i].strip() + "\n")
    f.close()
    cmd = "ngspice43 -b -r " + filename[:-4] + ".raw -o " + filename[:-4] + ".log " + filename
    try:
        result = subprocess.run(cmd, cwd=test_path, timeout=maxtime, shell=True)
        if result.returncode == 0:
            return 0
        else:
            return 1
    except subprocess.TimeoutExpired:
        subprocess.run(f"pkill -f ngspice44", shell=True)
        return 2


# def get_same_time_points(path1, path2, output_file='same_time_points.txt'):
#     try:
#         # 读取raw文件
#         raw_file1 = RawRead(path1)
#         raw_file2 = RawRead(path2)
#
#         # 获取时间波形数据
#         trace_names1 = raw_file1.get_trace_names()
#         if "time" not in trace_names1:
#             return -1, [], []
#
#         trace_time1 = raw_file1.get_trace("time")
#         trace_time2 = raw_file2.get_trace("time")
#         wave_time1 = trace_time1.get_wave(0)
#         wave_time2 = trace_time2.get_wave(0)
#
#         points_1 = []
#         points_2 = []
#         point_1 = 0
#         point_2 = 0
#
#         # 对比时间点
#         while point_1 < len(wave_time1) and point_2 < len(wave_time2):
#             if wave_time1[point_1] == wave_time2[point_2]:
#                 points_1.append(point_1)
#                 points_2.append(point_2)
#                 point_1 += 1
#                 point_2 += 1
#             elif wave_time1[point_1] < wave_time2[point_2]:
#                 point_1 += 1
#             else:
#                 point_2 += 1
#
#         # 保存结果到文件
#         with open(output_file, 'w') as file:
#             file.write("Index in File 1\tIndex in File 2\n")
#             for p1, p2 in zip(points_1, points_2):
#                 file.write(f"{p1}\t{p2}\n")
#
#         print(f"Same time points saved to {output_file}")
#         return 0, points_1, points_2
#
#     except Exception as e:
#         print(f"Error processing files {path1} and {path2}: {e}")
#         return -1, [], []


# def compare_ngspice_raw_file(path1, path2, error):
#     state, points1,points2 = get_same_time_points(path1,path2)
#     raw_file1 = RawRead(path1)
#     raw_file2 = RawRead(path2)
#     trace_names1 = raw_file1.get_trace_names()
#     trace_names2 = raw_file2.get_trace_names()
#     for i in range(len(trace_names1)):
#         trace_name1 = trace_names1[i]
#         trace_name2 = trace_names2[i]
#         if trace_name1 == "time":
#             continue
#         trace1 = raw_file1.get_trace(trace_name1)
#         trace2 = raw_file2.get_trace(trace_name2)
#         wave1 = trace1.get_wave(0)
#         wave2 = trace2.get_wave(0)
#         if state == -1:
#             if len(wave1) != len(wave2):
#                 return 1
#             for k in range(len(wave1)):
#                 value1 = wave1[k]
#                 value2 = wave2[k]
#                 min_value = min(math.fabs(value1), math.fabs(value2))
#                 if math.fabs(value1 - value2) > numpy.float32(error) * min_value:
#                     return 1
#                 # if not ((value1 - numpy.float32(error)) <= value2 <= (value1 + numpy.float32(error))):
#                 #     return 1
#             return 0
#         elif state == 0:
#             for k in range(len(points1)):
#                 value1= wave1[points1[k]]
#                 value2= wave2[points2[k]]
#                 min_value = min(math.fabs(value1), math.fabs(value2))
#                 if math.fabs(value1 - value2) > numpy.float32(error) * min_value:
#                     return 1
#                 # if not ((value1-numpy.float32(error))<=value2<=(value1+numpy.float32(error))):
#                 #     return 1
#             return 0
def compare_raw_files_by_index(path1, path2, error):
    try:
        # Read raw files
        raw_file1 = RawRead(path1)
        raw_file2 = RawRead(path2)

        trace_names1 = raw_file1.get_trace_names()
        trace_names2 = raw_file2.get_trace_names()

        # Compare traces
        for i, trace_name1 in enumerate(trace_names1):
            if i >= len(trace_names2):
                print(f"Trace mismatch: {trace_name1} not found in second file")
                return 1

            trace_name2 = trace_names2[i]
            if trace_name1 == "time":
                continue

            trace1 = raw_file1.get_trace(trace_name1)
            trace2 = raw_file2.get_trace(trace_name2)
            wave1 = trace1.get_wave(0)
            wave2 = trace2.get_wave(0)

            if len(wave1) != len(wave2):
                print(f"Trace lengths do not match for {trace_name1}")
                return 1

            # Compare values directly
            for value1, value2 in zip(wave1, wave2):
                min_value = min(abs(value1), abs(value2))
                if min_value == 0:
                    if abs(value1 - value2) > numpy.float32(error):
                        return 1
                elif abs(value1 - value2) > numpy.float32(error) * min_value:
                    return 1

        return 0

    except Exception as e:
        print(f"Error in compare_raw_files_by_index: {e}")
        return 1
def differential_testing(filepath, filename, maxtime, error):
    code1 = simulate_on_ngspice_44(filepath, filename, maxtime)
    print("sparse code:" + str(code1))
    code2 = simulate_on_ngspice_43(filepath, filename, maxtime)
    print("klu code:" + str(code2))
    compare_code = -1
    raw_file_path1 = "./test/ngspice44/" + filename[:-4] + ".raw"
    raw_file_path2 = "./test/ngspice43/" + filename[:-4] + ".raw"
    if code1 == 0 and code2 == 0:
        if os.path.exists(raw_file_path1) and os.path.exists(raw_file_path2):
            compare_code = compare_raw_files_by_index(raw_file_path1, raw_file_path2, error)
        else:
            compare_code = 2
    print("compare code:" + str(compare_code))
    with open("./test/output.txt", "w") as f:
        f.write("code1:" + str(code1) + "\n")
        f.write("code2:" + str(code2) + "\n")
        f.write("code3:" + str(compare_code) + "\n")
    f.close()
    return code1, code2, compare_code

