import os
import re
import time
import openai
import random
import shutil
import argparse
import Levenshtein
from scripts.mutations import *
from scripts.reinforcement_learning import *
from scripts.differential_testing37_44 import differential_testing
from scripts.extract_error import extract_error_msg

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed_dir", type=str, help="Seed netlist directory",
                        default="/media/user/data/ljx/SpiceFuzz-main/data/seed_netlist/ngspice_test_circuits")
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
            f.close()
            with open(os.path.join(workdir, seed_names[j]), 'r') as f:
                str2 = f.read()
            f.close()
            weight = Levenshtein.distance(str1, str2)
            weight_sum += weight
            seed_weights[j] = (seed_weights[j] * (i - 1) + weight) / i
        seed_weights.append(weight_sum / i)
    print(seed_weights)
    # initialize mutation rules and forms
    mutations = initialize_mutations()
    forms = initialize_forms()
    # initialize RL
    s_dim = len(mutations)
    a_dim = len(mutations)
    net = Net(s_dim, a_dim)
    optim = torch.optim.Adam(net.parameters(), lr=args.lr)
    init_stat = np.ones(len(mutations))
    weight_sum = 0
    for i in range(len(seed_weights)):
        weight_sum += seed_weights[i]
    pre_instant_score = weight_sum / len(seed_weights)
    history_score = []
    for i in range(len(mutations)):
        history_score.append([0, 0])
    # [a, b] a:times the mutation is selected, b: the mutation score
    buffer_s = []
    buffer_a = []
    buffer_r = []
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
        print("---------------------")
        seed_name = random.choice(seed_names)
        print("Selected seed netlist:\n" + seed_name)
        optim.zero_grad()
        mutation_no = net.choose_action(v_wrap(init_stat[None, :]))
        mutation_no = mutation_no.numpy()[0]
        mutation = mutations[mutation_no]
        print("Selected mutation:\n" + mutation)
        with open(os.path.join(workdir, seed_name), 'r') as f:
            seed_lines = f.readlines()
        f.close()
        seed = ""
        for i in range(1, len(seed_lines)):
            seed += seed_lines[i].strip() + "\n"
        # Assembling prompt
        if 0 <= mutation_no <= 14:
            user_content = (
                "Please generate only one variant of the input spice netlist ```{}``` by {} and connecting to original nodes (make sure variant is valid and don't add additional comments). {}").format(
                seed, mutation, forms[mutation_no])
        elif 15 <= mutation_no <= 23:
            user_content = (
                "Please generate only one variant of the input spice netlist ```{}``` by {} (make sure variant is valid and don't add additional comments). {}").format(
                seed, mutation, forms[mutation_no])
        else:
            user_content = (
                "Please generate only one variant of the input spice netlist ```{}``` by {} (make sure variant is valid and don't add additional comments). And make sure the remaining elements can be connected together.").format(
                seed, mutation)
        # LLM
        messages = [{"role": "system",
                     "content": "You are an effective program mutator and your job is to generate a variant of the input code based on the specified instructions in the following."},
                    {"role": "user",
                     "content": user_content}]
        if error_msg != "":
            back_to_llm = ("The netlist you generated has a syntax error, and I got the error {} after simulating. "
                           "Please do not generate such netlist again").format(
                error_msg)
            messages.append({"role": "assistant", "content": back_to_llm})
        print("LLM input messages:\n" + str(messages))
        time_1 = time.time()
        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
        except openai.PermissionDeniedError as e:
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
        # Dealing with coding issues
        variant_content_code = variant_content.encode("gbk", errors="ignore")
        variant_content = variant_content_code.decode("gbk", errors="ignore")
        with open(variant_path, "w") as f:
            f.write(variant_content.replace("µ", "u"))
        f.close()
        # Delete blank lines and comments
        with open(variant_path, 'r') as f:
            lines = f.readlines()
        f.close()
        new_lines = []
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            if line.startswith("*"):
                continue
            index = line.find(";")
            if index != -1:
                line = line[:index].strip()
            new_lines.append(line)
        # Fix title line issues
        with open(variant_path, 'w') as f:
            if "spice" not in new_lines[0] and "plaintext" not in new_lines[0] and "SPICE" not in new_lines[
                0] and "PLAINTEXT" not in new_lines[0] and "netlist" not in new_lines[0] and "NETLIST" not in new_lines[
                0]:
                f.write("spice\n")
            for i in range(0, len(new_lines)):
                f.write(new_lines[i].strip() + "\n")
        f.close()
        time_2 = time.time()
        llm_time += time_2 - time_1
        total_num += 1
        buffer_a.append(mutation_no)
        run_results, compare_results = differential_testing(variant_path, variant_name, args.maxtime, args.error)
        time_3 = time.time()
        compare_time += time_3 - time_2
        
        # Initialize counters for categorization
        success_versions = sum(1 for status in run_results.values() if status == 0)
        failed_versions = sum(1 for status in run_results.values() if status == 1)
        timeout_versions = sum(1 for status in run_results.values() if status == 2)
        
        # Initialize flags for categorization
        has_inconsistency = any(result == 1 for result in compare_results.values())
        has_uncomparable = any(result == 2 for result in compare_results.values())
        all_consistent = all(result == 0 for result in compare_results.values())
        
        # Extract error messages from all failed versions
        error_msgs = {}
        for version, status in run_results.items():
            if status == 1:
                log_path = f"./test/ngspice{version}/{variant_name[:-4]}.log"
                error_msgs[version] = extract_error_msg(log_path)
        
        # Determine the category and save path
        old_path = "./test"
        if timeout_versions > 0:
            new_path = f"./result/ngspice_v/timeout/{variant_name[:-4]}"
            timeout_num += 1
        elif success_versions == 0:
            new_path = f"./result/ngspice_v/error/{variant_name[:-4]}"
            error_num += 1
        elif has_uncomparable:
            new_path = f"./result/ngspice_v/no_output/{variant_name[:-4]}"
            no_output_num += 1
        elif has_inconsistency:
            new_path = f"./result/ngspice_v/inconsistency/{variant_name[:-4]}"
            inconsistency_num += 1
        elif all_consistent and success_versions > 1:
            new_path = f"./result/ngspice_v/same/{variant_name[:-4]}"
            same_num += 1
        else:
            new_path = f"./result/ngspice_v/other/{variant_name[:-4]}"
        
        # Create directory and move files
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        shutil.move(old_path, new_path)
        shutil.copy(os.path.join(workdir, seed_name), os.path.join(new_path, seed_name))
        
        # Save test results
        with open(os.path.join(new_path, "test_results.txt"), "w") as f:
            f.write("Run Results:\n")
            for version, status in run_results.items():
                f.write(f"ngspice{version}: {status}\n")
            f.write("\nComparison Results:\n")
            for pair, result in compare_results.items():
                f.write(f"{pair}: {result}\n")
            if error_msgs:
                f.write("\nError Messages:\n")
                for version, msg in error_msgs.items():
                    f.write(f"ngspice{version}: {msg}\n")
        
        # Update success counter
        if success_versions > 0:
            success_num += 1
        
        # Add to seed netlist pool if all versions succeed and are consistent
        if success_versions == len(run_results) and all_consistent:
            seed_names.append(variant_name)
            init_stat[mutation_no] += 1
            weight_sum = 0
            for j in range(0, len(seed_weights)):
                with open(variant_path, 'r') as f:
                    str1 = f.read()
                f.close()
                with open(os.path.join(workdir, seed_names[j]), 'r') as f:
                    str2 = f.read()
                f.close()
                weight = Levenshtein.distance(str1, str2)
                weight_sum += weight
                seed_weights[j] = (seed_weights[j] * (len(seed_weights) - 1) + weight) / len(seed_weights)
            seed_weights.append(weight_sum / len(seed_weights))
            weight_sum = 0
            for i in range(len(seed_weights)):
                weight_sum += seed_weights[i]
            instantScore = weight_sum / len(seed_weights)
            instantReward = instantScore - pre_instant_score
        else:
            instantReward = 0
            os.remove(variant_path)
        
        # Update history scores and buffers
        history_score[mutation_no][1] = (instantReward + history_score[mutation_no][1] * history_score[mutation_no][0]) / (history_score[mutation_no][0] + 1)
        history_score[mutation_no][0] += 1
        buffer_r.append(history_score[mutation_no][1])
        buffer_s.append(init_stat)
        
        # Rest of the code remains the same
        v_s_ = net((v_wrap(init_stat[None, :])))[-1].data.numpy()[0, 0]
        buffer_v_target = []
        for r in buffer_r[::-1]:
            v_s_ = r + 0.9 * v_s_
            buffer_v_target.append(v_s_)
        buffer_v_target.reverse()
        
        loss = net.loss_func(
            v_wrap(np.vstack(buffer_s)),
            v_wrap(np.array(buffer_a)),
            v_wrap(np.array(buffer_v_target)[:, None]))
        loss.backward()
        optim.step()
        
        end_time = time.time()
        gap_time = end_time - start_time
    shutil.rmtree(workdir)
    print("total_num",total_num)
    print("success_num",success_num)
    print("same_num",same_num)
    print("inconsistency_num",inconsistency_num)
    print("no_output_num:",no_output_num)
    print("timeout_num",timeout_num)
    print("error_num",error_num)
    print("gap_time:",gap_time)
    print("llm_time",llm_time)
    print("compare_time",compare_time)
