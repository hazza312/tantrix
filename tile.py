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

