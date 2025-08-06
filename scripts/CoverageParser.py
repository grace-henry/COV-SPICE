import re
import os
import shutil
import subprocess


class CoverageParser:
    def __init__(self):
        self.function_coverage = {}
        self.previous_coverage = {}
        self.top_functions = []

    def parse_callgrind_output(self, log_path):
        """Parse Callgrind output to extract coverage information."""
        if not os.path.exists(log_path):
            print(f"Warning: Callgrind log file not found at {log_path}")
            return {}

        coverage_data = {}

        with open(log_path, 'r') as f:
            content = f.read()

        # Extract the function coverage data
        pattern = r"([0-9,]+)\s+\(\s*([0-9.]+)%\)\s+(\S+):(\S+)"
        matches = re.findall(pattern, content)

        for match in matches:
            ir_count, percentage, file_path, function_name = match
            ir_count = int(ir_count.replace(',', ''))
            percentage = float(percentage)

            function_key = f"{file_path}:{function_name}"
            coverage_data[function_key] = {
                'ir_count': ir_count,
                'percentage': percentage,
                'file': file_path,
                'function': function_name
            }

        # Update the top functions
        sorted_funcs = sorted(coverage_data.items(), key=lambda x: x[1]['ir_count'], reverse=True)
        self.top_functions = [func[0] for func in sorted_funcs[:5]]

        # Calculate coverage improvement
        coverage_improvement = {}
        for func, data in coverage_data.items():
            prev_count = self.previous_coverage.get(func, {}).get('ir_count', 0)
            if prev_count > 0:
                improvement = (data['ir_count'] - prev_count) / prev_count
            else:
                improvement = 1.0 if data['ir_count'] > 0 else 0.0
            coverage_improvement[func] = improvement

        # Update previous coverage
        self.previous_coverage = coverage_data.copy()
        self.function_coverage = coverage_data

        return coverage_improvement

    def run_callgrind(self, test_case_path):
        callgrind_output_dir = "./callgrind_output/"
        if not os.path.exists(callgrind_output_dir):
            os.makedirs(callgrind_output_dir)

        cmd = f"valgrind --tool=callgrind ngspice44 -b {test_case_path}"

        try:
            subprocess.run(cmd, shell=True, check=False, timeout=60)
        except subprocess.TimeoutExpired:
            print(f"[Timeout] {test_case_path} 卡住了，跳过")
            subprocess.run("pkill -f ngspice44", shell=True)
            return None
        except subprocess.CalledProcessError:
            return None

        callgrind_files = [f for f in os.listdir('.') if f.startswith('callgrind.out.')]
        if not callgrind_files:
            print("[Warning] 未生成 callgrind 输出文件")
            return None

        latest_callgrind = sorted(callgrind_files)[-1]
        final_callgrind_path = os.path.join(callgrind_output_dir, latest_callgrind)
        shutil.move(latest_callgrind, final_callgrind_path)

        # ✅ 检查是否包含 events 行
        with open(final_callgrind_path, 'r') as f:
            if not any(line.startswith("events:") for line in f):
                print(f"[Warning] 无效的 callgrind 文件（缺少 events 行）: {final_callgrind_path}")
                return None

        report_file = f"./coverage_reports/{latest_callgrind}.coverage.txt"
        try:
            subprocess.run(
                f"callgrind_annotate --auto=yes {final_callgrind_path} > {report_file}",
                shell=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[Error] callgrind_annotate 失败: {e}")
            return None

        return report_file

    def run_callgrind_xyce(self, test_case_path):
        callgrind_output_dir = "./callgrind_output/"
        if not os.path.exists(callgrind_output_dir):
            os.makedirs(callgrind_output_dir)

        cmd = f"valgrind --tool=callgrind /home/user/XyceInstall/Serial/bin/Xyce -l {test_case_path}"

        try:
            subprocess.run(cmd, shell=True, check=False, timeout=60)
        except subprocess.TimeoutExpired:
            print(f"[Timeout] {test_case_path} 卡住了，跳过")
            subprocess.run("pkill -f Xyce", shell=True)
            return None
        except subprocess.CalledProcessError:
            return None

        callgrind_files = [f for f in os.listdir('.') if f.startswith('callgrind.out.')]
        if not callgrind_files:
            print("[Warning] 未生成 callgrind 输出文件")
            return None

        latest_callgrind = sorted(callgrind_files)[-1]
        final_callgrind_path = os.path.join(callgrind_output_dir, latest_callgrind)
        shutil.move(latest_callgrind, final_callgrind_path)

        # ✅ 检查是否包含 events 行
        with open(final_callgrind_path, 'r') as f:
            if not any(line.startswith("events:") for line in f):
                print(f"[Warning] 无效的 callgrind 文件（缺少 events 行）: {final_callgrind_path}")
                return None

        report_file = f"./coverage_reports/{latest_callgrind}.coverage.txt"
        try:
            subprocess.run(
                f"callgrind_annotate --auto=yes {final_callgrind_path} > {report_file}",
                shell=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[Error] callgrind_annotate 失败: {e}")
            return None

        return report_file
    def calculate_reward(self, coverage_improvement):
        """Calculate reward based on coverage improvement."""
        if not coverage_improvement:
            return 0.0

        # 打印 coverage_improvement 类型，检查是否为字典
        print(f"coverage_improvement type: {type(coverage_improvement)}")
        print(f"coverage_improvement: {coverage_improvement}")
        # Calculate incremental coverage reward
        incremental_reward = sum(coverage_improvement.values()) / len(coverage_improvement)

        # Calculate top function focus reward
        top_function_reward = 0.0
        beta_weights = [5, 3, 3, 2, 2]  # Weights for top 5 functions
        for i, func in enumerate(self.top_functions[:5]):
            if func in coverage_improvement:
                top_function_reward += beta_weights[i] * coverage_improvement[func]

        # Calculate new feature discovery reward
        new_feature_reward = 0.0
        for func, improvement in coverage_improvement.items():
            if func not in self.previous_coverage and improvement > 0:
                # Estimate rank based on function name depth
                rank = func.count('/') + func.count('\\')
                new_feature_reward += 0.1 * (rank ** 2) * improvement

        # Combine rewards with dynamic weights
        total_reward = (0.3 * incremental_reward +
                        0.3 * top_function_reward +
                        0.4 * new_feature_reward)

        return total_reward

import os

def main():
    simulator_path = input("请输入模拟器路径: ").strip()
    test_case_path = input("请输入测试用例路径: ").strip()

    if not os.path.exists(simulator_path):
        print(f"Error: Simulator not found at {simulator_path}")
        return
    if not os.path.exists(test_case_path):
        print(f"Error: Test case file not found at {test_case_path}")
        return

    coverage_parser = CoverageParser()
    log_file = coverage_parser.run_callgrind(simulator_path, test_case_path)

    if log_file:
        coverage_improvement = coverage_parser.parse_callgrind_output(log_file)
        reward = coverage_parser.calculate_reward(coverage_improvement)
        print(f"Coverage improvement: {coverage_improvement}")
        print(f"Total reward: {reward}")
    else:
        print("Failed to generate Callgrind report.")

if __name__ == "__main__":
    main()