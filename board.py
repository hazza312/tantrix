from tile import Tile

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

