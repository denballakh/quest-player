# Usage:
# python quest_player.py -i quests/q1.json
import json
from pprint import pprint

__all__ = ['QuestPlayer', ]

# TODO: {"next_loc_name":{...jump...}} -> [{"next":"next_loc_name",...jump...}]

class Location:
    id_: str
    text: str
    jumps: dict[str, 'Jump']
    terminal: bool

    def __init__(self, id_: str, data: dict):
        self.id_ = id_
        self.text = data['text']

        if 'terminal' in data:
            self.terminal = bool(data['terminal'])
        else:
            self.terminal = False

        jumps: dict[str, dict] = data['jumps']
        self.jumps = {}
        for jump_to_id, jump_data in jumps.items():
            jump = Jump(jump_to_id, jump_data)
            self.jumps[jump_to_id] = jump

    def __repr__(self) -> str:
        return f'<Location: id={self.id_!r} text={self.text!r} jumps={self.jumps!r}>'



class Jump:
    id_: str # jump to
    text: str
    condition: str
    var_changes: dict[str, str]

    def __init__(self, id_: str, data: dict):
        self.id_ = id_
        self.text = data['text']

        if 'condition' in data:
            self.condition = data['condition']
        else:
            self.condition = '1' # truth value, always passes check

        self.var_changes = {}
        if 'var_changes' in data:
            for var_name, var_expr in data['var_changes'].items():
                self.var_changes[var_name] = var_expr

    def __repr__(self) -> str:
        return f'<Jump: id={self.id_!r} condition={self.condition!r} var_changes={self.var_changes!r}>'


class QuestPlayer:
    locations: dict[str, Location]
    variables: dict[str, int]
    current_location: Location

    def __init__(self, data: dict):
        self.locations = {}
        for loc_id, loc_data in data['locations'].items():
            loc = Location(loc_id, loc_data)
            self.locations[loc_id] = loc

        self.variables = data['vars']
        self.current_location = self.locations[data['start_loc']]


    def __repr__(self) -> str:
        return f'<QuestPlayer: locations={self.locations!r} variables={self.variables!r} current_location={self.current_location!r}>'

    def check(self):
        pass

    def run(self):
        while True:
            print(self.current_location.text)
            print()
            jumps = []
            for jump in self.current_location.jumps.values():
                jumps.append(jump)

            for i, jump in enumerate(jumps):
                if self.check_jump(jump):
                    print(f'{i}) {jump.text}')
                else:
                    print(f'[disabled] {i}) {jump.text}')
            print()


            if self.current_location.terminal:
                break

            inp = input()
            if inp == 'q':
                break

            jump_id = int(inp)
            jump = jumps[jump_id]
            if not self.check_jump(jump):
                print('Jump is disabled. Try again')
            self.execute_jump(jump)

    def execute_jump(self, jump: Jump):
        self.current_location = self.locations[jump.id_]
        # TODO: execute vars changes

    def check_jump(self, jump: Jump) -> bool:
        return True
        # TODO: check conditions


    @classmethod
    def from_file(cls, filename: str) -> 'QuestPlayer':
        with open(filename, 'rt') as file:
            data = json.load(file)

        return cls(data)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Quest file to run')
    args = parser.parse_args()
    # pprint(args)

    qp = QuestPlayer.from_file(args.input)
    # pprint(qp)
    qp.run()

