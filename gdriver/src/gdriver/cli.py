def main():
  from pydrive.auth import GoogleAuth
  gauth = GoogleAuth()
  gauth.LocalWebserverAuth()
  gauth.SaveCredentialsFile('credentials.json')
  print('Credentials saved to credentials.json')