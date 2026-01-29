class SearchInfo:
    def __init__(self):
        self.eval = None
        self.depth = None
        self.principle_variation = None

    def update(self, info):
        if "score" in info:    
            score_obj = info["score"].relative
            self.eval = score_obj.score()

        # 2. Depth
        if "depth" in info:
            self.depth = info['depth']
    
        # 3. Best Line (Principal Variation)
        if "pv" in info:
            self.principle_variation = info["pv"]

    