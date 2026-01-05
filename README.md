# EchoSim

<div align="center">

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAgents](https://img.shields.io/badge/Powered%20by-OpenAgents-orange.svg)](https://github.com/openagents)

</div>

EchoSim 是一个基于 OpenAgents 构建的自动化市场调研框架。它通过编排 MirrorSwarm（镜像集群）多智能体网络，模拟了从问卷设计、用户画像生成，到高保真填答模拟及自动化洞察抽取的完整调研生命周期。

## 🏗️ 架构概览

EchoSim 作为一个"虚拟市场调研团队"运行，采用混合编排模式，既保证了作业程序的规范性，又兼顾了 Agent 协作的灵活性。

**架构类型**: 流水线 + 星型协作

## 🤖 MirrorSwarm 智能体网络

| Agent | 角色 | 职责 |
|-------|------|------|
| Agent A | 调研架构师 (Survey Architect) | 理解人类需求，优化问卷逻辑，定义目标人群维度（年龄、职业、痛点等） |
| Agent B | 人格生成工厂 (Persona Factory) | 批量生产具有详细背景、性格偏好和生活状态的"合成用户画像" |
| Agent C | 虚拟受访者 (Synthetic Respondent) | 核心执行者。加载画像进入角色扮演模式，模拟特定角色的语气和认知偏差进行回答 |
| Agent D | 洞察分析师 (Insight Hunter) | 负责收集模拟数据，进行情感与聚类分析，输出最终分析报告 |

## 🚀 关键特性

- **标准作业程序 (SOP)**: 从需求输入到报告输出的全自动线性工作流
- **上下文注入**: 基于 JSON 的动态画像注入技术，确保 Agent C 的高保真角色扮演
- **全量反馈挖掘**: 内置插件支持爬取应用商店评论或读取本地 CSV/Excel 原始数据
- **结构化输出**: 强制输出标准 JSON 格式，确保调研结果可量化、可统计
- **大规模并发**: 利用 OpenAgents 并发能力，同时运行数百个虚拟受访者实例，模拟"千人千面"

## 🛠️ 快速上手

### 环境要求

- Python 3.8+
- OpenAgents 依赖

### 安装

```bash
git clone https://github.com/YourUsername/EchoSim.git
cd EchoSim
pip install -r requirements.txt
```

### 使用

```bash
python main.py --task "调研用户对折叠屏手机的购买意向"
```

## 📁 项目结构

```
EchoSim/
├── main.py              # 入口文件
├── requirements.txt     # 依赖列表
├── LICENSE              # MIT 许可证
└── README.md            # 项目说明文档
```

## 🤝 贡献

欢迎提交 Pull Request 或 Issue！

## 📝 许可证

本项目采用 MIT 许可证开源。

```
MIT License

Copyright (c) 2026 ZilongXiao-00

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
