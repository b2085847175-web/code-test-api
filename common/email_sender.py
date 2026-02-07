"""
测试报告邮件发送模块
- 读取 Allure 报告摘要
- 将报告目录打包为 zip
- 构建 HTML 邮件（正文展示摘要 + 附件为 zip）
- 通过 163 邮箱 SMTP 发送
"""

import os
import json
import zipfile
import smtplib
import tempfile
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def _read_summary(report_dir):
    """读取 Allure 报告的 summary.json，提取测试摘要信息"""
    summary_path = os.path.join(report_dir, "widgets", "summary.json")
    if not os.path.exists(summary_path):
        print(f"[邮件] 未找到摘要文件: {summary_path}")
        return None

    with open(summary_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _format_duration(ms):
    """将毫秒转换为可读的时间格式"""
    if ms is None:
        return "未知"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f} 秒"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f} 分钟"
    hours = minutes / 60
    return f"{hours:.1f} 小时"


def _build_html_body(summary):
    """根据测试摘要构建 HTML 邮件正文"""
    if summary is None:
        return "<p>未能读取测试报告摘要，请查看附件中的完整报告。</p>"

    stat = summary.get("statistic", {})
    time_info = summary.get("time", {})

    passed = stat.get("passed", 0)
    failed = stat.get("failed", 0)
    broken = stat.get("broken", 0)
    skipped = stat.get("skipped", 0)
    total = stat.get("total", 0)
    duration = _format_duration(time_info.get("duration"))

    # 计算通过率
    pass_rate = f"{(passed / total * 100):.1f}%" if total > 0 else "N/A"

    # 整体状态判断
    if failed > 0 or broken > 0:
        status_text = "存在失败/异常"
        status_color = "#e74c3c"
    else:
        status_text = "全部通过"
        status_color = "#27ae60"

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: "Microsoft YaHei", Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px 30px;
            text-align: center;
        }}
        .header h2 {{
            margin: 0;
            font-size: 22px;
        }}
        .header p {{
            margin: 5px 0 0;
            font-size: 14px;
            opacity: 0.8;
        }}
        .status-bar {{
            background-color: {status_color};
            color: white;
            text-align: center;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        }}
        .content {{
            padding: 20px 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 10px 15px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #333;
        }}
        .passed {{ color: #27ae60; font-weight: bold; font-size: 18px; }}
        .failed {{ color: #e74c3c; font-weight: bold; font-size: 18px; }}
        .broken {{ color: #f39c12; font-weight: bold; font-size: 18px; }}
        .skipped {{ color: #95a5a6; font-weight: bold; font-size: 18px; }}
        .total {{ color: #2c3e50; font-weight: bold; font-size: 18px; }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .footer {{
            padding: 15px 30px;
            background-color: #f8f9fa;
            text-align: center;
            color: #888;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>API 自动化测试报告</h2>
            <p>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        <div class="status-bar">{status_text} | 通过率: {pass_rate}</div>
        <div class="content">
            <table>
                <tr>
                    <th>通过</th>
                    <th>失败</th>
                    <th>异常</th>
                    <th>跳过</th>
                    <th>总计</th>
                </tr>
                <tr>
                    <td class="passed">{passed}</td>
                    <td class="failed">{failed}</td>
                    <td class="broken">{broken}</td>
                    <td class="skipped">{skipped}</td>
                    <td class="total">{total}</td>
                </tr>
            </table>
            <p>执行耗时: <strong>{duration}</strong></p>
        </div>
        <div class="footer">
            完整 Allure 报告请查看附件，解压后打开 index.html 即可查看详情。
        </div>
    </div>
</body>
</html>
"""
    return html


def _zip_report(report_dir):
    """将 Allure 报告目录打包为 zip 文件，返回 zip 文件路径"""
    zip_path = os.path.join(tempfile.gettempdir(), "allure-report.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(report_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join("allure-report", os.path.relpath(file_path, report_dir))
                zf.write(file_path, arcname)

    print(f"[邮件] 报告已打包: {zip_path} ({os.path.getsize(zip_path) / 1024:.1f} KB)")
    return zip_path


def _build_subject(summary):
    """根据测试摘要构建邮件主题"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    if summary is None:
        return f"API自动化测试报告 - {date_str}"

    stat = summary.get("statistic", {})
    passed = stat.get("passed", 0)
    failed = stat.get("failed", 0)
    broken = stat.get("broken", 0)
    total = stat.get("total", 0)
    return f"API自动化测试报告 - {date_str} 通过: {passed}, 失败: {failed}, 异常: {broken}, 总计: {total}"


def send_test_report(
    report_dir,
    recipients,
    smtp_server="smtp.qq.com",
    smtp_port=465,
):
    """
    发送测试报告邮件

    参数:
        report_dir: Allure 报告目录路径 (reports/allure-report)
        recipients: 收件人邮箱列表，如 ["zhaowenlong@zhijianai.cn"]
        smtp_server: SMTP 服务器地址，默认 smtp.163.com
        smtp_port: SMTP 端口，默认 465 (SSL)
    """
    # 从环境变量读取发件人配置，未设置则使用默认值
    sender = os.environ.get("EMAIL_SENDER", "2085847175@qq.com")
    auth_code = os.environ.get("EMAIL_AUTH_CODE", "exooyaokaiptcadg")

    if not os.path.isdir(report_dir):
        print(f"[邮件] 错误: 报告目录不存在: {report_dir}")
        return False

    try:
        # 1. 读取测试摘要
        summary = _read_summary(report_dir)

        # 2. 构建邮件
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = _build_subject(summary)

        # 3. 添加 HTML 正文
        html_body = _build_html_body(summary)
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # 4. 打包报告并添加为附件
        zip_path = _zip_report(report_dir)
        with open(zip_path, "rb") as f:
            attachment = MIMEBase("application", "zip")
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename="allure-report.zip"
            )
            msg.attach(attachment)

        # 5. 发送邮件 (SSL)
        print(f"[邮件] 正在发送测试报告到: {', '.join(recipients)} ...")
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender, auth_code)
            server.sendmail(sender, recipients, msg.as_string())

        print("[邮件] 测试报告邮件发送成功!")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[邮件] 发送失败: SMTP 认证错误，请检查 EMAIL_SENDER 和 EMAIL_AUTH_CODE 是否正确")
        return False
    except smtplib.SMTPException as e:
        print(f"[邮件] 发送失败 (SMTP错误): {e}")
        return False
    except Exception as e:
        print(f"[邮件] 发送失败: {e}")
        return False
    finally:
        # 清理临时 zip 文件
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)
