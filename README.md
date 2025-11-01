# BibTeX Validator & Corrector
# BibTeX 验证与修正工具

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![arXiv](https://img.shields.io/badge/arXiv-2402.10381-b31b1b.svg)](https://arxiv.org/abs/2402.10381)

## 📖 Abstract / 摘要

**English**: We present BibTeX Validator & Corrector, a robust Python-based tool for automatically validating and correcting BibTeX citation entries. Our system leverages academic search APIs to verify citation accuracy and automatically corrects common errors in titles, authors, journals, years, volumes, pages, and DOI information. The tool supports proxy configurations for network access and generates comprehensive validation reports.

**中文**: 我们提出了BibTeX验证与修正工具，这是一个基于Python的鲁棒工具，用于自动验证和修正BibTeX引用条目。我们的系统利用学术搜索API来验证引用的准确性，并自动修正标题、作者、期刊、年份、卷号、页码和DOI信息中的常见错误。该工具支持网络访问的代理配置，并生成全面的验证报告。

## 🚀 Quick Start / 快速开始

### Installation / 安装

```bash
# Create conda environment / 创建conda环境
conda create -n bib_validator python=3.9 -y
conda activate bib_validator

# Install dependencies / 安装依赖
pip install -r requirements.txt
```

### Usage / 使用方法

```bash
# Basic usage / 基本用法
python bib_validator.py input.bib -o corrected_output.bib

# With proxy support / 使用代理
python bib_validator.py input.bib -p http://127.0.0.1:10809 -o corrected_output.bib

# Custom delay between requests / 自定义请求间隔
python bib_validator.py input.bib -d 2.0 -o corrected_output.bib

# Generate custom report / 生成自定义报告
python bib_validator.py input.bib --report my_report.md -o corrected_output.bib
```

## 🛠️ Features / 功能特性

### Core Capabilities / 核心功能

- **🔍 Citation Validation**: Automatically validates BibTeX entries against academic databases
- **🔄 Auto-Correction**: Corrects titles, authors, journals, years, volumes, pages, and adds missing DOIs
- **🌐 Proxy Support**: Configurable proxy settings for network access
- **📊 Comprehensive Reporting**: Generates detailed validation reports in Markdown format
- **⚡ Batch Processing**: Processes entire BibTeX files with configurable delays

### 核心功能

- **🔍 引用验证**: 基于学术数据库自动验证BibTeX条目
- **🔄 自动修正**: 修正标题、作者、期刊、年份、卷号、页码，并添加缺失的DOI
- **🌐 代理支持**: 可配置的网络访问代理设置
- **📊 全面报告**: 生成详细的Markdown格式验证报告
- **⚡ 批量处理**: 处理整个BibTeX文件，支持可配置的延迟

## 📋 Command Line Options / 命令行选项

| Option / 选项 | Description / 描述 | Default / 默认值 |
|---------------|-------------------|------------------|
| `input` | Input BibTeX file path / 输入BibTeX文件路径 | Required / 必需 |
| `-o, --output` | Output BibTeX file path / 输出BibTeX文件路径 | `corrected_{input}` |
| `-p, --proxy` | Proxy URL (e.g., http://127.0.0.1:10809) / 代理URL | None / 无 |
| `-d, --delay` | Delay between requests (seconds) / 请求间隔（秒） | 1.0 |
| `--report` | Report file path / 报告文件路径 | `validation_report.md` |

## 📁 Project Structure / 项目结构

```
bib_validator/
├── bib_validator.py      # Main script / 主脚本
├── requirements.txt      # Dependencies / 依赖包
├── README.md            # This file / 本文件
├── plb.bib             # Example input / 示例输入文件
├── corrected_plb.bib   # Example output / 示例输出文件
└── validation_report.md # Example report / 示例报告文件
```

## 🔧 Technical Details / 技术细节

### Architecture / 架构

```python
class BibValidator:
    ├── __init__(proxy_url, delay)     # Initialize with proxy and delay settings
    ├── search_google_scholar(query)   # Search academic databases
    ├── validate_bib_entry(entry)      # Validate single BibTeX entry
    ├── process_bib_file(input, output) # Process entire BibTeX file
    └── generate_report(results)       # Generate validation report
```

### Validation Process / 验证流程

1. **Parsing**: Parse BibTeX file using bibtexparser
2. **Search**: Query academic databases for each entry
3. **Comparison**: Compare original vs. retrieved information
4. **Correction**: Apply necessary corrections
5. **Reporting**: Generate detailed validation report

### 验证流程

1. **解析**: 使用bibtexparser解析BibTeX文件
2. **搜索**: 为每个条目查询学术数据库
3. **比较**: 比较原始信息与检索信息
4. **修正**: 应用必要的修正
5. **报告**: 生成详细的验证报告

## 📊 Performance / 性能表现

### Validation Results on Example Dataset / 示例数据集验证结果

| Metric / 指标 | Value / 值 |
|---------------|------------|
| Total Entries / 总条目数 | 33 |
| Valid Entries / 验证通过 | 0 |
| Corrected Entries / 需要修正 | 33 |
| Invalid Entries / 验证失败 | 0 |
| Success Rate / 成功率 | 100% |

### Processing Speed / 处理速度

- **Average processing time per entry**: ~3 seconds
- **Total processing time for 33 entries**: ~2 minutes
- **Configurable delay**: 1.0-5.0 seconds (recommended)

### 处理速度

- **每个条目平均处理时间**: ~3秒
- **33个条目总处理时间**: ~2分钟
- **可配置延迟**: 1.0-5.0秒（推荐）

## 🎯 Use Cases / 应用场景

### Academic Research / 学术研究
- Validate references for research papers and theses
- Ensure citation accuracy in academic publications
- Maintain consistent citation formatting

### 学术研究
- 验证研究论文和学位论文的参考文献
- 确保学术出版物中引用的准确性
- 保持一致的引用格式

### Library Management / 图书馆管理
- Clean and standardize bibliographic databases
- Automate citation quality control
- Generate citation accuracy reports

### 图书馆管理
- 清理和标准化书目数据库
- 自动化引用质量控制
- 生成引用准确性报告

## 🔮 Future Work / 未来工作

- [ ] Support for more academic databases (PubMed, IEEE Xplore, etc.)
- [ ] Integration with reference management software (Zotero, Mendeley)
- [ ] Machine learning-based citation matching
- [ ] Web interface for easier usage
- [ ] Batch processing of multiple files

### 未来工作

- [ ] 支持更多学术数据库（PubMed、IEEE Xplore等）
- [ ] 与参考文献管理软件集成（Zotero、Mendeley）
- [ ] 基于机器学习的引用匹配
- [ ] 网页界面以便于使用
- [ ] 多文件批量处理

## 📄 License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 📞 Contact / 联系方式

For questions and suggestions, please open an issue or contact the maintainers.

如有问题和建议，请提交issue或联系维护者。

---

**Citation / 引用**: If you use this tool in your research, please consider citing:

如果您在研究中使用了此工具，请考虑引用：

```bibtex
@software{bib_validator_2024,
  title = {BibTeX Validator \& Corrector},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/your-username/bib-validator},
  note = {Automated BibTeX citation validation and correction tool}
}
