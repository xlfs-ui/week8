extract_action_items 完整函数（每行带注释）
import re
# 导入正则表达式模块re，用于文本匹配、分割和替换操作

# 定义行动项前缀元组，包含常见的待办/行动项标识前缀（不区分大小写，后续判断会统一转小写）
ACTION_PREFIXES = (
    "todo:",
    "action:",
    "task:",
    "next:",
    "to do:",
    "follow-up:",
)

# 定义行动项动词元组，包含常见的行动类动词（用于判断文本是否包含具体行动指令）
ACTION_VERBS = (
    "fix",          # 修复（问题、bug等）
    "implement",    # 实现（功能、需求等）
    "add",          # 添加（内容、功能等）
    "update",       # 更新（内容、版本等）
    "refactor",     # 重构（代码等）
    "write",        # 编写（文档、代码等）
    "test",         # 测试（功能、代码等）
    "deploy",       # 部署（项目、代码等）
    "review",       # 审核、评审（文档、代码等）
    "send",         # 发送（邮件、文件等）
    "prepare",      # 准备（材料、方案等）
    "follow up",    # 跟进（事项、需求等）
    "handle",       # 处理（问题、任务等）
    "resolve",      # 解决（问题、冲突等）
    "close",        # 关闭（任务、工单等）
    "investigate",  # 调查、排查（问题等）
    "coordinate",   # 协调（资源、人员等）
    "document",     # 记录、文档化（内容、流程等）
)

# 定义日期相关正则表达式，用于匹配文本中的日期/时间标识（不区分大小写）
DATE_PATTERN = re.compile(
    r"\b(?:by|before|due|today|tomorrow|this week)\b|\b\d{4}-\d{1,2}-\d{1,2}\b|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b",
    re.IGNORECASE,
)
# 正则说明：
# 1. \b(?:by|before|due|today|tomorrow|this week)\b：匹配常见时间关键词（截止、之前、今天、明天、本周）
# 2. \b\d{4}-\d{1,2}-\d{1,2}\b：匹配YYYY-MM-DD格式日期（如2026-05-01）
# 3. \b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b：匹配MM/DD或MM/DD/YYYY格式日期（如05/01、05/01/2026）
# 4. re.IGNORECASE：忽略大小写匹配

# 定义负责人相关正则表达式，用于匹配文本中的负责人标识（不区分大小写）
ASSIGNEE_PATTERN = re.compile(r"@\w+|owner\s*[:=]|assignee\s*[:=]", re.IGNORECASE)
# 正则说明：
# 1. @\w+：匹配@开头的用户名（如@user123）
# 2. owner\s*[:=]：匹配owner:、owner=及中间带空格的情况（如owner: 张三、owner = 李四）
# 3. assignee\s*[:=]：匹配assignee:、assignee=及中间带空格的情况
# 4. re.IGNORECASE：忽略大小写匹配

# 定义列表/复选框正则表达式，用于匹配列表项或复选框格式的文本
CHECKBOX_OR_LIST_PATTERN = re.compile(r"^\s*(?:[-*]\s+|\d+[.)]\s+|\[[ xX]\]\s+)")
# 正则说明：
# 1. ^\s*：匹配行首任意空白字符（空格、制表符等）
# 2. (?:[-*]\s+)：匹配短横线/星号开头的无序列表（如- 任务、* 任务）
# 3. \d+[.)]\s+：匹配数字开头的有序列表（如1. 任务、2) 任务）
# 4. \[[ xX]\]\s+：匹配复选框（如[ ] 任务、[x] 任务、[X] 任务）


def _split_candidates(text: str) -> list[str]:
    # 辅助函数：将输入文本分割成多个候选片段，用于后续判断是否为行动项
    # 参数text：输入的原始文本（字符串类型）
    # 返回值：候选片段列表（字符串列表）
    candidates: list[str] = []  # 初始化候选片段列表，用于存储分割后的有效片段
    for raw_line in text.splitlines():  # 按行分割原始文本，遍历每一行
        line = raw_line.strip()  # 去除当前行首尾的空白字符（空格、换行符等）
        if not line:  # 如果当前行去除空白后为空（空行），跳过当前循环
            continue

        # 用分号、句号、感叹号分割当前行，得到多个片段（行动项可能被标点分割在同一行）
        for segment in re.split(r"[;.!]", line):
            cleaned = segment.strip()  # 去除每个片段首尾的空白字符
            if cleaned:  # 如果片段去除空白后非空，添加到候选列表中
                candidates.append(cleaned)
    return candidates  # 返回分割后的所有有效候选片段


def _normalize_candidate(candidate: str) -> str:
    # 辅助函数：标准化候选片段，去除列表/复选框前缀，统一格式
    # 参数candidate：单个候选片段（字符串类型）
    # 返回值：标准化后的候选片段（字符串类型）
    # 用正则替换掉行首的列表/复选框前缀（无序列表、有序列表、复选框），再去除首尾空白
    return re.sub(r"^\s*(?:[-*]\s+|\d+[.)]\s+|\[[ xX]\]\s+)", "", candidate).strip()


def _score_actionability(candidate: str) -> int:
    # 辅助函数：给候选片段打分，判断其是否为行动项（分数越高，越可能是行动项）
    # 参数candidate：标准化后的候选片段（字符串类型）
    # 返回值：行动项评分（整数，分数越高，行动可能性越强）
    lowered = candidate.lower()  # 将候选片段转为全小写，用于不区分大小写的判断
    score = 0  # 初始化评分，默认为0分

    # 1. 若片段以行动项前缀开头，加4分（最高权重，最直接的行动项标识）
    if lowered.startswith(ACTION_PREFIXES):
        score += 4
    # 2. 若片段是列表/复选框格式，加2分（列表项常为待办/行动项）
    if CHECKBOX_OR_LIST_PATTERN.match(candidate):
        score += 2
    # 3. 若片段包含行动类动词，加2分（有具体行动指令）
    if any(verb in lowered for verb in ACTION_VERBS):
        score += 2
    # 4. 若片段包含日期/时间标识，加1分（有时间要求，更可能是行动项）
    if DATE_PATTERN.search(candidate):
        score += 1
    # 5. 若片段包含负责人标识，加1分（有明确负责人，更可能是行动项）
    if ASSIGNEE_PATTERN.search(candidate):
        score += 1
    # 6. 若片段以感叹号结尾、包含asap（尽快）或urgent（紧急），加1分（强调优先级，是行动项）
    if candidate.endswith("!") or "asap" in lowered or "urgent" in lowered:
        score += 1
    return score  # 返回当前候选片段的行动项评分


def _is_noise(candidate: str) -> bool:
    # 辅助函数：判断候选片段是否为无效噪音（非行动项）
    # 参数candidate：标准化后的候选片段（字符串类型）
    # 返回值：布尔值（True=噪音/非行动项，False=有效候选/可能是行动项）
    stripped = candidate.strip()  # 去除片段首尾空白
    lowered = stripped.lower()    # 转为全小写，用于不区分大小写判断

    # 1. 片段长度小于5个字符（过短，不可能是有效行动项），视为噪音
    if len(stripped) < 5:
        return True
    # 2. 片段以问号结尾（疑问句，不是行动指令），视为噪音
    if stripped.endswith("?"):
        return True
    # 3. 片段以note:、notes:开头（备注类内容，非行动项），视为噪音
    if lowered.startswith(("note:", "notes:")):
        return True
    return False  # 以上条件都不满足，视为有效候选


def extract_action_items(text: str) -> list[str]:
    # 主函数：从输入文本中提取行动项，返回去重后的有效行动项列表
    # 参数text：输入的原始文本（字符串类型）
    # 返回值：有效行动项列表（字符串列表，无重复）
    results: list[str] = []  # 初始化结果列表，用于存储最终提取的行动项
    seen: set[str] = set()   # 初始化集合，用于去重（存储已处理过的行动项特征）

    # 遍历所有候选片段（由_split_candidates函数分割得到）
    for candidate in _split_candidates(text):
        # 标准化候选片段，去除列表/复选框前缀
        normalized = _normalize_candidate(candidate)
        # 判断当前标准化后的片段是否为噪音，若是则跳过
        if _is_noise(normalized):
            continue

        # 计算当前片段的行动项评分
        score = _score_actionability(normalized)
        # 评分低于3分（行动可能性低），跳过当前片段
        if score < 3:
            continue

        # 生成去重键：去除多余空格、转为小写，确保不同格式的同一行动项被识别为重复
        dedupe_key = re.sub(r"\s+", " ", normalized).strip().lower()
        # 若去重键已在seen集合中（已处理过该行动项），跳过
        if dedupe_key in seen:
            continue

        # 将去重键加入seen集合，标记为已处理
        seen.add(dedupe_key)
        # 将标准化后的行动项加入结果列表
        results.append(normalized)

    return results  # 返回去重后的有效行动项列表