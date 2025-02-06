from logging import Logger
from typing import Any, Callable, Generic, Literal, TypeVar, cast, final
from supaernova.utils.typing import CFG

# --- Types ---
type RequirementReturn[T] = tuple[Literal[False], str] | tuple[Literal[True], T]
IN = TypeVar("IN")
OUT = TypeVar("OUT")


@final
class Requirement(Generic[IN, OUT]):
    def __init__(
        self,
        name: str,
        description: str,
        type: type | None = None,
        choice: list[IN] | None = None,
        bounds: tuple[IN, IN] | None = None,
        transform: Callable[[IN, CFG], OUT] | None = None,
        valid_transform: Callable[[OUT, CFG], RequirementReturn[OUT]] | None = None,
    ):
        self.name = name
        self.description = description
        self.type = type
        self.choice = choice
        self.bounds = bounds
        self.transform = transform
        self.valid_transform = valid_transform

    def validate_type(self, opt: IN) -> RequirementReturn[IN]:
        if self.type is not None and not isinstance(opt, self.type):
            return (
                False,
                f"Incorrect type {type(opt)}, must be {self.type}",
            )
        return True, opt

    def validate_choice(self, opt: IN) -> RequirementReturn[IN]:
        if self.choice is not None and opt not in self.choice:
            return (
                False,
                f"Unknown choice {opt}, must be one of {self.choice}",
            )
        return True, opt

    def validate_bounds(self, opt: IN) -> RequirementReturn[IN]:
        if self.bounds is not None and not (self.bounds[0] <= opt <= self.bounds[-1]):
            return (
                False,
                f"{opt} must be within {self.bounds}",
            )
        return True, opt

    def validate_transform(self, opt: IN, cfg: CFG) -> RequirementReturn[IN | OUT]:
        if self.transform is not None:
            try:
                result = self.transform(opt, cfg)
                return True, result
            except Exception as e:
                return False, f"Error tranforming {opt}: {e}"
        return True, opt

    def validate_post_transform(
        self, opt: IN | OUT, cfg: CFG
    ) -> RequirementReturn[IN | OUT]:
        if self.transform is not None and self.valid_transform is not None:
            try:
                # opt is of type OUT if transform != None
                return self.valid_transform(cast(OUT, opt), cfg)
            except Exception as e:
                return False, f"Error validating transform {opt}: {e}"
        return True, opt

    def validate(self, opt: IN, cfg: CFG):
        ok, result = self.validate_type(opt)
        if not ok:
            return ok, result
        ok, result = self.validate_choice(opt)
        if not ok:
            return ok, result
        ok, result = self.validate_bounds(opt)
        if not ok:
            return ok, result
        ok, result = self.validate_transform(opt, cfg)
        if not ok:
            return ok, result
        # result is of type IN | OUT if transform did not fail
        ok, result = self.validate_post_transform(cast(IN | OUT, result), cfg)
        if not ok:
            return ok, result
        return (ok, result)


type REQ = Requirement[Any, Any]


class Step:
    required: list[REQ] = []
    optional: list[REQ] = []

    def __init__(self, config: CFG):
        self.config: CFG = config
        self.cfg: CFG = config["global"]
        self.log: Logger = self.cfg["log"]
        self.opts: CFG = config["data"]
        self.results: CFG = {}
        self.name: str = self.__class__.__name__
        self.log.debug(f"Running {self.name} with opts: {self.opts}")
        is_valid = self.validate()
        if not is_valid:
            raise ValueError(f"Invalid {self.name} configuration")

    def validate(self):
        for requirement in self.required:
            key = requirement.name
            opt = self.opts.get(key)
            if opt is None:
                self.log.error(
                    f"{self.name} is missing required option: {key}: {requirement.description}"
                )
                return False
            else:
                ok, result = requirement.validate(opt, self.cfg)
            if not ok:
                self.log.error(f"Invalid `{key}`=`{opt}`: {result}")
                return False
            self.opts[key] = result

        for requirement in self.optional:
            key = requirement.name
            opt = self.opts.get(key)
            if opt is not None:
                ok, result = requirement.validate(opt, self.cfg)
                if not ok:
                    self.log.error(f"Invalid `{key}`=`{opt}`: {result}")
                    return False
                self.opts[key] = result
        return True

    def run(self):
        self.log.info(f"Running {self.name}")
        self.cfg["results"][self.name] = self.results
        self.config["global"] = self.cfg
        self.config[self.name] = self.opts
        self.log.info(f"Finished running {self.name}")
        return self.config
