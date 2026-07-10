import os
import boto3
from dotenv import load_dotenv

load_dotenv()


def get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=f"https://{os.environ.get('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ.get('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('R2_SECRET_ACCESS_KEY'),
        region_name='auto',
    )


def get_presigned_url(key, expiry=None):
    expiry = expiry or int(os.environ.get('HLS_EXPIRY', 18000))
    client = get_r2_client()
    return client.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.environ.get('R2_BUCKET_NAME'), 'Key': key},
        ExpiresIn=expiry,
    )


def get_master_manifest(manifest_key, sub_playlist_base_url):
    """Fetch master m3u8 and rewrite variant playlist paths to Django proxy URLs."""
    client = get_r2_client()
    bucket = os.environ.get('R2_BUCKET_NAME')

    obj = client.get_object(Bucket=bucket, Key=manifest_key)
    manifest = obj['Body'].read().decode('utf-8')

    lines = []
    for line in manifest.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            lines.append(f"{sub_playlist_base_url}/{stripped}")
        else:
            lines.append(line)

    return '\n'.join(lines)


def get_sub_playlist_with_presigned_segments(playlist_key, key_url=None):
    """Fetch variant playlist and rewrite segment paths to presigned R2 URLs."""
    import re
    client = get_r2_client()
    bucket = os.environ.get('R2_BUCKET_NAME')

    obj = client.get_object(Bucket=bucket, Key=playlist_key)
    manifest = obj['Body'].read().decode('utf-8')

    base_dir = playlist_key.rsplit('/', 1)[0]

    lines = []
    for line in manifest.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            segment_key = f"{base_dir}/{stripped}"
            lines.append(get_presigned_url(segment_key))
        elif key_url and stripped.startswith('#EXT-X-KEY:'):
            lines.append(re.sub(r'URI="[^"]*"', f'URI="{key_url}"', stripped))
        else:
            lines.append(line)

    return '\n'.join(lines)
