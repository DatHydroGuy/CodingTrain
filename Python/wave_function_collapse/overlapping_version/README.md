# Wave Function Collapse

### Preset Values
In `main.py` the user can pick the tilset to use and the parameters for successful edge matching by altering the line

`tile_set = TileSet(r'tilesets\Castle', colour_tolerance=20, match_ratio=0.5, max_mismatch_run=1)`

The following presets give pretty good results in testing:

`'tilesets\Castle', colour_tolerance=20, match_ratio=0.5, max_mismatch_run=1`</br>
`'tilesets\Circuit', colour_tolerance=10, match_ratio=0.7, max_mismatch_run=1`</br>
`'tilesets\FloorPlan', colour_tolerance=1, match_ratio=0.95, max_mismatch_run=1`</br>
`'tilesets\Rooms', colour_tolerance=10, match_ratio=0.9, max_mismatch_run=1`</br>
`'tilesets\Summer', colour_tolerance=50, match_ratio=0.5, max_mismatch_run=5`</br>
`'tilesets\others', colour_tolerance=10, match_ratio=0.5, max_mismatch_run=1`

Experiment with these values, as they can give wildly different results.
