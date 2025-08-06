from scripts.CoverageParser import CoverageParser
import numpy as np
import math
class MAB:
    def __init__(self, num_arms, mutations,  test_case_path, exploration_weight=1.0):
        self.num_arms = num_arms
        self.mutations = mutations  # 突变列表
        self.simulator_path = "ngspice44" # 模拟器路径
        self.test_case_path = test_case_path  # 测试用例路径
        self.exploration_weight = exploration_weight
        self.pulls = np.zeros(num_arms)
        self.coverage_rewards = np.zeros(num_arms)
        self.total_pulls = 0
        self.coverage_parser = CoverageParser()  # 创建 CoverageParser 实例

    def select_arm(self):
        """Select an arm using UCB algorithm with coverage rewards"""
        # 如果有未被拉取的臂，优先选择
        for arm in range(self.num_arms):
            if self.pulls[arm] == 0:
                return arm

        # 计算 UCB 分数
        ucb_scores = np.zeros(self.num_arms)
        for arm in range(self.num_arms):
            exploitation = self.coverage_rewards[arm] / self.pulls[arm]
            exploration = math.sqrt(2 * math.log(self.total_pulls) / self.pulls[arm])
            ucb_scores[arm] = exploitation + self.exploration_weight * exploration

        return np.argmax(ucb_scores)

    def update(self, arm, reward, execution_success=True):
        """Update the bandit with feedback after pulling an arm"""

        self.pulls[arm] += 1
        self.total_pulls += 1

        # 只有执行成功时才更新奖励
        if execution_success:
            self.coverage_rewards[arm] = (self.coverage_rewards[arm] * (self.pulls[arm] - 1) +
                                          reward) / self.pulls[arm]
        print(f"Updated reward for arm {arm}: {self.coverage_rewards[arm]}")

    def run_mutation(self, arm):
        """执行与突变相关的操作，并计算覆盖率改进奖励"""
        selected_mutation = self.mutations[arm]
        print(f"Executing mutation: {selected_mutation}")

        # 执行模拟器并获取覆盖率数据
        log_file = self.coverage_parser.run_callgrind(self.simulator_path, self.test_case_path)

        if log_file:
            coverage_improvement = self.coverage_parser.parse_callgrind_output(log_file)
            return coverage_improvement
        else:
            print("Error: Callgrind report generation failed.")
            return {}
