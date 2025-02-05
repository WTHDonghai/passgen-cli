import string
import random
import json
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 定义基础类
Base = declarative_base()

class Password(Base):
    __tablename__ = 'passwords'
    
    id = Column(Integer, primary_key=True)
    account = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)
    note = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PasswordManager:
    def __init__(self, db_path: str = "passwords.db", key_path: str = "key.key") -> None:
        self.db_path = db_path
        self.key_path = Path(key_path)
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)
        
        # 初始化数据库
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.language = "en"  # 默认语言为英文

    def _load_or_generate_key(self) -> bytes:
        """加载或生成新的加密密钥"""
        if self.key_path.exists():
            return base64.urlsafe_b64decode(self.key_path.read_bytes())
        
        key = Fernet.generate_key()
        self.key_path.write_bytes(base64.urlsafe_b64encode(key))
        return key

    def generate_password(self, length: int = 12, exclude: str = "") -> str:
        """生成随机密码"""
        # 定义字符集
        chars = string.ascii_letters + string.digits + string.punctuation
        # 移除需要排除的字符
        for char in exclude:
            chars = chars.replace(char, '')
        
        # 生成密码
        return ''.join(random.choice(chars) for _ in range(length))

    def add_password(self, account: str, password: str, note: str = "") -> None:
        """添加新密码"""
        session = self.Session()
        try:
            encrypted_password = self.fernet.encrypt(password.encode()).decode()
            new_password = Password(
                account=account,
                encrypted_password=encrypted_password,
                note=note
            )
            session.add(new_password)
            session.commit()
        finally:
            session.close()

    def get_passwords(self, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有密码"""
        session = self.Session()
        try:
            query = session.query(Password)
            if search_term:
                query = query.filter(Password.account.like(f'%{search_term}%'))
            
            passwords = []
            for p in query.all():
                decrypted_password = self.fernet.decrypt(p.encrypted_password.encode()).decode()
                passwords.append({
                    'id': p.id,
                    'account': p.account,
                    'password': decrypted_password,
                    'note': p.note,
                    'created_at': p.created_at,
                    'updated_at': p.updated_at
                })
            return passwords
        finally:
            session.close()

    def delete_password(self, password_id: int) -> bool:
        """删除密码"""
        session = self.Session()
        try:
            password = session.query(Password).filter_by(id=password_id).first()
            if password:
                session.delete(password)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def export_passwords(self, export_path: str) -> None:
        """导出密码文件，只保持密码字段加密"""
        session = self.Session()
        try:
            # 获取所有记录，只保持密码字段加密
            passwords = []
            for p in session.query(Password).all():
                passwords.append({
                    'id': p.id,
                    'account': p.account,
                    'encrypted_password': p.encrypted_password,  # 保持密码字段加密
                    'note': p.note,
                    'created_at': p.created_at.isoformat(),
                    'updated_at': p.updated_at.isoformat()
                })
            
            # 直接写入 JSON 文件
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(passwords, f, ensure_ascii=False, indent=2)
        finally:
            session.close()

    def import_passwords(self, import_path: str) -> None:
        """导入密码，所有记录作为新数据添加"""
        with open(import_path, 'r', encoding='utf-8') as f:
            passwords = json.load(f)
        
        session = self.Session()
        try:
            current_time = datetime.utcnow()
            for p in passwords:
                # 为导入的每条记录生成新的记录，使用当前时间
                new_password = Password(
                    account=p['account'],
                    encrypted_password=p['encrypted_password'],  # 保持密码的加密状态
                    note=p.get('note', ''),
                    created_at=current_time,
                    updated_at=current_time
                )
                session.add(new_password)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"导入过程中出错: {str(e)}")
        finally:
            session.close()

    def clear_all_passwords(self) -> bool:
        """清空所有密码"""
        session = self.Session()
        try:
            session.query(Password).delete()
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def get_text(self, key):
        """获取当前语言的文本"""
        from .languages import TRANSLATIONS
        return TRANSLATIONS[self.language][key]
    
    def set_language(self, lang):
        """设置语言"""
        from .languages import TRANSLATIONS
        if lang in TRANSLATIONS:
            self.language = lang
            return True
        return False