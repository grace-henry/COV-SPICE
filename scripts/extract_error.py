def extract_error_msg(log_path):
    with open(log_path, 'r') as f:
        log_lines = f.readlines()
    f.close()
    error_msg = ""
    for i in range(len(log_lines)):
        if "error" in log_lines[i]:
            index = log_lines[i].find("error")
            new_index = log_lines[i].find(";")
            if new_index != -1:
                error_msg = log_lines[i][index:new_index]
            else:
                error_msg = log_lines[i][index:]
            break
    return error_msg


# def extract_error_msg_xyce(log_path):
#     with open(log_path, 'r') as f:
#         log_lines = f.readlines()
#
#     error_msg = ""
#     for line in log_lines:
#         if "*** Xyce Abort ***" in line:  # 查找包含 "Xyce Abort" 的行
#             error_msg = line.strip()  # 去除多余的空格
#             break  # 找到第一个包含错误信息的行就停止
#
#     return error_msg if error_msg else None  # 如果没有找到错误信息，返回 None
def extract_error_msg_xyce(log_path, context_lines=3):
    with open(log_path, 'r') as f:
        log_lines = f.readlines()

    error_msg = None
    error_context = []

    for i, line in enumerate(log_lines):
        if "*** Xyce Abort ***" in line:  # 查找包含 "Xyce Abort" 的行
            error_msg = line.strip()  # 去除多余的空格
            # 提取错误前后的上下文
            start = max(i - context_lines, 0)
            end = min(i + context_lines + 1, len(log_lines))
            error_context = log_lines[start:end]
            break  # 找到第一个包含错误信息的行就停止

    # 返回错误信息和上下文，若没有找到错误，则返回 None
    return error_msg, error_context if error_msg else None, None
