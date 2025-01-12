"""
Core file system operations
"""

import tempfile
from datetime import datetime
from typing import List

from fastapi import UploadFile
from sqlalchemy.orm import Session

from db.conn import get_db
from db.models import File as DbFile


class FileStorage:
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())

    def save_file_content(self, file_content: bytes, path: str) -> DbFile:
        """Save file content to database"""
        file = UploadFile(filename=path, file=tempfile.SpooledTemporaryFile())
        file.file.write(file_content)
        file.file.seek(0)

        db_file = DbFile(
            filename=path,
            original_filename=path,
            content_type="application/octet-stream",
            file_size=len(file_content),
            file=file,
        )

        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def download_file(self, file_id: str) -> bytes:
        """Download file content from database"""
        file = self.db.query(DbFile).filter(DbFile.id == file_id).first()
        if not file:
            raise FileNotFoundError(f"File {file_id} not found")
        with file.file.open() as f:
            return f.read()

    def list_files(self) -> List[DbFile]:
        """List all files from database"""
        return self.db.query(DbFile).filter(DbFile.archived == False).all()

    def delete_file(self, file_id: str):
        """Delete file from database"""
        file = self.db.query(DbFile).filter(DbFile.id == file_id).first()
        if not file:
            raise FileNotFoundError(f"File {file_id} not found")
        file.archived = True
        file.archived_at = datetime.now()
        self.db.commit()
