
import pytz
from datetime import datetime
import libtaxii.messages_11 as tm11

from .entities import ContentBinding


def get_utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)


def pack_content_binding(content_binding, version):
    if isinstance(content_binding, ContentBinding):
        if version == 11:
            binding = tm11.ContentBinding(
                binding_id=content_binding.id,
                subtype_ids=content_binding.subtypes)
        else:
            binding = content_binding.id
    else:
        if version == 11:
            binding = tm11.ContentBinding(binding_id=content_binding)
        else:
            binding = content_binding
    return binding


def pack_content_bindings(content_bindings, version):

    if not content_bindings:
        return None

    bindings = []

    for b in content_bindings:
        bindings.append(pack_content_binding(b, version))

    return bindings


def if_key_encrypted(key_file):
    with open(key_file, 'r') as f:
        return 'Proc-Type: 4,ENCRYPTED' in f.read()
