import string
import random
import json
import base64
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    def __init__(self, db_path: str = "passwords.db", key_path: str = "key.key"):
        self.db_path = db_path
        self.key_path = Path(key_path)
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)
        
        # 初始化数据库
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    # ... 其余 PasswordManager 类的方法保持不变 ... 