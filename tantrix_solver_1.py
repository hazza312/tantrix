import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from math import sqrt, cos, sin, pi
from time import time
from random import shuffle

class Tile:
    def __init__(self, id: int, colour: str, edges: str):
        self.id = id
        self.colour = colour
        self.unrotated_edges = edges
        self.rotation = 0

    def get_edge(self, edge):
        return self.unrotated_edges[(edge + 6 - self.rotation) % 6]

    def rotate_clockwise(self, rotation):
        self.rotation = (self.rotation + rotation) % 6 

    def align_edge_with_colour(self, edge, colour):
        """Give edge specified colour, forcing a rotation if already aligned"""
        for i in range(1, 6):
            if self.unrotated_edges[(edge -i -self.rotation + 6) % 6] == colour:
                self.rotate_clockwise(i)
                return

    def paired_edge(self, edge) -> int:
        """The other edge with the same colour"""
        colour = self.get_edge(edge)
        for i in range(6):
            if i != edge and self.get_edge(i) == colour:
                return i

    @staticmethod
    def opposite_edge(edge: int) -> int:
        return (edge + 3) % 6
    
    def __str__(self):
        rot_edges = "".join(self.get_edge(i) for i in range(6))
        return f"({self.id}{self.colour} {rot_edges})"

    __repr__ = __str__

    

class HexagonBoard:
    """
    The following coordinate system is used in the hexagonal grid where
        - columns in ascending x
        - even columns have even x, 

    For example (where asterisks are valid positions in the coordinate system):

    0123456
    * * * * 0
     * * *  1
    * * * * 2
     * * *  3
    """

    def __init__(self):
        self.board = {}

    def is_occupied(self, position) -> bool:
        return position in self.board

    def place(self, position, tile):
        self.board[position] = tile

    def remove(self, position):
        del self.board[position]

    @staticmethod
    def neighbour(position, edge):
        """
        With a tile location and edge, get the position of the other tile that would
        share this edge.
        """
        x, y = position

        if edge == 0:
            return (x, y-2), Tile.opposite_edge(edge)
        if edge == 1:
            return (x+1, y-1), Tile.opposite_edge(edge)
        if edge == 2:
            return (x+1, y+1), Tile.opposite_edge(edge)
        if edge == 3:
            return (x, y+2), Tile.opposite_edge(edge)
        if edge == 4:
            return (x-1, y+1), Tile.opposite_edge(edge)
        
        return (x-1, y-1), Tile.opposite_edge(edge)


    def neighbours(self, position):
        for i in range(6):
            neighbour, neighbour_edge = HexagonBoard.neighbour(position, i)
            if neighbour in self.board:
                yield i, self.board[neighbour], neighbour_edge


    def placement_is_valid(self, position, next_edge, last=False) -> bool:
        """Valid if the tile edges don't clash with any neighbours
            and the next spot is not occupied (if not the last)"""
        tile = self.board[position]            

        for i, neighbour, neighbour_edge in self.neighbours(position):
            colour = tile.get_edge(i)
            if tile.get_edge(i) != neighbour.get_edge(neighbour_edge):
                return False            
            elif i == next_edge and not last:
                return False

        return True


    def joined(self, position, edge) -> bool:
        """Joined if the opposite tile edge has the same colour"""
        this_tile = self.board[position]
        colour = this_tile.get_edge(edge)
        neighbour, neighbour_edge = HexagonBoard.neighbour(position, edge)

        if neighbour in self.board:
            return self.board[neighbour].get_edge(neighbour_edge) == colour

        return False             


    def bounds(self):
        positions = self.board.keys()
        min_x = min(x for x, _ in positions)
        max_x = max(x for x, _ in positions)
        min_y = min(y for _, y in positions)
        max_y = max(y for _, y in positions)

        return min_x, min_y, max_x, max_y
    
class RingSolver:
    START_POSITION = (0, 0)

    def __init__(self, tiles, colour):
        self.colour = colour
        self.tiles = tiles
        self.board = HexagonBoard()
        self.tiles_remaining = set(range(len(tiles)))


    def _place_tile(self, tile_id, position):
        tile = self.tiles[tile_id]
        self.tiles_remaining.remove(tile_id)
        self.board.place(position, tile)  
        return tile


    def _remove_tile(self, tile_id, position):
        self.tiles_remaining.add(tile_id)
        self.board.remove(position)


    def _solve(self, last_position, last_edge):
        if len(self.tiles_remaining) == 0:
            return self.board.joined(last_position, last_edge)

        # need to place in next position where new tile touches the previous tile edge
        position, position_edge = HexagonBoard.neighbour(last_position, last_edge)

        for tile_id in tuple(self.tiles_remaining):   
            tile = self._place_tile(tile_id, position)  
         
            for _ in range(2):                               
                tile.align_edge_with_colour(position_edge, self.colour)          
                paired_edge = tile.paired_edge(position_edge)
                if self.board.placement_is_valid(position, paired_edge, last=len(self.tiles_remaining) == 0):                 
                    if self._solve(position, paired_edge):
                        return True

            self._remove_tile(tile_id, position)

        return False


    def solve(self):
        self.tiles[0].align_edge_with_colour(0, self.colour)
        self.tiles_remaining.remove(0)
        self.board.place(self.START_POSITION, self.tiles[0])
        return self.board if self._solve(self.START_POSITION, self.tiles[0].paired_edge(0)) else None
    

class HexagonBoardVisualiser:
    HEXAGON_SIZE = 20
    IMAGE_WIDTH = 1000
    IMAGE_HEIGHT = 1000

    OUTLINE_COLOUR = (255, 255, 255)
    COLOURS = {
        "R": (255, 0, 0),
        "G": (0, 255, 0),
        "Y": (255, 255, 0),
        "B": (0, 0, 255),
    }

    def __init__(self, board: HexagonBoard): 
        self.board = board

    def visualise(self, out_path):
        min_x, min_y, max_x, max_y = self.board.bounds()
        hex_size = 60        

        with Image.new("RGB", (self.IMAGE_WIDTH, self.IMAGE_HEIGHT)) as im:
            draw = ImageDraw.Draw(im)
            for (x, y), tile in self.board.board.items(): 
                px = hex_size * (1 + x - min_x) * 3 / 2
                py = (sqrt(3) / 2) * hex_size * (1 + y - min_y)
                draw.regular_polygon((px, py, hex_size), 6, outline=self.OUTLINE_COLOUR) 
            

                for i in range(6):
                    ppx = px + 0.75*hex_size * cos(pi/6 + ((i + 4) % 6) * pi / 3) 
                    ppy = py + 0.75*hex_size * sin(pi/6 + ((i + 4) % 6) * pi / 3) 
                    colour = self.COLOURS[tile.get_edge(i)]
                    draw.regular_polygon((ppx, ppy, hex_size/10), 10, fill=colour)
                    
                    paired_edge = tile.paired_edge(i)
                    oppx = px + 0.75*hex_size * cos(pi/6 + ((paired_edge + 4) % 6) * pi / 3) 
                    oppy = py + 0.75*hex_size * sin(pi/6 + ((paired_edge + 4) % 6) * pi / 3) 
                    draw.line([ppx, ppy, oppx, oppy], width=5, fill=colour)
                fnt = ImageFont.truetype("FreeSans.ttf", size=int(hex_size / 1.5))
                draw.text((px, py), str(tile.id), anchor="mm", font=fnt, fill=self.COLOURS[tile.colour])   
                   
                
            im.save(open(out_path, "wb"))


if __name__ == '__main__':
    tiles = []
    for line in open("tiles.csv").readlines():
        id, colour, edges = line.strip().split(",")
        tiles.append(Tile(int(id), colour, edges))

    
    for i in range(3, 30):
        times = []
        subset_tiles = tiles[:i]
        start = time()
        board = RingSolver(subset_tiles, tiles[i-1].colour).solve()
        times.append(time() - start)
        assert board is not None
        HexagonBoardVisualiser(board).visualise(f"loop_{i}.png")
            

        print(i, " ".join([str(t) for t in times]))
            
            

