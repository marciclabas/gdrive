from typing import BinaryIO
import asyncio
from pydrive.drive import GoogleDrive, GoogleDriveFile

async def list_folder(drive: GoogleDrive, folder_id: str) -> list[GoogleDriveFile]:
  r = await asyncio.to_thread(drive.ListFile, {'q': f"'{folder_id}' in parents and trashed=false"})
  return r.GetList()

def download_file_sync(file: GoogleDriveFile) -> bytes:
  file.FetchContent()
  return file.content.getvalue() # type: ignore

async def download_file(file: GoogleDriveFile) -> bytes:
  return await asyncio.to_thread(download_file_sync, file)

def upload_file_sync(drive: GoogleDrive, data: BinaryIO, *, folder_id: str, name: str):
  file = drive.CreateFile({ 'title': name, 'parents': [{ 'id': folder_id }] })
  file.content = data
  file.Upload()

async def upload_file(drive: GoogleDrive, data: BinaryIO, *, folder_id: str, name: str):
  await asyncio.to_thread(upload_file_sync, drive, data, folder_id=folder_id, name=name)
