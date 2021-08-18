from time import time
from random import shuffle

from tile import Tile
from board import HexagonBoard 
from visualise import HexagonBoardVisualiser

    
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
    



if __name__ == '__main__':
    tiles = []
    for line in open("tiles.csv").readlines():
        id, colour, edges = line.strip().split(",")
        tiles.append(Tile(int(id), colour, edges))

    
    for i in range(3, 20):
        subset_tiles = tiles[:i]
        start = time()
        board = RingSolver(subset_tiles, tiles[i-1].colour).solve()
        end = time()
        assert board is not None
        HexagonBoardVisualiser(board).visualise(f"loop_{i}.png")
        print(f"Solved loop {i} in {end - start} seconds")
            
            

