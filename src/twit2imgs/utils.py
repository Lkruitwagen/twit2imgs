import importlib
import io
import json
import re
import functools
from datetime import datetime, timedelta  # noqa
from typing import Dict

from dotmap import DotMap
from google.cloud import storage


def _indirect_cls(path):
    mod_name, _cls_name = path.rsplit(".", 1)
    mod = importlib.import_module(mod_name)
    _cls = getattr(mod, _cls_name)
    return _cls

def rsetattr(obj, attrs, val):
    pre = attrs[0:-1]
    post = attrs[-1]
    (rgetattr(obj, pre) if pre else obj)[post]=val
    return None

def rgetattr(obj, attrs, *args):
    def _getattr(obj, attr):
        return obj.get(attr)
    return functools.reduce(_getattr, [obj] + attrs)

def recursive_keys(keys, dictionary):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            yield from recursive_keys(keys+[key],value)
        else:
            yield keys +[key]
    

def maybe_parse_environ(v):
    if isinstance(v, str):
        if 'ENVIRON' in v:
            g = re.search('\(.*\)',v)
            return os.environ.get(v[g.start()+1:v.end()-1],None)
    else:
        return v
    
def walk_dict(d, f):
    
    list_of_keys = recursive_keys([],d)
    
    for sublist in list_of_keys:
        val = rgetattr(d, sublist)
        rsetattr(d, sublist, f(val))
    
    return d


def download_blob(url: str) -> io.BytesIO:
    """Download a blob as bytes
    Args:
        url (str): the url to download
    Returns:
        io.BytesIO: the content as bytes
    """
    storage_client = storage.Client()

    bucket_id = url.split("/")[0]
    file_path = "/".join(url.split("/")[1:])

    bucket = storage_client.bucket(bucket_id)
    blob = bucket.blob(file_path)

    f = io.BytesIO(blob.download_as_bytes())
    return f


def download_blob_to_filename(url: str, local_path: str) -> int:
    """Download a blob as bytes
    Args:
        url (str): the url to download
    Returns:
        io.BytesIO: the content as bytes
    """
    storage_client = storage.Client()

    bucket_id = url.split("/")[0]
    file_path = "/".join(url.split("/")[1:])

    bucket = storage_client.bucket(bucket_id)
    blob = bucket.blob(file_path)

    blob.download_to_filename(local_path)
    return 1


def upload_blob(source_directory: str, target_directory: str):
    """Function to save file to a bucket.
    Args:
        target_directory (str): Destination file path.
        source_directory (str): Source file path
    Returns:
        None: Returns nothing.
    Examples:
        >>> target_directory = 'target/path/to/file/.pkl'
        >>> source_directory = 'source/path/to/file/.pkl'
        >>> save_file_to_bucket(target_directory)
    """

    client = storage.Client()

    bucket_id = target_directory.split("/")[0]
    file_path = "/".join(target_directory.split("/")[1:])

    bucket = client.get_bucket(bucket_id)

    # get blob
    blob = bucket.blob(file_path)

    # upload data
    blob.upload_from_filename(source_directory)

    return target_directory


def download_cloud_json(target_file: str, **kwargs) -> Dict:
    """
    Function to load the json data for the WorldFloods bucket using the filename
    corresponding to the image file name. The filename corresponds to the full
    path following the bucket name through intermediate directories to the final
    json file name.
    Args:
      bucket_name (str): the name of the Google Cloud Storage (GCP) bucket.
      filename (str): the full path following the bucket_name to the json file.
    Returns:
      The unpacked json data formatted to a dictionary.
    """
    # initialize client
    client = storage.Client(**kwargs)

    bucket_id = target_file.split("/")[0]
    file_path = "/".join(target_file.split("/")[1:])

    # get bucket
    bucket = client.get_bucket(bucket_id)
    # get blob
    blob = bucket.blob(file_path)
    # check if it exists
    # TODO: wrap this within a context
    return json.loads(blob.download_as_string(client=None))


def cloud_file_exists(full_path: str, **kwargs) -> bool:
    """
    Function to check if the file in the bucket exist utilizing Google Cloud Storage
    (GCP) blobs.
    Args:
      bucket_name (str): a string corresponding to the name of the GCP bucket.
      filename_full_path (str): a string containing the full path from bucket to file.
    Returns:
      A boolean value corresponding to the existence of the file in the bucket.
    """

    bucket_name = full_path.split("/")[0]
    remaining_path = "/".join(full_path.split("/")[1:])

    # initialize client
    client = storage.Client(**kwargs)
    # get bucket
    bucket = client.get_bucket(bucket_name)
    # get blob
    blob = bucket.blob(remaining_path)
    # check if it exists
    return blob.exists()