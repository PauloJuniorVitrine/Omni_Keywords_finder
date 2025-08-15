import os
import shutil
import tempfile
import pytest
from scripts import backup_restore
from typing import Dict, List, Optional, Any

@pytest.fixture
def temp_backup_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(backup_restore, 'BACKUP_DIR', str(tmp_path))
    return str(tmp_path)

@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b'data')
        yield f.name
    os.remove(f.name)

def test_backup_creates_zip(temp_backup_dir, monkeypatch):
    def fake_make_archive(base_name, format, root_dir=None, base_dir=None, **kwargs):
        zip_path = base_name + '.zip'
        with open(zip_path, 'wb') as f:
            f.write(b'FAKEZIP')
        return zip_path
    monkeypatch.setattr(shutil, 'make_archive', fake_make_archive)
    backup_restore.backup()
    files = os.listdir(backup_restore.BACKUP_DIR)
    assert any(f.endswith('.zip') for f in files)

def test_restore_file_not_found(temp_backup_dir, capsys):
    backup_restore.restore('inexistente.zip')
    out = capsys.readouterr().out
    assert 'Arquivo não encontrado' in out

def test_listar_backups(temp_backup_dir, monkeypatch, capsys):
    # Cria arquivo fake
    path = os.path.join(backup_restore.BACKUP_DIR, 'fake.zip')
    with open(path, 'w') as f:
        f.write('value')
    backup_restore.listar()
    out = capsys.readouterr().out
    assert 'fake.zip' in out

class DummyFile:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def write(self, *args, **kwargs):
        pass
    def read(self, *args, **kwargs):
        return "" 