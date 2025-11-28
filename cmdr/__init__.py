from typing import Self, Iterable, Sequence, TypeVar, overload, override, Any
from abc import ABC, abstractmethod
import sys, argparse, inspect
from argparse import Namespace, ArgumentParser, Action
from pathlib import Path
from functools import wraps

__all__ = ['action', 'arg', 'command', 'CommandItem', 'entry', 'flag', 'group', 'subcommand', 'subparser']

T = TypeVar('T')
ArgumentParserT = TypeVar('ArgumentParserT')
ActionType = TypeVar('ActionType')
FormatterClass = TypeVar('FormatterClass')

def entry(target):
    name = inspect.currentframe().f_back.f_globals['__name__']
    if name == '__main__':
        target(sys.argv[1:])
    return target

class action:
    store='store'
    store_const='store_const'
    store_true='store_true'
    store_false='store_false'
    append='append'
    append_const='append_const'
    extend='extend'
    count='count'
    help='help'
    version='version'

class CommandItem(ABC):
    @abstractmethod
    def add_to_parser(self, parser: ArgumentParser): pass

class arg(CommandItem):
    __slots__ = ('name_or_flags', 'kwargs',)
    @overload
    def __init__(
        self,
        *name_or_flags: str,
        action: str | type[Action] = ...,
        nargs: int | str | None = None,
        const: Any = ...,
        default: Any = ...,
        type: ActionType = ...,
        choices: Iterable[T] | None = ...,
        required: bool = ...,
        help: str | None = ...,
        metavar: str | tuple[str, ...] | None = ...,
        dest: str | None = ...,
        version: str = ...,
        **kwargs,
    ):pass
    def __init__(self, *name_or_flags, **kwargs):
        self.name_or_flags = name_or_flags
        self.kwargs = kwargs
    
    @override
    def add_to_parser(self, parser: ArgumentParser) -> Action:
        return parser.add_argument(*self.name_or_flags, **self.kwargs)

@overload
def flag(
    *name_or_flags: str,
    action: str | type[Action] = action.store_true,
    nargs: int | str | None = None,
    const: Any = ...,
    default: Any = ...,
    type: ActionType = ...,
    choices: Iterable[T] | None = ...,
    required: bool = ...,
    help: str | None = ...,
    metavar: str | tuple[str, ...] | None = ...,
    dest: str | None = ...,
    version: str = ...,
    **kwargs,
)->arg:pass
def flag(
    *name_or_flags: str,
    action = 'store_true',
    **kwargs
)->arg:
    return arg(*name_or_flags, action=action, **kwargs)

class group(CommandItem):
    __slots__ = ('input_args', 'group_args', 'kwargs',)
    @overload
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        prefix_chars: str = ...,
        argument_default: Any = ...,
        conflict_handler: str = ...,
    ): pass
    def __init__(
        self,
        *args,
        **kwargs
    ):
        self.group_args = list()
        self.input_args = args
        self.kwargs = kwargs
    
    def args(self, *args: CommandItem)->Self:
        self.group_args.extend(args)
        return self
    
    @override
    def add_to_parser(self, parser: ArgumentParser):
        group = parser.add_argument_group(
            *self.input_args,
            **self.kwargs
        )
        for item in self.group_args:
            item.add_to_parser(group)
        return group

class subcommand(CommandItem):
    __slots__ = (
        'parser_args',
        'parser_subcommand',
        'kwargs',
    )
    @overload
    def __init__(
        self,
        *,
        deprecated: bool = False,
        help: str | None = ...,
        aliases: Sequence[str] = ...,
        prog: str | None = ...,
        usage: str | None = ...,
        description: str | None = ...,
        epilog: str | None = ...,
        parents: Sequence[ArgumentParser] = ...,
        formatter_class: FormatterClass = ...,
        prefix_chars: str = ...,
        fromfile_prefix_chars: str | None = ...,
        argument_default: Any = ...,
        conflict_handler: str = ...,
        add_help: bool = True,
        allow_abbrev: bool = True,
        exit_on_error: bool = True,
        **kwargs: Any,
    ): pass
    def __init__(
        self,
        **kwargs,
    ):
        self.parser_args = list()
        self.parser_subcommand = None
        self.kwargs = kwargs
    
    def args(self, *args: CommandItem) -> Self:
        self.parser_args.extend(args)
        return self
    
    def subcommand(self, command: subcommand) -> Self:
        self.parser_subcommand = command
        return self
    
    @override
    def add_to_parser(self, parser: ArgumentParser):
        for arg in self.parser_args:
            arg.add_to_parser(parser)
        if self.parser_subcommand:
            self.parser_subcommand.add_to_parser(parser)

class subparser(CommandItem):
    __slots__ = (
        'subcommands',
        'kwargs',
    )
    subcommands: dict[str, subcommand]
    @overload
    def __init__(
        self,
        *,
        title: str = "subcommands",
        description: str | None = None,
        prog: str | None = None,
        action: type[Action] = ...,
        option_string: str = ...,
        dest: str | None = None,
        required: bool = False,
        help: str | None = None,
        metavar: str | None = None,
    ): pass
    @overload
    def __init__(
        self,
        *,
        title: str = "subcommands",
        description: str | None = None,
        prog: str | None = None,
        parser_class: type[ArgumentParserT] = ...,
        action: type[Action] = ...,
        option_string: str = ...,
        dest: str | None = None,
        required: bool = False,
        help: str | None = None,
        metavar: str | None = None,
    ): pass
    def __init__(
        self,
        **kwargs,
    ):
        self.subcommands = dict()
        self.kwargs = kwargs
    
    def commands(
        self,
        **commands: subcommand,
    )->Self:
        self.subcommands.update(commands)
        return self
    
    @override
    def add_to_parser(self, parser: ArgumentParser):
        command = parser.add_subparsers(**self.kwargs)
        if not self.subcommands:
            return command
        for name, subcommand in self.subcommands.items():
            subparser: ArgumentParser = command.add_parser(name, **subcommand.kwargs)
            subcommand.add_to_parser(subparser)
        return command

class command:
    __slots__ = ('parser',)
    parser: ArgumentParser
    @overload
    def __init__(
        self,
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        epilog: str | None = None,
        parents: Sequence[ArgumentParser] = [],
        formatter_class: FormatterClass = ...,
        prefix_chars: str = "-",
        fromfile_prefix_chars: str | None = None,
        argument_default: Any = None,
        conflict_handler: str = "error",
        add_help: bool = True,
        allow_abbrev: bool = True,
        exit_on_error: bool = True,
    ): pass
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        parser = argparse.ArgumentParser(
            *args,
            **kwargs
        )
        self.parser = parser
    
    def args(self, *args: CommandItem)->Self:
        for arg in args:
            arg.add_to_parser(self.parser)
        return self
    
    def subcommand(self, subcommand: subcommand)->Self:
        subcommand.add_to_parser(self.parser)
        return self
    
    def __call__(self, target):
        @wraps(target)
        def wrapped(args: Iterable[str]):
            ns = self.parse(args)
            return target(ns)
        return wrapped
    
    @overload
    def parse(self, args: Sequence[str])->Namespace:pass
    @overload
    def parse(self, args: Sequence[str], namespace: Namespace):pass
    def parse(self, args, namespace=None):
        if namespace is not None:
            return self.parser.parse_args(args, namespace)
        else:
            return self.parser.parse_args(args)