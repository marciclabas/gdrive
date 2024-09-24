# Google Driver

> Actually usable Google Drive client

Install with `pip install gdriver`

## Client from credentials

```python
import gdriver as gd

with open('credentials.json') as f:
  creds = json.load(f)
client = gd.Client(creds)
```

**How to get `credentials.json`?** See [below](#credentials)

## Recursive Upload/Download

```python
# `folder_id`, as in https://drive.google.com/drive/folders/<folder_id>
await client.download_folder('<folder_id>', dest='path/to/output')
```

```python
folder_id = await client.create_folder('new-folder-name', parent_id='<folder_id>')
await client.upload_folder(folder_id, src='path/to/folder')
```

## File Upload/Download/List

```python
import io
await client.upload_file(io.BytesIO(b'Hello, world!'), folder_id='<folder_id>', name='hello-world.txt')
await client.upload_file(open('image.jpg'), folder_id='<folder_id>', name='image.jpg')
```

```python
files = await client.list_files('<folder_id>')
data: bytes = await client.download_file(files[0])
```

## Credentials

1. Read [pydrive docs](https://pythonhosted.org/PyDrive/quickstart.html#authentication)
2. Copy `client_secrets.json` to the working directory
3. Run `gdrive-auth` (installed with the package), which will open a browser window, and save the credentials to `credentials.json`
