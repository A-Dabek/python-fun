class CollisionSystem:
    actors = []
    collided_pairs = []

    @staticmethod
    def add(actor):
        CollisionSystem.actors.append(actor)

    @staticmethod
    def resolve():
        col_list = CollisionSystem.actors
        for a_i in range(len(CollisionSystem.actors)):
            if col_list[a_i].collidable is None:
                continue
            ax, ay, aw, ah = col_list[a_i].collision_rect
            for c_i in range(a_i + 1, len(CollisionSystem.actors)):
                if col_list[c_i].collidable is None:
                    continue
                cx, cy, cw, ch = col_list[c_i].collision_rect
                if ax - cx < cw and cx - ax < aw and ay - cy < cw and cy - ay < aw:
                    if (a_i, c_i) in CollisionSystem.collided_pairs:
                        continue
                    col_list[a_i].add_effects(*col_list[c_i].collision_reacts())
                    CollisionSystem.collided_pairs.append((a_i, c_i))

                elif (a_i, c_i) in CollisionSystem.collided_pairs:
                    CollisionSystem.collided_pairs.remove((a_i, c_i))

    @staticmethod
    def clear():
        CollisionSystem.actors = []
