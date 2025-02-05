import pytest
import os
import json
from pathlib import Path
from typing import Any, Tuple
from src.password_manager import PasswordManager, Password

@pytest.fixture  # type: ignore
def temp_db(tmp_path: Path) -> Tuple[str, str]:
    """创建临时数据库"""
    db_path = tmp_path / "test.db"
    key_path = tmp_path / "test.key"
    return str(db_path), str(key_path)

@pytest.fixture  # type: ignore
def password_manager(temp_db: Tuple[str, str]) -> PasswordManager:
    """创建密码管理器实例"""
    db_path, key_path = temp_db
    return PasswordManager(db_path=db_path, key_path=key_path)

class TestPasswordManager:
    def test_init(self, temp_db):
        """测试初始化"""
        db_path, key_path = temp_db
        pm = PasswordManager(db_path=db_path, key_path=key_path)
        
        assert os.path.exists(key_path)
        assert pm.key is not None
        assert pm.fernet is not None

    def test_generate_password(self, password_manager):
        """测试密码生成"""
        # 测试默认长度
        password = password_manager.generate_password()
        assert len(password) == 12
        
        # 测试指定长度
        password = password_manager.generate_password(length=16)
        assert len(password) == 16
        
        # 测试排除字符
        excluded = "@#$"
        password = password_manager.generate_password(excluded_chars=excluded)
        for char in excluded:
            assert char not in password

    def test_add_and_get_password(self, password_manager):
        """测试添加和获取密码"""
        account = "test@example.com"
        password = "TestPassword123!"
        note = "Test note"
        
        # 添加密码
        password_manager.add_password(account, password, note)
        
        # 获取密码
        passwords = password_manager.get_passwords()
        assert len(passwords) == 1
        
        stored = passwords[0]
        assert stored['account'] == account
        assert stored['password'] == password
        assert stored['note'] == note

    def test_search_password(self, password_manager):
        """测试搜索密码"""
        # 添加测试数据
        accounts = [
            ("test1@example.com", "pass1", "note1"),
            ("test2@example.com", "pass2", "note2"),
            ("other@gmail.com", "pass3", "note3")
        ]
        
        for account, password, note in accounts:
            password_manager.add_password(account, password, note)
        
        # 测试搜索
        results = password_manager.get_passwords(search_term="example.com")
        assert len(results) == 2
        
        results = password_manager.get_passwords(search_term="gmail")
        assert len(results) == 1

    def test_delete_password(self, password_manager):
        """测试删除密码"""
        # 添加测试数据
        password_manager.add_password("test@example.com", "password123", "note")
        
        # 获取ID
        passwords = password_manager.get_passwords()
        password_id = passwords[0]['id']
        
        # 测试删除
        assert password_manager.delete_password(password_id) is True
        assert len(password_manager.get_passwords()) == 0
        
        # 测试删除不存在的ID
        assert password_manager.delete_password(999) is False

    def test_export_import_passwords(self, password_manager, tmp_path):
        """测试导出和导入密码"""
        # 添加测试数据
        test_data = [
            ("test1@example.com", "pass1", "note1"),
            ("test2@example.com", "pass2", "note2")
        ]
        
        for account, password, note in test_data:
            password_manager.add_password(account, password, note)
        
        # 导出密码
        export_path = tmp_path / "export.json"
        password_manager.export_passwords(str(export_path))
        
        # 验证导出文件
        assert export_path.exists()
        with open(export_path) as f:
            exported = json.load(f)
            assert 'passwords' in exported
            assert 'key' in exported
            assert len(exported['passwords']) == 2
        
        # 创建新的管理器实例并导入
        new_db_path = tmp_path / "new.db"
        new_key_path = tmp_path / "new.key"
        new_pm = PasswordManager(str(new_db_path), str(new_key_path))
        
        new_pm.import_passwords(str(export_path))
        
        # 验证导入的数据
        imported = new_pm.get_passwords()
        assert len(imported) == 2
        
        # 验证导入的密码是否正确
        accounts = {p['account']: p['password'] for p in imported}
        for account, password, _ in test_data:
            assert account in accounts
            assert accounts[account] == password 