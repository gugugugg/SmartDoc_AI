import os
from llama_cpp import Llama

class AIEngine:
    """
    本地 AI 推理引擎
    负责加载大语言模型并基于文档差异生成语义审计报告。
    """

    def __init__(self, model_path: str, n_ctx: int = 4096):
        """
        初始化 AI 引擎
        :param model_path: 本地模型文件路径 (.gguf 格式)
        :param n_ctx: 上下文窗口大小
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"未找到模型文件: {model_path}")

        # 针对本地高性能显卡进行优化配置
        # n_gpu_layers=-1 表示尝试将所有计算层卸载到显存以实现硬件加速
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,      
            n_ctx=n_ctx,
            n_batch=512,
            f16_kv=True,
            verbose=False         # 关闭底层冗余日志输出
        )

    def generate_diff_summary(self, diff_text: str) -> str:
        """
        根据差异序列生成深度的中文审计摘要
        :param diff_text: 格式化后的差异文本内容
        :return: 中文分析摘要
        """
        # 设置系统指令，规定 AI 的角色与输出规范
        system_content = (
            "你是一位资深的文档审计专家。请始终使用【中文】对两份文档间的变更进行深度总结。"
            "分析重点：1. 核心数值或限量指标变动；2. 操作规程或技术参数调整；3. 关键条款的逻辑变更。"
            "请忽略排版与空格变化，直接给出具备工业价值的分析报告。"
        )

        user_content = f"以下为提取的文档差异片段，请生成详细的中文审计摘要：\n\n{diff_text}"

        # 构造对话模型专用的提示词格式
        prompt = f"<|im_start|>system\n{system_content}<|im_end|>\n"
        prompt += f"<|im_start|>user\n{user_content}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"

        # 执行推理，设置低采样温度以保证输出的严谨性
        response = self.llm(
            prompt,
            max_tokens=1024,
            temperature=0.1,    
            stop=["<|im_end|>"],
            echo=False
        )

        return response["choices"][0]["text"].strip()