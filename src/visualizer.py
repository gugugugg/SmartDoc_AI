import os

class VisualDiffGenerator:
    """
    可视化分析生成器
    负责构建侧边栏双视图对比的 HTML 报告。
    """
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def generate_html_diff(self, file1_data, file2_data, diff_report):
        """
        生成左右侧边栏布局的对比页面
        :param file1_data: 字典格式，包含原始文件的名称、图片列表及高亮文本
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>SmartDoc 文档比对可视化报告</title>
            <style>
                body {{ font-family: 'Segoe UI', 'PingFang SC', sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; background: #f0f2f5; }}
                .header {{ background: #24292e; color: white; padding: 15px; text-align: center; font-size: 1.2em; }}
                .main {{ display: flex; flex: 1; overflow: hidden; padding: 12px; gap: 12px; }}
                .pane {{ flex: 1; display: flex; flex-direction: column; background: white; border: 1px solid #d1d5da; border-radius: 6px; overflow: hidden; }}
                .pane-header {{ background: #f6f8fa; padding: 12px; font-weight: 600; border-bottom: 1px solid #d1d5da; }}
                .scroll {{ flex: 1; overflow-y: auto; padding: 20px; }}
                img {{ width: 100%; border: 1px solid #e1e4e8; margin-bottom: 15px; border-radius: 4px; }}
                .diff-area {{ margin-top: 20px; padding-top: 20px; border-top: 2px dashed #e1e4e8; line-height: 1.6; color: #24292e; }}
                .ins {{ background: #e6ffed; color: #22863a; border-bottom: 1px solid #22863a; text-decoration: none; }}
                .del {{ background: #ffeef0; color: #b31d28; text-decoration: line-through; }}
            </style>
        </head>
        <body>
            <div class="header">SmartDoc-AI 语义与原件多模态比对报告</div>
            <div class="main">
                <div class="pane">
                    <div class="pane-header">【基准版本】: {file1_data['name']}</div>
                    <div class="scroll">
                        {''.join([f'<img src="{img}">' for img in file1_data['images']])}
                        <div class="diff-area">{file1_data['text_html']}</div>
                    </div>
                </div>
                <div class="pane">
                    <div class="pane-header">【修订版本】: {file2_data['name']}</div>
                    <div class="scroll">
                        {''.join([f'<img src="{img}">' for img in file2_data['images']])}
                        <div class="diff-area">{file2_data['text_html']}</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        # 保存比对结果到输出目录
        output_path = os.path.join(self.output_dir, f"Analysis_{file1_data['name']}_VS_{file2_data['name']}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return output_path