# DeepSeek API 增强验证功能使用指南
# DeepSeek API Enhanced Validation Usage Guide

## 📖 概述 / Overview

**English**: This document describes how to use the DeepSeek API enhanced validation feature to perform deep analysis of BibTeX citation formats using large language models. The DeepSeek validator provides intelligent format validation and improvement analysis.

**中文**: 本文档介绍如何使用DeepSeek API增强验证功能，通过大语言模型对BibTeX引用格式进行深度分析。DeepSeek验证器提供智能格式验证和改进分析。

## 🚀 快速开始 / Quick Start

### 1. 获取DeepSeek API密钥 / Get DeepSeek API Key

1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册账户并登录
3. 在控制台中创建API密钥
4. 复制您的API密钥

1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Register an account and log in
3. Create an API key in the console
4. Copy your API key

### 2. 安装依赖 / Install Dependencies

```bash
# 激活虚拟环境 / Activate virtual environment
conda activate bib_validator

# 安装DeepSeek相关依赖 / Install DeepSeek dependencies
pip install -r requirements.txt
```

### 3. 使用方法 / Usage

```bash
# 基本用法 / Basic usage
python deepseek_validator.py plb.bib corrected_plb.bib --api-key YOUR_DEEPSEEK_API_KEY

# 使用代理 / With proxy
python deepseek_validator.py plb.bib corrected_plb.bib --api-key YOUR_DEEPSEEK_API_KEY -p http://127.0.0.1:10809

# 自定义输出文件 / Custom output file
python deepseek_validator.py plb.bib corrected_plb.bib --api-key YOUR_DEEPSEEK_API_KEY -o deepseek_report.md
```

## 🛠️ 功能特性 / Features

### 核心功能 / Core Capabilities

- **🔍 智能格式验证**: 使用DeepSeek分析BibTeX格式正确性
- **🔄 改进分析**: 比较原始和修正后条目的改进程度
- **📊 详细报告**: 生成包含格式验证和改进分析的详细报告
- **🌐 代理支持**: 支持代理配置，优化网络访问

### Core Capabilities

- **🔍 Intelligent Format Validation**: Use DeepSeek to analyze BibTeX format correctness
- **🔄 Improvement Analysis**: Compare improvement levels between original and corrected entries
- **📊 Detailed Reporting**: Generate comprehensive reports with format validation and improvement analysis
- **🌐 Proxy Support**: Support proxy configuration for optimized network access

## 🔧 技术细节 / Technical Details

### 验证流程 / Validation Process

1. **格式验证**: 对每个BibTeX条目进行格式正确性分析
2. **问题识别**: 识别必填字段、作者格式、期刊名称等问题
3. **修正建议**: 提供具体的格式修正建议
4. **改进比较**: 比较原始和修正后版本的改进程度

### Validation Process

1. **Format Validation**: Analyze format correctness for each BibTeX entry
2. **Issue Identification**: Identify issues with required fields, author format, journal names, etc.
3. **Correction Suggestions**: Provide specific format correction suggestions
4. **Improvement Comparison**: Compare improvement levels between original and corrected versions

### API调用分析 / API Call Analysis

每个条目的验证包含以下API调用：
- 1次原始条目格式验证
- 1次修正后条目格式验证
- 1次改进比较分析

**总API调用次数**: 3 × 条目数量

Each entry validation includes the following API calls:
- 1 original entry format validation
- 1 corrected entry format validation
- 1 improvement comparison analysis

**Total API calls**: 3 × number of entries

## 💰 成本估算 / Cost Estimation

DeepSeek API目前提供免费额度，具体定价请参考官方文档。

DeepSeek API currently offers free quotas. Please refer to official documentation for specific pricing.

## 📊 输出报告示例 / Output Report Example

```markdown
# DeepSeek BibTeX 深度验证报告

## 统计摘要
- 总条目数: 33
- 格式验证通过: 28
- 确认改进: 30
- 改进率: 90.9%

## 详细验证结果

### posebench2024

#### 原始条目验证
- 格式正确: ✗
- 验证结果: 标题格式需要改进，作者信息不完整...

#### 修正后条目验证
- 格式正确: ✓
- 验证结果: 格式正确，所有必填字段完整...

#### 改进分析
- 确认改进: ✓
- 分析结果: 修正后版本在标题格式、作者信息和DOI方面有显著改进...
```

## 🎯 使用场景 / Use Cases

### 学术研究 / Academic Research
- 验证论文参考文献格式的正确性
- 确保引用格式符合期刊要求
- 提供格式改进建议

### Academic Research
- Validate correctness of reference formats in research papers
- Ensure citation formats meet journal requirements
- Provide format improvement suggestions

### 质量控制 / Quality Control
- 自动化引用格式质量检查
- 批量验证大型文献数据库
- 生成格式合规性报告

### Quality Control
- Automated citation format quality checking
- Batch validation of large bibliographic databases
- Generate format compliance reports

## ⚠️ 注意事项 / Important Notes

1. **API限制**: 注意API调用频率限制，建议设置适当的延迟
2. **成本控制**: 监控API使用量，避免意外费用
3. **网络稳定性**: 确保网络连接稳定，建议使用代理
4. **数据隐私**: 注意敏感数据的处理

1. **API Limits**: Be aware of API rate limits, recommend setting appropriate delays
2. **Cost Control**: Monitor API usage to avoid unexpected charges
3. **Network Stability**: Ensure stable network connection, recommend using proxy
4. **Data Privacy**: Be cautious with sensitive data processing

## 🔮 未来改进 / Future Improvements

- [ ] 支持更多大语言模型（OpenAI、Claude等）
- [ ] 添加批量处理优化
- [ ] 实现缓存机制减少API调用
- [ ] 添加格式模板验证

- [ ] Support more LLMs (OpenAI, Claude, etc.)
- [ ] Add batch processing optimization
- [ ] Implement caching mechanism to reduce API calls
- [ ] Add format template validation

## 📞 技术支持 / Technical Support

如有问题，请提交GitHub Issue或联系维护者。

For issues, please submit a GitHub Issue or contact the maintainers.
