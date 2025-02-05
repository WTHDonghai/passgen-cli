import pytest
from click.testing import CliRunner
from pathlib import Path
from src.cli import cli
import os
import json
from typing import Any, Generator
from src.password_manager import PasswordManager

@pytest.fixture  # type: ignore
def runner() -> CliRunner:
    """创建 CLI 测试运行器"""
    return CliRunner()

@pytest.fixture  # type: ignore
def isolated_runner(tmp_path: Path) -> Generator[CliRunner, None, None]:
    """创建带有隔离环境的测试运行器"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        yield runner

def test_generate_command(isolated_runner):
    """测试生成密码命令"""
    # 测试基本生成
    result = isolated_runner.invoke(cli, ['generate', '-a', 'test@example.com'])
    assert result.exit_code == 0
    assert '密码生成成功' in result.output
    
    # 测试指定长度
    result = isolated_runner.invoke(cli, ['generate', '-a', 'test@example.com', '-l', '16'])
    assert result.exit_code == 0
    
    # 测试排除字符
    result = isolated_runner.invoke(cli, ['generate', '-a', 'test@example.com', '-e', '@#$'])
    assert result.exit_code == 0

def test_list_command(isolated_runner):
    """测试列出密码命令"""
    # 测试空列表
    result = isolated_runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert '未找到任何密码记录' in result.output
    
    # 添加测试数据后再次测试
    isolated_runner.invoke(cli, ['generate', '-a', 'test@example.com'])
    result = isolated_runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'test@example.com' in result.output

def test_delete_command(isolated_runner):
    """测试删除密码命令"""
    # 先添加测试数据
    isolated_runner.invoke(cli, ['generate', '-a', 'test@example.com'])
    
    # 获取密码ID（通过list命令的输出）
    list_result = isolated_runner.invoke(cli, ['list'])
    assert 'ID: 1' in list_result.output
    
    # 测试删除
    result = isolated_runner.invoke(cli, ['delete', '1'], input='y\n')  # 添加确认输入
    assert result.exit_code == 0
    assert '成功删除' in result.output

def test_export_import_commands(isolated_runner, tmp_path):
    """测试导出和导入命令"""
    # 先添加测试数据
    isolated_runner.invoke(cli, ['generate', '-a', 'test@example.com'])
    
    # 测试导出
    export_path = tmp_path / "test_export.json"
    result = isolated_runner.invoke(cli, ['export', str(export_path)])
    assert result.exit_code == 0
    assert export_path.exists()
    
    # 测试导入
    result = isolated_runner.invoke(cli, ['import', str(export_path)])
    assert result.exit_code == 0
    assert '成功' in result.output

def test_interactive_mode(isolated_runner):
    """测试交互模式"""
    # 测试主菜单
    result = isolated_runner.invoke(cli, input='0\n')  # 选择退出
    assert result.exit_code == 0
    assert '密码管理器' in result.output
    
    # 测试生成密码
    result = isolated_runner.invoke(
        cli, 
        input='1\ntest@example.com\n16\n\n\ny\n0\n'
    )
    assert result.exit_code == 0
    assert '密码生成成功' in result.output 