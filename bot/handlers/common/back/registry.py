# handlers/common/back/registry.py
from aiogram.fsm.state import State, StatesGroup
from typing import Dict, Callable, Union, Type

class BackRegistry:
    def __init__(self):
        # Маршруты для конкретных состояний (высокий приоритет)
        self._exact_routes: Dict[str, Callable] = {}
        # Маршруты для групп состояний (общий приоритет)
        self._group_routes: Dict[str, Callable] = {}

    def register(self, state_or_group: Union[State, Type[StatesGroup]], handler: Callable):
        """
        Регистрирует правило возврата.
        
        :param state_or_group: Состояние (ProfileState.main) или Группа (ProfileState).
        :param handler: Функция, которую нужно вызвать (show_profile).
        """
        if isinstance(state_or_group, State):
            # Если передали конкретное состояние
            self._exact_routes[state_or_group.state] = handler
        
        elif isinstance(state_or_group, type) and issubclass(state_or_group, StatesGroup):
            # Если передали группу (класс)
            # Берем имя класса (например, "ProfileState")
            group_name = state_or_group.__name__
            self._group_routes[group_name] = handler

    def get_handler(self, current_state: str) -> Callable | None:
        """Находит функцию возврата для текущего состояния."""
        if not current_state:
            return None

        # 1. Точное совпадение (например, "ProfileState:settings")
        if current_state in self._exact_routes:
            return self._exact_routes[current_state]

        # 2. Совпадение по группе
        # Aiogram хранит состояния как "Group:state". Нам нужно имя группы.
        group_name = current_state.split(":")[0]
        if group_name in self._group_routes:
            return self._group_routes[group_name]

        return None

# Создаем один экземпляр на весь проект
back_registry = BackRegistry()