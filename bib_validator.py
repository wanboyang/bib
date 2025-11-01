#!/usr/bin/env python3
"""
BibTeX 引用验证和修正工具
使用谷歌学术作为来源，支持proxy设置
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
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bib_validation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BibValidator:
    def __init__(self, proxy_url: Optional[str] = None, delay: float = 1.0):
        """
        初始化验证器
        
        Args:
            proxy_url: proxy URL (例如: http://127.0.0.1:8080)
            delay: 请求之间的延迟时间（秒）
        """
        self.delay = delay
        self.proxy_handler = None
        
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
        self.proxy_handler = proxy_handler
        logger.info(f"已设置proxy: {proxy_url}")
    
    def search_google_scholar(self, query: str) -> Optional[Dict]:
        """
        搜索谷歌学术（模拟API调用）
        注意：由于谷歌学术没有公开API，这里使用模拟搜索
        
        Args:
            query: 搜索查询
            
        Returns:
            搜索结果字典或None
        """
        try:
            # 模拟谷歌学术搜索
            encoded_query = urllib.parse.quote(query)
            
            # 这里使用Crossref API作为替代方案，因为谷歌学术没有公开API
            url = f"https://api.crossref.org/works?query={encoded_query}&rows=1"
            
            logger.info(f"搜索: {query}")
            
            # 添加延迟避免请求过快
            time.sleep(self.delay)
            
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data['message']['items']:
                    item = data['message']['items'][0]
                    return {
                        'title': item.get('title', [''])[0],
                        'authors': [author.get('given', '') + ' ' + author.get('family', '') 
                                   for author in item.get('author', [])],
                        'journal': item.get('container-title', [''])[0],
                        'year': item.get('published-print', {}).get('date-parts', [[None]])[0][0],
                        'volume': item.get('volume'),
                        'issue': item.get('issue'),
                        'pages': item.get('page'),
                        'doi': item.get('DOI'),
                        'url': item.get('URL')
                    }
            
            return None
            
        except Exception as e:
            logger.warning(f"搜索失败: {e}")
            return None
    
    def validate_bib_entry(self, entry: Dict) -> Tuple[bool, Dict, str]:
        """
        验证单个bib条目
        
        Args:
            entry: bib条目字典
            
        Returns:
            (是否有效, 修正后的条目, 验证信息)
        """
        entry_id = entry.get('ID', 'unknown')
        title = entry.get('title', '')
        authors = entry.get('author', '')
        journal = entry.get('journal', '')
        year = entry.get('year', '')
        
        logger.info(f"验证条目: {entry_id}")
        
        # 构建搜索查询
        search_query = f"{title} {authors} {journal} {year}"
        
        # 搜索验证
        search_result = self.search_google_scholar(search_query)
        
        if not search_result:
            return False, entry, "未找到匹配的文献"
        
        # 比较和修正
        corrections = {}
        validation_notes = []
        
        # 检查标题
        if title and search_result['title']:
            if not self._fuzzy_match(title, search_result['title']):
                corrections['title'] = search_result['title']
                validation_notes.append(f"标题不匹配: '{title}' -> '{search_result['title']}'")
        
        # 检查作者
        if authors and search_result['authors']:
            expected_authors = ' and '.join(search_result['authors'])
            if not self._author_match(authors, expected_authors):
                corrections['author'] = expected_authors
                validation_notes.append(f"作者信息需要更新")
        
        # 检查期刊
        if journal and search_result['journal']:
            if not self._fuzzy_match(journal, search_result['journal']):
                corrections['journal'] = search_result['journal']
                validation_notes.append(f"期刊名称更新: '{journal}' -> '{search_result['journal']}'")
        
        # 检查年份
        if year and search_result['year']:
            if str(year) != str(search_result['year']):
                corrections['year'] = str(search_result['year'])
                validation_notes.append(f"年份更新: {year} -> {search_result['year']}")
        
        # 检查卷号
        volume = entry.get('volume', '')
        if volume and search_result['volume']:
            if str(volume) != str(search_result['volume']):
                corrections['volume'] = str(search_result['volume'])
                validation_notes.append(f"卷号更新: {volume} -> {search_result['volume']}")
        
        # 检查页码
        pages = entry.get('pages', '')
        if pages and search_result['pages']:
            if pages != search_result['pages']:
                corrections['pages'] = search_result['pages']
                validation_notes.append(f"页码更新: {pages} -> {search_result['pages']}")
        
        # 添加DOI（如果缺失）
        if 'doi' not in entry and search_result['doi']:
            corrections['doi'] = search_result['doi']
            validation_notes.append(f"添加DOI: {search_result['doi']}")
        
        # 创建修正后的条目
        corrected_entry = entry.copy()
        corrected_entry.update(corrections)
        
        if corrections:
            validation_message = f"需要修正: {', '.join(validation_notes)}"
            return False, corrected_entry, validation_message
        else:
            return True, entry, "验证通过"
    
    def _fuzzy_match(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """模糊匹配文本"""
        import difflib
        text1_clean = re.sub(r'[^\w\s]', '', text1.lower())
        text2_clean = re.sub(r'[^\w\s]', '', text2.lower())
        similarity = difflib.SequenceMatcher(None, text1_clean, text2_clean).ratio()
        return similarity >= threshold
    
    def _author_match(self, authors1: str, authors2: str) -> bool:
        """比较作者列表"""
        def normalize_authors(authors_str):
            authors = [a.strip() for a in authors_str.split(' and ')]
            return sorted([re.sub(r'\s+', ' ', a) for a in authors])
        
        try:
            norm1 = normalize_authors(authors1)
            norm2 = normalize_authors(authors2)
            return norm1 == norm2
        except:
            return False
    
    def process_bib_file(self, input_file: str, output_file: Optional[str] = None) -> Dict:
        """
        处理整个bib文件
        
        Args:
            input_file: 输入bib文件路径
            output_file: 输出bib文件路径（可选）
            
        Returns:
            处理结果统计
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"文件不存在: {input_file}")
        
        # 读取bib文件
        with open(input_file, 'r', encoding='utf-8') as f:
            bib_content = f.read()
        
        # 解析bib文件
        parser = BibTexParser()
        parser.ignore_nonstandard_types = False
        parser.homogenize_fields = True
        
        try:
            bib_database = bibtexparser.loads(bib_content, parser=parser)
        except Exception as e:
            logger.error(f"解析bib文件失败: {e}")
            raise
        
        results = {
            'total_entries': len(bib_database.entries),
            'valid_entries': 0,
            'corrected_entries': 0,
            'invalid_entries': 0,
            'corrections': []
        }
        
        corrected_entries = []
        
        # 验证每个条目
        for entry in bib_database.entries:
            is_valid, corrected_entry, message = self.validate_bib_entry(entry)
            
            if is_valid:
                results['valid_entries'] += 1
                corrected_entries.append(entry)
                logger.info(f"✓ {entry['ID']}: {message}")
            else:
                if message.startswith("需要修正"):
                    results['corrected_entries'] += 1
                    corrected_entries.append(corrected_entry)
                    logger.info(f"⚠ {entry['ID']}: {message}")
                else:
                    results['invalid_entries'] += 1
                    corrected_entries.append(entry)  # 保留原始条目
                    logger.warning(f"✗ {entry['ID']}: {message}")
            
            results['corrections'].append({
                'id': entry['ID'],
                'valid': is_valid,
                'message': message,
                'corrections': corrected_entry if not is_valid else {}
            })
        
        # 保存修正后的文件
        if output_file:
            self._save_corrected_bib(corrected_entries, output_file)
            logger.info(f"修正后的文件已保存: {output_file}")
        
        return results
    
    def _save_corrected_bib(self, entries: List[Dict], output_file: str):
        """保存修正后的bib文件"""
        db = BibDatabase()
        db.entries = entries
        
        writer = BibTexWriter()
        writer.indent = '  '
        writer.comma_first = False
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(writer.write(db))
    
    def generate_report(self, results: Dict, report_file: str = "validation_report.md"):
        """生成验证报告"""
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# BibTeX 验证报告\n\n")
            f.write(f"**处理时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 统计摘要\n")
            f.write(f"- 总条目数: {results['total_entries']}\n")
            f.write(f"- 验证通过: {results['valid_entries']}\n")
            f.write(f"- 需要修正: {results['corrected_entries']}\n")
            f.write(f"- 验证失败: {results['invalid_entries']}\n\n")
            
            f.write("## 详细结果\n")
            for correction in results['corrections']:
                status = "✓" if correction['valid'] else "⚠" if correction['message'].startswith("需要修正") else "✗"
                f.write(f"### {status} {correction['id']}\n")
                f.write(f"- 状态: {correction['message']}\n")
                if correction['corrections']:
                    f.write("- 修正内容:\n")
                    for key, value in correction['corrections'].items():
                        f.write(f"  - {key}: {value}\n")
                f.write("\n")
        
        logger.info(f"验证报告已生成: {report_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='BibTeX 引用验证和修正工具')
    parser.add_argument('input', help='输入bib文件路径')
    parser.add_argument('-o', '--output', help='输出bib文件路径')
    parser.add_argument('-p', '--proxy', help='proxy URL (例如: http://127.0.0.1:8080)')
    parser.add_argument('-d', '--delay', type=float, default=1.0, 
                       help='请求之间的延迟时间（秒）')
    parser.add_argument('--report', help='报告文件路径', default='validation_report.md')
    
    args = parser.parse_args()
    
    # 创建验证器
    validator = BibValidator(proxy_url=args.proxy, delay=args.delay)
    
    try:
        # 处理bib文件
        output_file = args.output or f"corrected_{os.path.basename(args.input)}"
        results = validator.process_bib_file(args.input, output_file)
        
        # 生成报告
        validator.generate_report(results, args.report)
        
        # 输出摘要
        print("\n" + "="*50)
        print("验证完成!")
        print(f"总条目数: {results['total_entries']}")
        print(f"验证通过: {results['valid_entries']}")
        print(f"需要修正: {results['corrected_entries']}")
        print(f"验证失败: {results['invalid_entries']}")
        print(f"修正文件: {output_file}")
        print(f"报告文件: {args.report}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
