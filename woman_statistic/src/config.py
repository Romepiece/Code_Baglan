"""
ГЛОБАЛЬНАЯ КОНФИГУРАЦИЯ ПРОЕКТА
woman_statistic

Все пути и параметры проекта определены здесь.
Каждый скрипт импортирует config.py и использует эти пути.
"""

from pathlib import Path

# ============================================================================
# КОРНЕВАЯ ПАПКА ПРОЕКТА
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent  # woman_statistic/

# ============================================================================
# ВХОДНЫЕ ДАННЫЕ
# ============================================================================
DATA_PATH = PROJECT_ROOT / "data" / "women_agri_panel.xlsx"

# ============================================================================
# ВЫХОДНЫЕ ПУТИ (OUTPUT СТРУКТУРА)
# ============================================================================
OUTPUT_ROOT = PROJECT_ROOT / "output"

# --- ТАБЛИЦЫ ---
TABLES_ROOT = OUTPUT_ROOT / "tables"
TABLES_01_VALIDATE = TABLES_ROOT / "01_validate"
TABLES_02_EDA = TABLES_ROOT / "02_eda"
TABLES_03_PREPARE = TABLES_ROOT / "03_prepare"
TABLES_04_ECONOMETRICS = TABLES_ROOT / "04_econometrics"
TABLES_05_KMEANS = TABLES_ROOT / "05_kmeans"
TABLES_06_RF = TABLES_ROOT / "06_random_forest"
TABLES_99_ARTICLE = TABLES_ROOT / "99_article_pack"

# --- ГРАФИКИ ---
INFOGRAPHICS_ROOT = OUTPUT_ROOT / "infographics"
INFOGRAPHICS_01_VALIDATE = INFOGRAPHICS_ROOT / "01_validate"
INFOGRAPHICS_02_EDA = INFOGRAPHICS_ROOT / "02_eda"
INFOGRAPHICS_03_PREPARE = INFOGRAPHICS_ROOT / "03_prepare"
INFOGRAPHICS_04_ECONOMETRICS = INFOGRAPHICS_ROOT / "04_econometrics"
INFOGRAPHICS_05_KMEANS = INFOGRAPHICS_ROOT / "05_kmeans"
INFOGRAPHICS_06_RF = INFOGRAPHICS_ROOT / "06_random_forest"

# --- ТЕКСТОВЫЕ ВЫВОДЫ ---
PROMPT_ROOT = OUTPUT_ROOT / "prompt"
PROMPT_04_ECONOMETRICS = PROMPT_ROOT / "04_econometrics"
PROMPT_05_KMEANS = PROMPT_ROOT / "05_kmeans"
PROMPT_06_RF = PROMPT_ROOT / "06_random_forest"
PROMPT_99_ARTICLE = PROMPT_ROOT / "99_article_pack"

# ============================================================================
# КОНФИГУРАЦИЯ АНАЛИЗА
# ============================================================================
SEED = 42  # Random seed для воспроизводимости

# ============================================================================
# ФУНКЦИЯ ИНИЦИАЛИЗАЦИИ ПАПОК
# ============================================================================

def ensure_dirs():
    """
    Создаёт все необходимые подпапки в output/, если они не существуют.
    Должна вызваться в начале каждого скрипта.
    """
    dirs = [
        TABLES_01_VALIDATE,
        TABLES_02_EDA,
        TABLES_03_PREPARE,
        TABLES_04_ECONOMETRICS,
        TABLES_05_KMEANS,
        TABLES_06_RF,
        TABLES_99_ARTICLE,
        INFOGRAPHICS_01_VALIDATE,
        INFOGRAPHICS_02_EDA,
        INFOGRAPHICS_03_PREPARE,
        INFOGRAPHICS_04_ECONOMETRICS,
        INFOGRAPHICS_05_KMEANS,
        INFOGRAPHICS_06_RF,
        PROMPT_04_ECONOMETRICS,
        PROMPT_05_KMEANS,
        PROMPT_06_RF,
        PROMPT_99_ARTICLE,
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)

# Инициализация при импорте
ensure_dirs()
