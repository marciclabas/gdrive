from typing import TextIO
import asyncio
import os
import sys
from pydrive.drive import GoogleDrive, GoogleDriveFile
import gdriver as gd

def create_folder_sync(drive: GoogleDrive, name: str, *, parent_id: str) -> str:
  folder = drive.CreateFile({
    'title': name,
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [{'id': parent_id }]
  })
  folder.Upload()
  return folder['id']

async def create_folder(drive: GoogleDrive, name: str, *, parent_id: str) -> str:
  """Create a folder, returning its generated ID"""
  return await asyncio.to_thread(create_folder_sync, drive, name, parent_id=parent_id)

async def download_folder(
  drive: GoogleDrive, folder_id: str, *,
  dest: str, max_tasks: int = 10,
  logstream: TextIO | None = sys.stderr
):
  """Recursively download a folder
  - `folder_id`: as in `https://drive.google.com/drive/folders/<folder_id>`
  - `dest`: local directory to download to
  """
  semaphore = asyncio.Semaphore(max_tasks)

  async def _download_to(file: GoogleDriveFile, out: str):
    async with semaphore:
      if logstream: print(f'Downloading file: {file["title"]}', file=logstream)
      data = await gd.download_file(file)
      if logstream: print(f'Downloaded file: {out}', file=logstream)
    with open(out, 'wb') as f:
      f.write(data)


  async def rec(folder_id: str, dest: str):
    if logstream:
      print(f'Creating folder: {dest}', file=logstream)
    os.makedirs(dest, exist_ok=True)

    file_list = await gd.list_folder(drive, folder_id)

    tasks = []
    for file in file_list:
      if file['mimeType'] == 'application/vnd.google-apps.folder':
        new_dest = os.path.join(dest, file['title'])
        tasks.append(asyncio.create_task(rec(file['id'], new_dest)))
      else:
        tasks.append(asyncio.create_task(_download_to(file, os.path.join(dest, file['title']))))

    await asyncio.gather(*tasks)

  await rec(folder_id, dest)

async def upload_folder(
  drive: GoogleDrive, folder_id: str, *,
  src: str, logstream: TextIO | None = sys.stderr,
  max_tasks: int = 10,
):
  """Recursively upload a folder
  - `src`: local directory to upload
  """

  semaphore = asyncio.Semaphore(max_tasks)

  async def _create_folder(name: str, parent_id: str):
    async with semaphore:
      if logstream: print(f'Creating folder: {name}', file=logstream)
      id = await create_folder(drive, name, parent_id=parent_id)
      if logstream: print(f'Created folder: {name}', file=logstream)
      return id

  async def _upload_file(path: str, *, name: str, folder_id: str):
    async with semaphore:
      if logstream: print(f'Uploading file: {name}', file=logstream)
      with open(path, 'rb') as f:
        await gd.upload_file(drive, f, name=name, folder_id=folder_id)
      if logstream: print(f'Uploaded file: {name}', file=logstream)

  async def rec(*, path: str, parent_id: str, name: str | None = None):

    folder_id = parent_id if name is None else await _create_folder(name, parent_id)
    tasks = []

    for entry in os.scandir(path):
      if entry.is_dir():
        tasks.append(asyncio.create_task(rec(path=entry.path, name=entry.name, parent_id=folder_id)))
      elif entry.is_file():
        tasks.append(asyncio.create_task(_upload_file(entry.path, name=entry.name, folder_id=folder_id)))

    await asyncio.gather(*tasks)

  await rec(path=src, parent_id=folder_id)
  return folder_id