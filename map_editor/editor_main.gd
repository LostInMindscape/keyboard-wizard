@tool
extends Node2D

@export var grid_size: Vector2 = Vector2(1600, 900)
@export var room_size: Vector2i = Vector2i(32, 18)

@export_tool_button("Print tile positions") var f: Callable = func():
    var layer: TileMapLayer = $TileMapLayer
    var cells := layer.get_used_cells()
    
    if cells.is_empty():
        print("There are no tiles!")
    else:
        cells.sort()
        print("Top-left tile:      ", cells[0])
        print("Bottom-right tile:  ", cells[-1])
        print("Map size:           ", cells[-1] - cells[0])


@export var file_name: String = "map.txt"
@export var add_to_each: int = 0
@export_tool_button("Export map") var f2: Callable = func():
    var layer: TileMapLayer = $TileMapLayer
    var cells := layer.get_used_cells()
    
    if cells.is_empty():
        print("Map is empty! Aborting")
        return
    
    cells.sort()
    var rooms_start: Vector2i = Vector2i(
        ceili(float(cells[0].x) / room_size.x),
        ceili(float(cells[0].y) / room_size.y)
    )
    var rooms_end: Vector2i = Vector2i(
        ceili(float(cells[-1].x) / room_size.x),
        ceili(float(cells[-1].y) / room_size.y)
    )
    var tiles_start: Vector2i = rooms_start * room_size
    var tiles_end: Vector2i = rooms_end * room_size
    var empty_tiles: int = 0
    
    var atlas_width: int = 0
    for src: int in layer.tile_set.get_source_count():
        if layer.tile_set.get_source(src) is TileSetAtlasSource:
            var atlas_src: TileSetAtlasSource = layer.tile_set.get_source(src)
            atlas_width = atlas_src.get_atlas_grid_size().x
            break
    
    if atlas_width == 0:
        printerr("Encountered problem while looking for atlas width - aborting")
        return
    
    var file: FileAccess = FileAccess.open(file_name, FileAccess.WRITE)
    
    file.store_string("[\n")
    for y: int in range(tiles_start.y, tiles_end.y):
        file.store_string("    [")
        for x: int in range(tiles_start.x, tiles_end.x):
            var atlas_coords: Vector2i = layer.get_cell_atlas_coords(Vector2i(x, y))
            var id: int = atlas_coords.y * atlas_width + atlas_coords.x + add_to_each
            
            if atlas_coords == -Vector2i.ONE:
                empty_tiles += 1
                id = 0
            
            if x != tiles_end.x - 1:
                file.store_string(str(id, ", "))
            else:
                file.store_string(str(id, "]"))
        
        if y != tiles_end.y - 1:
            file.store_string(",\n")
        else:
            file.store_string("\n")
    
    file.store_string("]")
    
    file.close()
    
    if empty_tiles != 0:
        printerr("WARNING: encountered ", empty_tiles, " empty tiles; they were replaced with 0s")


func _draw() -> void:
    for x in range(0, 20 * grid_size.x, grid_size.x):
        draw_line(
            Vector2(x, 0),
            Vector2(x, 25000),
            Color.RED
        )
    
    for y in range(0, 20 * grid_size.y, grid_size.y):
        draw_line(
            Vector2(0, y),
            Vector2(25000, y),
            Color.RED
        )


func _process(_delta: float) -> void:
    if Engine.is_editor_hint():
        queue_redraw()
