from typing_extensions import TypedDict, TextIO, BinaryIO
import sys
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from oauth2client.client import GoogleCredentials
import gdriver as gd

class Credentials(TypedDict):
  access_token: str
  client_id: str
  client_secret: str
  refresh_token: str
  token_uri: str
  user_agent: str

class Client:
  """Google Drive client"""
  def __init__(self, credentials: Credentials):
    """- `credentials`: credentials JSON"""
    auth = GoogleAuth()
    auth.credentials = GoogleCredentials(
      access_token=credentials['access_token'],
      client_id=credentials['client_id'],
      client_secret=credentials['client_secret'],
      refresh_token=credentials['refresh_token'],
      token_expiry=None,
      token_uri=credentials['token_uri'],
      user_agent=credentials['user_agent']
    )
    self.client = GoogleDrive(auth)

  async def list_folder(self, folder_id: str = 'root'):
    """List files in a folder by ID, non-recursively
    - `folder_id`: from `https://drive.google.com/drive/folders/<folder_id>`
    """
    return await gd.list_folder(self.client, folder_id)
  
  async def download_file(self, file: 'gd.GoogleDriveFile') -> bytes:
    """Download a file"""
    return await gd.download_file(file)
  
  async def upload_file(self, data: BinaryIO, *, folder_id: str, name: str):
    """Upload a file"""
    await gd.upload_file(self.client, data, folder_id=folder_id, name=name)

  async def create_folder(self, name: str, *, parent_id: str = 'root') -> str:
    """Create a folder, returning its generated ID"""
    return await gd.create_folder(self.client, name, parent_id=parent_id)

  async def download_folder(
    self, folder_id: str, *, dest: str,
    max_tasks: int = 10, logstream: TextIO | None = sys.stderr
  ):
    """Recursively download a folder
    - `folder_id`: as in `https://drive.google.com/drive/folders/<folder_id>`
    """
    await gd.download_folder(self.client, folder_id, dest=dest, max_tasks=max_tasks, logstream=logstream)

  async def upload_folder(
    self, folder_id: str, *,
    src: str, logstream: TextIO | None = sys.stderr,
    max_tasks: int = 10,
  ) -> str:
    """Recursively upload a folder, returning its generated ID
    - `src`: local directory to upload
    """
    return await gd.upload_folder(self.client, folder_id, src=src, logstream=logstream, max_tasks=max_tasks)