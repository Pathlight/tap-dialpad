from tap_dialpad.client import get_recordings
from datetime import datetime, timedelta
import pytz
import singer


LOGGER = singer.get_logger()

# dialpad returns date field as '2024-02-19 23:57:30', need to convert to RFC 3339 / ISO 2019-10-12T07:20:50.52Z
def format_recordings(rows):
    for row in rows:
        dt = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
        tz = pytz.timezone(row['timezone'])
        row['date'] = dt.replace(tzinfo=tz).isoformat()
    return rows

def sync_recordings(stream, config, state):
    bookmark_column = stream.replication_key # 'date' for recordings
    date_last_ran = state.get(bookmark_column)
    if not date_last_ran:
       days_ago_end = 1 # default to getting data from yesterday
    else:
        days_ago_end = (datetime.now() - datetime.fromisoformat(date_last_ran)).days
    rows = get_recordings(config, days_ago_end)
    formatted_rows = format_recordings(rows)

    for row in formatted_rows:
            singer.write_records(stream.tap_stream_id, [row])
            call_id = row['call_id']
            date = row[bookmark_column]
            singer.write_state({stream.tap_stream_id: {'date': date, 'id': call_id}})

def sync(config, state, catalog):
    """ Sync data from tap source """
    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)

        singer.write_schema(
            stream_name=stream.tap_stream_id,
            schema=stream.schema.to_dict(),
            key_properties=stream.key_properties,
        )

        if (stream.tap_stream_id == 'recordings'):
            recordings_state = state.get('recordings', {})
            sync_recordings(stream, config, recordings_state)
        else:
            LOGGER.error(f"[Sync] Non-recognized tap stream ID:{stream.tap_stream_id}")
            continue
    return




