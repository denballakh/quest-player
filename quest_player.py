# Usage:
# python quest_player.py -i quests/q1.yaml

from pprint import pprint
# from ast import literal_eval

import yaml

__all__ = ['QuestPlayer', ]

# TODO: replace `eval` with safe version

class Location:
    name: str
    text: str
    jumps: list['Jump']
    is_end: bool
    is_start: bool

    def __init__(self, name: str, data: dict):
        self.name = name
        self.text = data['text']
        self.is_end = bool(data['is_end']) if 'is_end' in data else False
        self.is_start = bool(data['is_start']) if 'is_start' in data else False


        self.jumps = []
        for jump_data in data['jumps']:
            jump = Jump(self.name, jump_data)
            self.jumps.append(jump)

    def __repr__(self) -> str:
        return f'<Location: name={self.name!r} text={self.text!r} jumps={self.jumps!r}>'

    def dump(self) -> object:
        return {
            'name': self.name,
            'text': self.text,
            'is_start': self.is_start,
            'is_end': self.is_end,
            'jumps': [j.dump() for j in self.jumps],
        }



class Jump:
    prev: str
    next: str # next location
    text: str
    condition: str
    var_changes: dict[str, str]

    def __init__(self, prev: str, data: dict):
        self.prev = prev
        self.next = data['next'] if 'next' in data else self.prev
        self.text = data['text']
        self.condition = data['condition'] if 'condition' in data else 'True'

        self.var_changes = {}
        if 'var_changes' in data:
            for var_name, var_expr in data['var_changes'].items():
                self.var_changes[var_name] = var_expr

    def __repr__(self) -> str:
        return f'<Jump: text={self.text!r} prev={self.prev!r} next={self.next!r} condition={self.condition!r} var_changes={self.var_changes!r}>'

    def dump(self) -> object:
        return {
            'next': self.next,
            '--prev': self.prev, # will be ignored
            'text': self.text,
            'condition': self.condition,
            'var_changes': self.var_changes,
        }

class QuestPlayer:
    locations: dict[str, Location]
    variables: dict[str, int]
    current_location: Location

    def __init__(self, data: dict):
        self.locations = {}
        for loc_name, loc_data in data['locations'].items():
            loc = Location(loc_name, loc_data)
            self.locations[loc_name] = loc

        self.variables = data['vars']
        # self.current_location = self.locations[data['start_loc']]
        for _, loc in self.locations.items():
            if loc.is_start:
                self.current_location = loc
                break

        self.check()


    def __repr__(self) -> str:
        return f'<QuestPlayer: locations={self.locations!r} variables={self.variables!r} current_location={self.current_location!r}>'

    def check(self):
        pass

    def run(self):
        while True:
            loc = self.current_location

            print(loc.text)
            pprint(self.variables)
            print()
            jumps = []
            for jump in loc.jumps:
                jumps.append(jump)

            for i, jump in enumerate(jumps):
                if self.check_jump(jump):
                    print(f'{i}) {jump.text}')
                else:
                    print(f'[disabled] {i}) {jump.text}')
            print()


            if loc.is_end:
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
        self.current_location = self.locations[jump.next]

        new_vars = {k: v for k, v in self.variables.items()}

        for var_name, var_new_val in jump.var_changes.items():
            new_vars[var_name] = self.calc_expression(var_new_val)

        self.variables = new_vars

    def check_jump(self, jump: Jump) -> bool:
        return bool(self.calc_expression(jump.condition))

    def calc_expression(self, expr: str):
        for var_name, var_value in self.variables.items():
            expr = expr.replace(f'<{var_name}>', str(var_value))

        return eval(expr)



    @classmethod
    def from_file(cls, filename: str) -> 'QuestPlayer':
        with open(filename, 'rt') as file:
            data = yaml.safe_load(file)
        # pprint(data)

        return cls(data)

    def dump(self) -> object:
        return {
            'locations': {name: loc.dump() for name, loc in self.locations.items()},
            'vars': self.variables,
            '--current_location': self.current_location.name,
        }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Quest file to run')
    args = parser.parse_args()
    # pprint(args)

    qp = QuestPlayer.from_file(args.input)
    # pprint(qp.dump())
    qp.run()

