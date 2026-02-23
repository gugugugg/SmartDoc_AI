from diff_match_patch import diff_match_patch

class SemanticComparator:
    """
    语义差异比对模块
    负责计算文本间的细微差异并进行语义化清理。
    """
    def __init__(self):
        self.dmp = diff_match_patch()
        # 设置超时时间（秒），防止处理极大型文档时发生程序假死 [cite: 2026-02-21]
        self.dmp.Diff_Timeout = 5.0 

    def compare_texts(self, text_old, text_new):
        """
        计算两个文本之间的核心差异序列
        """
        diffs = self.dmp.diff_main(text_old, text_new)
        # 语义清理：将零散的字符变动合并为人类易读的语义块
        self.dmp.diff_cleanupSemantic(diffs)
        return diffs

    def format_diff_for_ai(self, diffs, limit=3000):
        """
        将原始差异数据转化为 AI 易读的标注文本格式
        """
        formatted_results = []
        char_count = 0
        for op, data in diffs:
            if op == 1: # 新增
                chunk = f"【内容增加】: {data}\n"
            elif op == -1: # 删除
                chunk = f"【内容删除】: {data}\n"
            else:
                continue # 忽略无变化内容以节省 Token 消耗

            formatted_results.append(chunk)
            char_count += len(chunk)
            
            # 截断保护：防止超过大模型单次处理的最大长度
            if char_count > limit:
                formatted_results.append("\n[...报告内容过长，后续差异已自动省略...]")
                break
        return "".join(formatted_results)