import json
import logging
import os.path
from typing import List, Optional, Union

from dotmap import DotMap
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from PIL import Image

# https://github.com/eshmu/gphotos-upload


def save_cred(cred, auth_file):
    if isinstance(cred, DotMap):
        cred_dict = {
            "token": cred.token,
            "refresh_token": cred.refresh_token,
            "id_token": cred.id_token,
            "scopes": cred.scopes,
            "token_uri": cred.token_uri,
            "client_id": cred.client_id,
            "client_secret": cred.client_secret,
        }
    else:
        cred_dict = cred

    with open(auth_file, "w") as f:
        print(json.dumps(cred_dict), file=f)

    return 1


class GooglePhotosClient:
    def __init__(
        self,
        scopes: List[str],
        scoped_credentials_file: str,
        client_params: dict,
        client_file: Optional[str] = None,
    ):
        self.scopes = scopes

        # write the scoped credentials file
        save_cred(client_params, scoped_credentials_file)

        self.scoped_credentials_file = scoped_credentials_file
        self.client_file = client_file

        self.session = self._get_authorized_session()

    def _auth(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_file, scopes=self.scopes
        )

        credentials = flow.run_local_server(
            host="localhost",
            port=8080,
            authorization_prompt_message="",
            success_message="The auth flow is complete; you may close this window.",
            open_browser=True,
        )

        return credentials

    def _get_authorized_session(self):
        cred = None

        if self.scoped_credentials_file is not None:
            try:
                cred = Credentials.from_authorized_user_file(
                    self.scoped_credentials_file,
                    self.scopes,
                )
            except OSError as err:
                logging.debug(f"Error opening auth token file - {err}")
            except ValueError:
                logging.debug("Error loading auth tokens - Incorrect format")
            except Exception as e:
                print("ERROR")
                print(e)

            if not cred:
                cred = self._auth()

                save_cred(cred, self.scoped_credentials_file)

        session = AuthorizedSession(cred)

        return session

    def _get_albums(self, appCreatedOnly=False):
        params = {"excludeNonAppCreatedData": appCreatedOnly}

        while True:
            albums = self.session.get(
                "https://photoslibrary.googleapis.com/v1/albums", params=params
            ).json()

            logging.debug(f"Server response: {albums}")

            if "albums" in albums:
                yield from albums["albums"]

                if "nextPageToken" in albums:
                    params["pageToken"] = albums["nextPageToken"]
                else:
                    return

            else:
                return

    def _get_album_id(self, album_name):
        for a in self._get_albums():
            if a["title"].lower() == album_name.lower():
                album_id = a["id"]

                return album_id

    def _get_mediaitems(self, album_id):
        params = {
            "pageSize": "100",
            "albumId": album_id,
        }

        # loop content
        while True:
            resp = self.session.post(
                "https://photoslibrary.googleapis.com/v1/mediaItems:search", params
            ).json()

            if "mediaItems" in resp:
                yield from resp["mediaItems"]

                if "nextPageToken" in resp:
                    params["pageToken"] = resp["nextPageToken"]
                else:
                    return
            else:
                return

    def clear_album(self, album_id):
        media_items = self._get_mediaitems(album_id)

        body = {"mediaItemIds": [item["id"] for item in media_items]}

        resp = self.session.post(
            f"https://photoslibrary.googleapis.com/v1/albums/{album_id}:batchRemoveMediaItems",  # noqa
            body,
        )

        return resp.status_code

    def create_album(self, album_name):
        create_album_body = json.dumps({"album": {"title": album_name}})

        resp = self.session.post(
            "https://photoslibrary.googleapis.com/v1/albums", create_album_body
        ).json()

        logging.debug(f"Server response: {resp}")

        if "id" in resp:
            logging.info(f"Created new album -- '{album_name}'")
            return resp["id"]
        else:
            return 0

    def upload_images(self, album_id: str, imgs: Union[Image.Image, List[Image.Image]]):
        if isinstance(imgs, Image.Image):
            imgs = [imgs]

        self.session.headers["Content-type"] = "application/octet-stream"
        self.session.headers["X-Goog-Upload-Protocol"] = "raw"

        for ii, im in enumerate(imgs):
            fname = f"./upload_photo_{ii}.png"

            im.save(fname)

            try:
                photo_file = open(fname, mode="rb")
                photo_bytes = photo_file.read()
            except OSError as err:
                logging.error(f"Could not read file '{fname}' -- {err}")
                continue

            self.session.headers["X-Goog-Upload-File-Name"] = os.path.basename(fname)

            logging.info(f"Uploading photo -- '{fname}'")

            upload_token = self.session.post(
                "https://photoslibrary.googleapis.com/v1/uploads", photo_bytes
            )

            if (upload_token.status_code == 200) and (upload_token.content):
                create_body = json.dumps(
                    {
                        "albumId": album_id,
                        "newMediaItems": [
                            {
                                "description": "",
                                "simpleMediaItem": {
                                    "uploadToken": upload_token.content.decode()
                                },
                            }
                        ],
                    },
                    indent=4,
                )

                resp = self.session.post(
                    "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
                    create_body,
                ).json()

                if "newMediaItemResults" in resp:
                    status = resp["newMediaItemResults"][0]["status"]
                    if status.get("code") and (status.get("code") > 0):
                        logging.error(
                            "Could not add '{}' to library -- {}".format(
                                os.path.basename(fname), status["message"]
                            )
                        )
                    else:
                        logging.info(
                            f"Added '{os.path.basename(fname)}' to library and album"
                        )
                else:
                    logging.error(
                        f"Could not add '{os.path.basename(fname)}' to library. Server Response -- {resp}"  # noqaq
                    )

            else:
                logging.error(
                    f"Could not upload '{os.path.basename(fname)}'. Server Response - {upload_token}"  # noqa
                )

        try:
            del self.session.headers["Content-type"]
            del self.session.headers["X-Goog-Upload-Protocol"]
            del self.session.headers["X-Goog-Upload-File-Name"]
        except KeyError:
            pass


if __name__ == "__main__":
    scopes = [
        "https://www.googleapis.com/auth/photoslibrary",
        "https://www.googleapis.com/auth/photoslibrary.sharing",
    ]
    scoped_credentials_file = "./auth_creds_v3.json"
    client_file = None
    imgs = [Image.open("./notebooks/demo.png")]

    client = GooglePhotosClient(
        scopes=scopes,
        client_file=client_file,
        scoped_credentials_file=scoped_credentials_file,
    )

    # album_id = client.create_album('beautiful-s2-prod')
    # album_id = client._get_album_id('beautiful-s2-prod')
    # client.clear_album('beautiful-s2-prod')
    # client.upload_images(album_id,imgs)
