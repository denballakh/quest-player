from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, TypedDict
import os
import sys
from pprint import pprint

import colorama as cm
import yaml

from rangers.std.mixin import PrintableMixin

import atexit

# enable color codes:
os.system('')
# cm.init()

# reset color codes at exit
atexit.register(lambda: print(cm.Fore.RESET + cm.Back.RESET))

LocationId = str
LocationText = str
VarName = str
VarValue = int
Expression = str

if TYPE_CHECKING:

    class QPJSON(TypedDict):
        locations: dict[LocationId, LocationJSON]
        vars: dict[VarName, VarValue]
        current_location: LocationId

    class JumpJSON(TypedDict):
        next: LocationId
        text: LocationText
        condition: Expression
        var_changes: dict[VarName, Expression]

    class LocationJSON(TypedDict):
        name: LocationId
        text: LocationText
        is_start: bool
        is_end: bool
        jumps: list[JumpJSON]


class Location(PrintableMixin):
    name: LocationId
    text: LocationText
    jumps: list[Jump]
    is_end: bool
    is_start: bool

    def __init__(self, name: LocationId, data: LocationJSON) -> None:
        self.name = name
        assert isinstance(self.name, LocationId)
        self.text = data.get('text')
        assert isinstance(self.text, str)
        self.is_end = data.get('is_end', False)
        assert isinstance(self.is_end, bool)
        self.is_start = data.get('is_start', False)
        assert isinstance(self.is_start, bool)

        self.jumps = []
        for jump_data in data['jumps']:
            jump = Jump(jump_data)
            self.jumps.append(jump)

    def to_json(self) -> LocationJSON:
        return {
            'name': self.name,
            'text': self.text,
            'is_start': self.is_start,
            'is_end': self.is_end,
            'jumps': [j.to_json() for j in self.jumps],
        }


class Jump(PrintableMixin):
    next: LocationId
    text: LocationText
    condition: Expression
    var_changes: dict[VarName, Expression]

    def __init__(self, data: JumpJSON) -> None:
        self.next = data.get('next')
        assert isinstance(self.next, LocationId)
        self.text = data.get('text')
        assert isinstance(self.text, LocationText)
        self.condition = data.get('condition', 'True')
        assert isinstance(self.condition, Expression)

        self.var_changes = data.get('var_changes', {})
        for var_name, var_expr in self.var_changes.items():
            assert isinstance(var_name, VarName)
            assert isinstance(var_expr, Expression)

    def to_json(self) -> JumpJSON:
        return {
            'next': self.next,
            'text': self.text,
            'condition': self.condition,
            'var_changes': self.var_changes,
        }


class QuestPlayer(PrintableMixin):
    locations: dict[LocationId, Location]
    variables: dict[VarName, VarValue]
    current_location: Location

    def __init__(self, data: QPJSON) -> None:
        self.locations = {}
        for loc_name, loc_data in data.get('locations').items():
            assert loc_name not in self.locations
            loc = Location(loc_name, loc_data)
            self.locations[loc_name] = loc

        self.variables = data.get('vars', {})
        for var_name, var_value in self.variables.items():
            assert isinstance(var_name, VarName)
            assert isinstance(var_value, VarValue)

        current_location = None
        for _, loc in self.locations.items():
            if loc.is_start:
                assert current_location is None, 'two start locations'
                current_location = loc

        assert current_location is not None, 'no start locations'
        self.current_location = current_location

    def run(self) -> None:
        while True:
            loc = self.current_location

            print(cm.Fore.GREEN, loc.text, cm.Fore.RESET, sep='')
            print(cm.Fore.BLUE, self.variables, cm.Fore.RESET, sep='')
            print()
            jumps = []
            for jump in loc.jumps:
                jumps.append(jump)

            for i, jump in enumerate(jumps):
                if self.check_jump(jump):
                    print(f'{cm.Fore.YELLOW}{i}){cm.Fore.RESET} {jump.text}')
                else:
                    print(
                        f'{cm.Fore.RED}[disabled]{cm.Fore.RESET} {cm.Fore.YELLOW}{i}){cm.Fore.RESET} {jump.text}'
                    )
            print()

            if loc.is_end:
                print('Reached end location!')
                break

            inp = input()
            if inp.lower() in {'q', 'quit'}:
                print('Quited')
                break

            if not inp.isnumeric():
                print(f'{cm.Fore.RED}Enter valid number{cm.Fore.RESET}')
                continue

            jump_id = int(inp)
            if jump_id < 0 or jump_id >= len(jumps):
                print(f'{cm.Fore.RED}Invalid index{cm.Fore.RESET}')
                continue

            jump = jumps[jump_id]

            if not self.check_jump(jump):
                print(f'{cm.Fore.RED}Jump is disabled. Try again{cm.Fore.RESET}')
                continue

            self.execute_jump(jump)

    def execute_jump(self, jump: Jump) -> None:
        self.current_location = self.locations[jump.next]

        new_vars = self.variables.copy()

        for var_name, var_new_val in jump.var_changes.items():
            new_vars[var_name] = self.calc_expression(var_new_val)

        self.variables = new_vars

    def check_jump(self, jump: Jump) -> bool:
        return bool(self.calc_expression(jump.condition))

    def calc_expression(self, expr: Expression) -> VarValue:
        for var_name, var_value in self.variables.items():
            expr = expr.replace(f'<{var_name}>', str(var_value))

        return eval(expr)

    @classmethod
    def from_file(cls, filename: str) -> QuestPlayer:
        with open(filename, 'rt') as file:
            data = yaml.safe_load(file)

        return cls(data)

    def to_json(self) -> QPJSON:
        return {
            'locations': {name: loc.to_json() for name, loc in self.locations.items()},
            'vars': self.variables,
            'current_location': self.current_location.name,
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Quest file to run')
    args = parser.parse_args()

    qp = QuestPlayer.from_file(args.input)
    qp.run()
