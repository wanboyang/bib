#!/usr/bin/env python3
"""
BibTeX 引用验证和修正工具 - DeepSeek增强版
使用DeepSeek API进行引用格式验证
"""

import os
import re
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import urllib.parse
import urllib.request
import urllib.error
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deepseek_validation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeepSeekValidator:
    def __init__(self, api_key: str, proxy_url: Optional[str] = None, delay: float = 1.0):
        """
        初始化DeepSeek验证器
        
        Args:
            api_key: DeepSeek API密钥
            proxy_url: proxy URL (例如: http://127.0.0.1:10809)
            delay: 请求之间的延迟时间（秒）
        """
        self.api_key = api_key
        self.delay = delay
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
        if proxy_url:
            self._setup_proxy(proxy_url)
    
    def _setup_proxy(self, proxy_url: str):
        """设置proxy"""
        proxy_handler = urllib.request.ProxyHandler({
            'http': proxy_url,
            'https': proxy_url
        })
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
        logger.info(f"已设置proxy: {proxy_url}")
    
    def query_deepseek(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        查询DeepSeek API
        
        Args:
            prompt: 提示词
            max_tokens: 最大token数
            
        Returns:
            API响应内容或None
        """
        try:
            # 构建请求数据
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的学术引用验证专家。请严格分析BibTeX引用格式，提供准确的验证结果。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.1
            }
            
            # 添加延迟避免请求过快
            time.sleep(self.delay)
            
            # 发送请求
            request = urllib.request.Request(
                self.base_url,
                data=json.dumps(data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                    'User-Agent': 'BibTeX-Validator/1.0'
                }
            )
            
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
                
        except Exception as e:
            logger.error(f"DeepSeek API查询失败: {e}")
            return None
    
    def validate_bib_format(self, entry: Dict) -> Tuple[bool, str, Dict]:
        """
        使用DeepSeek验证BibTeX格式
        
        Args:
            entry: bib条目字典
            
        Returns:
            (是否有效, 验证信息, 修正建议)
        """
        entry_id = entry.get('ID', 'unknown')
        logger.info(f"使用DeepSeek验证条目: {entry_id}")
        
        # 构建验证提示词
        prompt = f"""
请分析以下BibTeX条目的格式正确性：

```bibtex
@article{{{entry_id},
  title = {{{entry.get('title', '')}}},
  author = {{{entry.get('author', '')}}},
  journal = {{{entry.get('journal', '')}}},
  year = {{{entry.get('year', '')}}},
  volume = {{{entry.get('volume', '')}}},
  number = {{{entry.get('number', '')}}},
  pages = {{{entry.get('pages', '')}}},
  doi = {{{entry.get('doi', '')}}}
}}
```

请按以下格式回复：
1. 格式正确性：是/否
2. 主要问题：列出发现的所有格式问题
3. 修正建议：提供具体的修正建议
4. 置信度：高/中/低

请严格分析以下方面：
- 必填字段是否完整（title, author, journal, year）
- 作者格式是否正确（使用"and"分隔）
- 期刊名称格式
- 年份格式（4位数字）
- 卷号格式（数字）
- 页码格式（正确使用连字符）
- DOI格式（以10.开头）
- 特殊字符转义
        """
        
        response = self.query_deepseek(prompt)
        if not response:
            return False, "DeepSeek API调用失败", {}
        
        # 解析响应
        is_valid = "格式正确性：是" in response
        corrections = self._parse_corrections(response)
        
        return is_valid, response, corrections
    
    def _parse_corrections(self, response: str) -> Dict:
        """解析DeepSeek的修正建议"""
        corrections = {}
        
        # 简单的关键词匹配来提取修正建议
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if '标题' in line.lower() and '建议' in line.lower():
                if ':' in line:
                    corrections['title'] = line.split(':', 1)[1].strip()
            elif '作者' in line.lower() and '建议' in line.lower():
                if ':' in line:
                    corrections['author'] = line.split(':', 1)[1].strip()
            elif '期刊' in line.lower() and '建议' in line.lower():
                if ':' in line:
                    corrections['journal'] = line.split(':', 1)[1].strip()
            elif '年份' in line.lower() and '建议' in line.lower():
                if ':' in line:
                    corrections['year'] = line.split(':', 1)[1].strip()
            elif '卷号' in line.lower() and '建议' in line.lower():
                if ':' in line:
                    corrections['volume'] = line.split(':', 1)[1].strip()
            elif '页码' in line.lower() and '建议' in line.lower():
                if ':' in line:
                    corrections['pages'] = line.split(':', 1)[1].strip()
            elif 'doi' in line.lower() and '建议' in line.lower():
                if ':' in line:
                    corrections['doi'] = line.split(':', 1)[1].strip()
        
        return corrections
    
    def compare_entries(self, original: Dict, corrected: Dict) -> Tuple[bool, str, Dict]:
        """
        比较原始条目和修正后的条目
        
        Args:
            original: 原始条目
            corrected: 修正后的条目
            
        Returns:
            (是否改进, 比较结果, 改进详情)
        """
        entry_id = original.get('ID', 'unknown')
        logger.info(f"比较条目改进: {entry_id}")
        
        # 构建比较提示词
        prompt = f"""
请比较以下两个BibTeX条目，判断修正后的版本是否比原始版本更好：

原始版本：
```bibtex
@article{{{entry_id},
  title = {{{original.get('title', '')}}},
  author = {{{original.get('author', '')}}},
  journal = {{{original.get('journal', '')}}},
  year = {{{original.get('year', '')}}},
  volume = {{{original.get('volume', '')}}},
  number = {{{original.get('number', '')}}},
  pages = {{{original.get('pages', '')}}},
  doi = {{{original.get('doi', '')}}}
}}
```

修正后版本：
```bibtex
@article{{{entry_id},
  title = {{{corrected.get('title', '')}}},
  author = {{{corrected.get('author', '')}}},
  journal = {{{corrected.get('journal', '')}}},
  year = {{{corrected.get('year', '')}}},
  volume = {{{corrected.get('volume', '')}}},
  number = {{{corrected.get('number', '')}}},
  pages = {{{corrected.get('pages', '')}}},
  doi = {{{corrected.get('doi', '')}}}
}}
```

请按以下格式回复：
1. 是否改进：是/否
2. 改进方面：列出具体改进的方面
3. 改进程度：显著/中等/轻微
4. 建议：进一步的改进建议
        """
        
        response = self.query_deepseek(prompt)
        if not response:
            return False, "DeepSeek API调用失败", {}
        
        # 解析响应
        is_improved = "是否改进：是" in response
        improvements = self._parse_improvements(response)
        
        return is_improved, response, improvements
    
    def _parse_improvements(self, response: str) -> Dict:
        """解析改进详情"""
        improvements = {}
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if '改进方面' in line and ':' in line:
                improvements['aspects'] = line.split(':', 1)[1].strip()
            elif '改进程度' in line and ':' in line:
                improvements['level'] = line.split(':', 1)[1].strip()
            elif '建议' in line and ':' in line:
                improvements['suggestions'] = line.split(':', 1)[1].strip()
        
        return improvements

class EnhancedBibValidator:
    def __init__(self, deepseek_api_key: Optional[str] = None, proxy_url: Optional[str] = None):
        """
        增强版BibTeX验证器
        
        Args:
            deepseek_api_key: DeepSeek API密钥（可选）
            proxy_url: proxy URL
        """
        self.deepseek_validator = None
        if deepseek_api_key:
            self.deepseek_validator = DeepSeekValidator(deepseek_api_key, proxy_url)
        
        self.proxy_url = proxy_url
    
    def validate_with_deepseek(self, original_file: str, corrected_file: str, output_file: str):
        """
        使用DeepSeek进行深度验证
        
        Args:
            original_file: 原始bib文件
            corrected_file: 修正后的bib文件
            output_file: 输出报告文件
        """
        if not self.deepseek_validator:
            logger.error("未提供DeepSeek API密钥")
            return
        
        # 读取原始文件
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 读取修正后文件
        with open(corrected_file, 'r', encoding='utf-8') as f:
            corrected_content = f.read()
        
        # 解析bib文件
        parser = BibTexParser()
        parser.ignore_nonstandard_types = False
        
        try:
            original_db = bibtexparser.loads(original_content, parser=parser)
            corrected_db = bibtexparser.loads(corrected_content, parser=parser)
        except Exception as e:
            logger.error(f"解析bib文件失败: {e}")
            return
        
        results = {
            'total_entries': len(original_db.entries),
            'format_validated': 0,
            'format_improved': 0,
            'comparison_results': []
        }
        
        # 验证每个条目
        for orig_entry, corr_entry in zip(original_db.entries, corrected_db.entries):
            entry_id = orig_entry.get('ID', 'unknown')
            logger.info(f"深度验证条目: {entry_id}")
            
            # 格式验证
            orig_valid, orig_validation, orig_corrections = self.deepseek_validator.validate_bib_format(orig_entry)
            corr_valid, corr_validation, corr_corrections = self.deepseek_validator.validate_bib_format(corr_entry)
            
            # 比较改进
            is_improved, comparison, improvements = self.deepseek_validator.compare_entries(orig_entry, corr_entry)
            
            results['comparison_results'].append({
                'id': entry_id,
                'original_validation': {
                    'valid': orig_valid,
                    'message': orig_validation,
                    'corrections': orig_corrections
                },
                'corrected_validation': {
                    'valid': corr_valid,
                    'message': corr_validation,
                    'corrections': corr_corrections
                },
                'improvement_analysis': {
                    'improved': is_improved,
                    'message': comparison,
                    'details': improvements
                }
            })
            
            if corr_valid:
                results['format_validated'] += 1
            if is_improved:
                results['format_improved'] += 1
        
        # 生成报告
        self._generate_deepseek_report(results, output_file)
        
        logger.info(f"DeepSeek验证完成！格式验证通过: {results['format_validated']}/{results['total_entries']}, "
                   f"改进确认: {results['format_improved']}/{results['total_entries']}")
    
    def _generate_deepseek_report(self, results: Dict, output_file: str):
        """生成DeepSeek验证报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# DeepSeek BibTeX 深度验证报告\n\n")
            f.write(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 统计摘要\n")
            f.write(f"- 总条目数: {results['total_entries']}\n")
            f.write(f"- 格式验证通过: {results['format_validated']}\n")
            f.write(f"- 确认改进: {results['format_improved']}\n")
            f.write(f"- 改进率: {results['format_improved']/results['total_entries']*100:.1f}%\n\n")
            
            f.write("## 详细验证结果\n")
            for result in results['comparison_results']:
                f.write(f"### {result['id']}\n")
                
                f.write("#### 原始条目验证\n")
                f.write(f"- 格式正确: {'✓' if result['original_validation']['valid'] else '✗'}\n")
                f.write(f"- 验证结果: {result['original_validation']['message'][:200]}...\n")
                
                f.write("#### 修正后条目验证\n")
                f.write(f"- 格式正确: {'✓' if result['corrected_validation']['valid'] else '✗'}\n")
                f.write(f"- 验证结果: {result['corrected_validation']['message'][:200]}...\n")
                
                f.write("#### 改进分析\n")
                f.write(f"- 确认改进: {'✓' if result['improvement_analysis']['improved'] else '✗'}\n")
                f.write(f"- 分析结果: {result['improvement_analysis']['message'][:200]}...\n")
                
                f.write("\n---\n\n")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='DeepSeek增强版BibTeX验证工具')
    parser.add_argument('original', help='原始bib文件路径')
    parser.add_argument('corrected', help='修正后的bib文件路径')
    parser.add_argument('-o', '--output', help='输出报告文件路径', default='deepseek_validation_report.md')
    parser.add_argument('--api-key', help='DeepSeek API密钥', required=True)
    parser.add_argument('-p', '--proxy', help='proxy URL (例如: http://127.0.0.1:10809)')
    
    args = parser.parse_args()
    
    # 创建验证器
    validator = EnhancedBibValidator(deepseek_api_key=args.api_key, proxy_url=args.proxy)
    
    try:
        # 进行深度验证
        validator.validate_with_deepseek(args.original, args.corrected, args.output)
        print(f"DeepSeek验证报告已生成: {args.output}")
        
    except Exception as e:
        logger.error(f"DeepSeek验证失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
