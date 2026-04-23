# tests/test_setup.py
"""
Простой тест для проверки что pytest настроен правильно.
"""
def test_pytest_works():
    """Проверка что pytest запускается."""
    assert True


def test_basic_math():
    """Проверка базовой математики."""
    assert 1 + 1 == 2
    assert 2 * 2 == 4


async def test_async_works():
    """Проверка что асинхронные тесты работают."""
    async def async_function():
        return "success"
    
    result = await async_function()
    assert result == "success"


def test_fixtures_work(test_user_data):
    """Проверка что фикстуры работают."""
    assert test_user_data["tg_id"] == 123456789
    assert test_user_data["username"] == "test_user"
