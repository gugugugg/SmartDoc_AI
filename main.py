import os
import sys
import webbrowser

# 动态路径调整：确保程序能正确定位并加载 src 文件夹下的模块包
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn

# 模块导入：指向业务核心子目录
try:
    from src.ai_engine import AIEngine
    from src.doc_parser import DocumentParser        
    from src.doc_comparator import SemanticComparator 
    from src.visualizer import VisualDiffGenerator
except ImportError as e:
    print(f"致命错误：组件缺失，无法加载核心业务模块。错误详情: {e}")
    sys.exit(1)

console = Console()

class SmartDocApp:
    """
    SmartDoc-AI 主应用程序类
    集成解析、比对、渲染与 AI 分析的全流程调度。
    """
    def __init__(self):
        self.input_dir = "input"
        self.output_dir = "output"
        self.model_path = "models/Qwen2.5-7B-Instruct-abliterated-v2.Q6_K.gguf"
        
        self.parser = DocumentParser()
        self.comparator = SemanticComparator()
        self.visualizer = VisualDiffGenerator(self.output_dir)
        self.ai = None # 延迟加载模型以优化初期系统资源占用

        # 确保基础工作环境目录完整
        for d in [self.input_dir, self.output_dir, "models"]:
            if not os.path.exists(d): os.makedirs(d)

    def _get_files(self):
        """扫描输入目录中的合法文档"""
        return [f for f in os.listdir(self.input_dir) if f.lower().endswith(('.pdf', '.docx'))]

    def _ensure_ai(self):
        """确保推理引擎已按需初始化"""
        if not self.ai:
            with console.status("[bold green]正在激活本地 AI 分析内核..."):
                self.ai = AIEngine(self.model_path)

    def run(self):
        """运行交互式控制台菜单"""
        while True:
            console.print("\n")
            console.print(Panel.fit(
                "SmartDoc-AI 智能分析系统\n"
                "--------------------------------\n"
                "[1] 文档结构化转换 (PDF/Word -> Markdown)\n"
                "[2] 多模态比对分析 (视觉高亮 + AI 审计)\n"
                "[Q] 退出程序",
                title="本地分析环境",
                border_style="bold blue",
                subtitle="本地硬件加速驱动已就绪"
            ))
            
            cmd = Prompt.ask("请键入操作代码", choices=["1", "2", "q", "Q"])
            
            if cmd == "1":
                self.handle_convert()
            elif cmd == "2":
                self.handle_compare()
            else:
                console.print("[yellow]正在安全关闭程序，缓存已释放。")
                break

    def handle_convert(self):
        """处理文档解析与结构化转换任务"""
        files = self._get_files()
        if not files:
            console.print("[red]input/ 目录为空，请先载入待处理文件。[/]")
            return

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("[cyan]正在进行深度解析...", total=len(files))
            for f in files:
                md = self.parser.parse_to_markdown(os.path.join(self.input_dir, f))
                with open(os.path.join(self.output_dir, f"{f}.md"), "w", encoding="utf-8") as out:
                    out.write(md)
                progress.update(task, advance=1, description=f"[green]已完成: {f}")

    def handle_compare(self):
        """处理差异对比、可视化生成与 AI 摘要任务"""
        files = self._get_files()
        if len(files) < 2:
            console.print("[red]进行差异比对至少需要两个 PDF 或 Word 文档。[/]")
            return
        
        # 渲染待选文件列表
        table = Table(title="待分析文档列表")
        table.add_column("索引", style="cyan")
        table.add_column("文件名", style="magenta")
        for i, f in enumerate(files): table.add_row(str(i), f)
        console.print(table)

        idx1 = IntPrompt.ask("选择【基准版本】", choices=[str(i) for i in range(len(files))])
        idx2 = IntPrompt.ask("选择【修订版本】", choices=[str(i) for i in range(len(files))])

        f1, f2 = files[idx1], files[idx2]
        
        with console.status("[bold yellow]正在提取多模态数据并对齐差异..."):
            # A. 语义内容提取
            t1 = self.parser.parse_to_markdown(os.path.join(self.input_dir, f1))
            t2 = self.parser.parse_to_markdown(os.path.join(self.input_dir, f2))
            # B. 渲染原始图像
            img1 = self.parser.render_pdf_pages(os.path.join(self.input_dir, f1), os.path.join(self.output_dir, "cache_old"))
            img2 = self.parser.render_pdf_pages(os.path.join(self.input_dir, f2), os.path.join(self.output_dir, "cache_new"))
            # C. 差异计算
            diffs = self.comparator.compare_texts(t1, t2)
            # D. 构建可视化页面
            html_p = self.visualizer.generate_html_diff(
                {'name': f1, 'images': img1, 'text_html': self._to_html(diffs, -1)},
                {'name': file2_name, 'images': img2, 'text_html': self._to_html(diffs, 1)},
                diffs
            )
            
        # E. AI 驱动的中文摘要报告
        self._ensure_ai()
        with console.status("[bold magenta]AI 正在生成深度中文审计报告..."):
            ai_input = self.comparator.format_diff_for_ai(diffs)
            report = self.ai.generate_diff_summary(ai_input)
        
        console.print(Panel(report, title="[bold green]AI 差异审计总结 (中文)[/]", border_style="green"))
        
        # 自动在默认浏览器中开启分析界面
        webbrowser.open(f"file:///{os.path.abspath(html_p)}")

    def _to_html(self, diffs, target_op):
        """内部辅助：将差异序列转译为带色彩高亮的 HTML 代码"""
        res = ""
        for op, data in diffs:
            clean_data = data.replace('\n', '<br>')
            if op == 0: res += clean_data
            elif op == target_op:
                cls = "ins" if op == 1 else "del"
                res += f'<span class="{cls}">{clean_data}</span>'
        return res

if __name__ == "__main__":
    # 以标准入口方式启动程序
    app = SmartDocApp()
    app.run()