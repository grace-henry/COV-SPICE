import os
import re
import time
import openai
import random
import shutil
import argparse
import Levenshtein
import numpy as np
from scripts.extract_error import extract_error_msg_xyce
from scripts.mutation_xyce import *
from scripts.differential_testing_xyce import differential_testing
from scripts.CoverageGuidedBandit import MAB
from scripts.CoverageParser import CoverageParser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed_dir", type=str, help="Seed netlist directory",
                        default="./data/seed_netlist/xyce1")
    parser.add_argument("--max_time", type=int, help="Fuzz running time",
                        default=86400)
    parser.add_argument('--lr', type=float, help="Learning rate",
                        default=0.01)
    parser.add_argument('--maxtime', type=int, help="Maximum time during simulation",
                        default=60)
    parser.add_argument('--error', type=str, help="Error when comparing raw files",
                        default="0.1")
    args = parser.parse_args()

    # move seed netlist to workdir
    workdir = "./netlist"
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    seed_names = []
    for filename in os.listdir(args.seed_dir):
        seed_names.append(filename)
        shutil.copy(os.path.join(args.seed_dir, filename), os.path.join(workdir, filename))

    # calculate seed netlist weight
    seed_weights = [0]
    for i in range(1, len(seed_names)):
        weight_sum = 0
        for j in range(0, i):
            with open(os.path.join(workdir, seed_names[i]), 'r') as f:
                str1 = f.read()
            with open(os.path.join(workdir, seed_names[j]), 'r') as f:
                str2 = f.read()
            weight = Levenshtein.distance(str1, str2)
            weight_sum += weight
            seed_weights[j] = (seed_weights[j] * (i - 1) + weight) / i
        seed_weights.append(weight_sum / i)
    print(seed_weights)

    # initialize mutation rules and forms
    mutations = initialize_mutations()
    forms = initialize_forms()

    # initialize MAB (Multi-Armed Bandit)
    mab = MAB(len(mutations),mutations,args.seed_dir)

    # initialize CoverageParser
    coverage_parser = CoverageParser()

    # initialize LLM
    base_url = "https://xiaoai.plus/v1"
    api_key = "sk-wTMrsN48TmTGNOjOjK6PUfHGwWtt2UZYQ5SqMkVypSs2h7Yf"
    client = openai.OpenAI(base_url=base_url, api_key=api_key)

    error_msg = ""

    # count
    total_num = 0
    success_num = 0
    same_num = 0
    inconsistency_num = 0
    no_output_num = 0
    timeout_num = 0
    error_num = 0
    llm_time = 0
    compare_time = 0

    # loop
    start_time = time.time()
    end_time = time.time()
    gap_time = end_time - start_time
    while gap_time < args.max_time:
        total_num += 1
        print("---------------------")
        seed_name = random.choice(seed_names)
        print("Selected seed netlist:\n" + seed_name)

        mutation_no = mab.select_arm()  # Select mutation strategy from MAB
        mutation = mutations[mutation_no]
        print("Selected mutation:\n" + mutation)
        print(f"mutation_no: {mutation_no}, mutations length: {len(mutations)}, forms length: {len(forms)}")
        with open(os.path.join(workdir, seed_name), 'r') as f:
            seed_lines = f.readlines()
        seed = "".join(line.strip() + "\n" for line in seed_lines[1:])

        # Prepare LLM prompt
        user_content = (
            "Please generate only one variant of the input spice netlist ```{}``` by {} and connecting to original nodes (make sure variant is valid and don't add additional comments). {}").format(
            seed, mutation, forms[mutation_no])

        # LLM interaction
        messages = [{"role": "system",
                     "content": "You are an effective program mutator and your job is to generate a variant of the input code based on the specified instructions in the following."},
                    {"role": "user",
                     "content": user_content}]

        if error_msg != "":
            back_to_llm = ("The netlist you generated has a syntax error, and I got the error {} after simulating. "
                           "Please do not generate such netlist again").format(error_msg)
            messages.append({"role": "assistant", "content": back_to_llm})

        print("LLM input messages:\n" + str(messages))
        time_1 = time.time()
        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                timeout=30  # 可选：设置请求超时时间（秒）
            )
        except openai.APIConnectionError as e:
            print("Connection error:", str(e))
            continue
        except openai.RateLimitError as e:
            print("Rate limit error:", str(e))
            time.sleep(10)  # 等待一下再继续
            continue
        except openai.APIError as e:
            print("OpenAI API error:", str(e))
            continue
        except Exception as e:
            print("Unexpected error during LLM call:", str(e))
            continue

        reply = chat_completion.choices[0].message.content
        print("LLM reply:\n" + reply)

        pattern = r"\`\`\`([\s\S]*?)\`\`\`"
        reply_blocks = re.findall(pattern, reply)
        if len(reply_blocks) == 0:
            continue
        variant_content = reply_blocks[0]
        print("Variant:\n", variant_content)

        variant_name = time.strftime('%Y%m%d%H%M%S', time.localtime()) + ".cir"
        variant_path = os.path.join(workdir, variant_name)

        # Write variant netlist to file
        variant_content_code = variant_content.encode("gbk", errors="ignore")
        variant_content = variant_content_code.decode("gbk", errors="ignore")
        with open(variant_path, "w") as f:
            f.write(variant_content.replace("µ", "u"))
        time_2 =time.time()
        # Run simulation and calculate coverage improvements
        run_results, compare_results = differential_testing(variant_path, variant_name, args.maxtime, args.error)
        coverage_data=None
        # 如果存在超时，跳过 coverage 分析
        if any(status == 2 for status in run_results.values()):
            print("Timeout occurred, skipping coverage analysis and reward calculation.")
        else:
            cov_path = coverage_parser.run_callgrind_xyce(variant_path)  # Run coverage analysis
            print("cov_path:",cov_path)
            # 获取覆盖率数据
            if cov_path is not None:
                coverage_data = coverage_parser.parse_callgrind_output(cov_path)
            else:
                print(f"跳过 coverage 分析，因为 cov_path 为 None")
                coverage_data = None

        # 如果 coverage_data 为空，跳过奖励计算和 MAB 更新
        if not coverage_data:
            print("No coverage data found, skipping analysis and reward calculation.")
        else:
            # Calculate reward based on coverage improvement
            reward = coverage_parser.calculate_reward(coverage_data)
            print(f"Calculated reward: {reward}")
            mab.update(mutation_no, reward)  # Update MAB with the calculated reward
        # else:
            # print("NGSpice simulation failed or differential testing did not pass, skipping coverage analysis.")

        time_3 = time.time()
        compare_time += time_3 - time_2

        # Categorize test results based on success/failure
        success_versions = sum(1 for status in run_results.values() if status == 0)
        failed_versions = sum(1 for status in run_results.values() if status == 1)
        timeout_versions = sum(1 for status in run_results.values() if status == 2)

        has_inconsistency = any(result == 1 for result in compare_results.values())
        has_uncomparable = any(result == 2 for result in compare_results.values())
        all_consistent = all(result == 0 for result in compare_results.values())

        # Extract error messages from failed versions
        # Extract error messages from failed versions
        error_msgs = {}
        for version, status in run_results.items():
            if status == 1:
                log_path = f"./test/{version}/{variant_name[:-4]}.log"
                if os.path.exists(log_path):
                    error_msgs[version] = extract_error_msg_xyce(log_path)
                else:
                    error_msgs[version] = "Log file not found."

        # Save the results to the appropriate directory based on test outcomes
        old_path = "./test"
        if timeout_versions > 0:
            new_path = f"./result/timeout/{variant_name[:-4]}"
            timeout_num += 1
        elif success_versions == 0:
            new_path = f"./result/error/{variant_name[:-4]}"
            error_num += 1
        elif has_uncomparable:
            new_path = f"./result/no_output/{variant_name[:-4]}"
            no_output_num += 1
        elif has_inconsistency:
            new_path = f"./result/inconsistency/{variant_name[:-4]}"
            inconsistency_num += 1
        elif all_consistent and success_versions > 1:
            new_path = f"./result/same/{variant_name[:-4]}"
            same_num += 1
        else:
            new_path = f"./result/other/{variant_name[:-4]}"

        # Create directory and move files
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        shutil.move(old_path, new_path)
        shutil.copy(os.path.join(workdir, seed_name), os.path.join(new_path, seed_name))

        # Save test results
        with open(os.path.join(new_path, "test_results.txt"), "w") as f:
            f.write("Run Results:\n")
            for version, status in run_results.items():
                f.write(f"{version}: {status}\n")
            f.write("\nComparison Results:\n")
            for pair, result in compare_results.items():
                f.write(f"{pair}: {result}\n")
            if error_msgs:
                f.write("\nError Messages:\n")
                for version, msg in error_msgs.items():
                    f.write(f"{version}: {msg}\n")

        # Update success counter
        if success_versions > 0:
            success_num += 1

        # Add to seed netlist pool if all versions succeed and are consistent
        if success_versions == len(run_results) and all_consistent:
            seed_names.append(variant_name)

        # Rest of the code remains the same for reinforcement learning and simulation
        end_time = time.time()
        gap_time = end_time - start_time

    shutil.rmtree(workdir)
    print("total_num", total_num)
    print("success_num", success_num)
    print("success rate:", success_num / total_num * 100, "%")
    print("same_num", same_num)
    print("inconsistency_num", inconsistency_num)
    print("no_output_num:", no_output_num)
    print("timeout_num", timeout_num)
    print("error_num", error_num)
    print("gap_time:", gap_time)
    print("llm_time", llm_time)
    print("compare_time", compare_time)