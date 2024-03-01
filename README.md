# tap-dialpad

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [Dialpad](https://www.dialpad.com/)
- Check schemas directory for data format

To run:
```commandline
// Build tap
pip install . 

// Use config file to 'discover' available streams
// Check __init__.py for required config keys
tap-dialpad --discover --config ./config.json > catalog.json // Use 

// Edit the catalog.json to add 'selected':true property at metadata.metadata
// level to enable sync for that stream

// Run sync for the tap to output schema, record, and state
tap-dialpad --config ./config.json --catalog ./catalog.json
```

