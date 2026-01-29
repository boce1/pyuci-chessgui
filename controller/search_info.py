class SearchInfo:
    def __init__(self):
        self.eval = None
        self.depth = None
        self.principle_variation = None

    def update(self, info):
        if "score" in info:
            self.eval = info["score"].relative  # Score from the perspective of the side to move
    
        # 2. Depth
        if "depth" in info:
            self.depth = info['depth']
    
        # 3. Best Line (Principal Variation)
        if "pv" in info:
            self.principle_variation = info["pv"]

    